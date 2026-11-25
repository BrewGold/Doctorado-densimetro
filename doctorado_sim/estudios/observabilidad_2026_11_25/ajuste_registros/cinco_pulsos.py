import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import least_squares
from scipy.signal import lfilter


ROOT = Path(__file__).resolve().parent
FREQUENCY = 1.89991
DECAY = 0.06447
PULSE_DURATION = 0.2
PERIOD = 20.0
PULSES = 5
IMU_HZ = 104
HOST_HZ = 100
CUTOFF = 20.0
TRIALS = 100
RHO = 1000.0
MU = 0.020


def ideal_velocity(t):
    wd = 2 * np.pi * FREQUENCY
    inertia = 8e-5 + RHO * 5e-8
    acceleration = 0.02 * 0.03 / inertia
    velocity = np.zeros_like(t)
    for pulse_start in np.arange(PULSES) * PERIOD:
        for start, sign in ((pulse_start, 1), (pulse_start + PULSE_DURATION, -1)):
            lag = t - start
            active = lag >= 0
            velocity[active] += (
                sign * acceleration / wd * np.exp(-DECAY * lag[active])
                * np.sin(wd * lag[active])
            )
    return velocity


def fit_ringdown(host_time, gyro, count):
    # Each pulse has its own phase, amplitude and offset; f and decay are shared.
    tau = []
    signals = []
    for i in range(count):
        relative = host_time - (i * PERIOD + PULSE_DURATION)
        mask = (relative >= 0.3) & (relative < 15.0)
        tau.append(relative[mask])
        signals.append(gyro[mask])

    def residual(parameters):
        frequency, decay = parameters
        parts = []
        for times, signal in zip(tau, signals):
            envelope = np.exp(-decay * times)
            phase = 2 * np.pi * frequency * times
            design = np.column_stack((
                envelope * np.cos(phase),
                envelope * np.sin(phase),
                np.ones_like(times),
            ))
            coefficients, _, _, _ = np.linalg.lstsq(design, signal, rcond=None)
            parts.append(design @ coefficients - signal)
        return np.concatenate(parts)

    result = least_squares(
        residual, x0=[1.89, 0.07], bounds=([1.5, 0.001], [2.3, 0.3]),
        xtol=1e-10, ftol=1e-10, gtol=1e-10,
    )
    if not result.success:
        raise RuntimeError(f"No convergió el ajuste: {result.message}")
    return result.x


def main():
    sensor_time = np.arange(PULSES * int(PERIOD * IMU_HZ) + 1) / IMU_HZ
    host_time = np.arange(PULSES * int(PERIOD * HOST_HZ) + 1) / HOST_HZ
    # Zero-order hold: use the latest sensor output at each host read.
    held_indexes = np.floor(host_time * IMU_HZ + 1e-9).astype(int)
    truth = ideal_velocity(sensor_time)
    lowpass_alpha = 1 - np.exp(-2 * np.pi * CUTOFF / IMU_HZ)
    quantum = np.deg2rad(0.00875)
    gyro_limit = np.deg2rad(250)
    noise_sigma = np.deg2rad(0.0038 * np.sqrt(52))
    bias_sigma = np.deg2rad(0.05)

    # Noiseless check verifies the free-response model and sensor timing.
    noiseless = lfilter([lowpass_alpha], [1, -(1 - lowpass_alpha)], truth)
    fitted_frequency, fitted_decay = fit_ringdown(host_time, noiseless[held_indexes], 5)
    if abs(fitted_frequency - FREQUENCY) > 2e-4 or abs(fitted_decay - DECAY) > 2e-4:
        raise RuntimeError("El ajuste no recupera el modo libre sin ruido")

    rng = np.random.default_rng(20261125)
    results = []
    first_gyro = None
    for trial in range(TRIALS):
        bias = rng.normal(0, bias_sigma)
        raw = truth + bias + rng.normal(0, noise_sigma, size=truth.size)
        clips = int(np.count_nonzero(np.abs(raw) >= gyro_limit))
        if clips:
            raise RuntimeError(f"Saturación del giroscopio: {clips} muestras")
        filtered = lfilter([lowpass_alpha], [1, -(1 - lowpass_alpha)], raw)
        sampled = np.round(filtered / quantum) * quantum
        gyro = sampled[held_indexes]
        if trial == 0:
            first_gyro = gyro.copy()
        for count in (1, 5):
            frequency, decay = fit_ringdown(host_time, gyro, count)
            # Illustrative inversion, assuming fixed rho and an exactly calibrated
            # damping law c proportional to sqrt(mu).
            mu_estimate = MU * (decay / DECAY) ** 2
            results.append({
                "trial": trial,
                "pulses_used": count,
                "frequency_hz": frequency,
                "decay_per_s": decay,
                "mu_estimate_pa_s": mu_estimate,
            })

    with (ROOT / "cinco_pulsos_resultados.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    summary = {}
    for count in (1, 5):
        rows = [r for r in results if r["pulses_used"] == count]
        frequency = np.array([r["frequency_hz"] for r in rows])
        decay = np.array([r["decay_per_s"] for r in rows])
        mu = np.array([r["mu_estimate_pa_s"] for r in rows])
        relative_error = 100 * (mu / MU - 1)
        summary[str(count)] = {
            "frequency_mean_hz": float(frequency.mean()),
            "frequency_sd_hz": float(frequency.std(ddof=1)),
            "decay_mean_per_s": float(decay.mean()),
            "decay_sd_per_s": float(decay.std(ddof=1)),
            "mu_mean_pa_s": float(mu.mean()),
            "mu_sd_pa_s": float(mu.std(ddof=1)),
            "mu_mape_percent": float(np.mean(np.abs(relative_error))),
            "mu_absolute_error_p95_percent": float(
                np.percentile(np.abs(relative_error), 95)
            ),
        }

    result = {
        "parameters": {
            "f_d_hz": FREQUENCY,
            "decay_per_s": DECAY,
            "rho_kg_m3_assumed": RHO,
            "mu_pa_s_assumed": MU,
            "pulses": PULSES,
            "pulse_width_s": PULSE_DURATION,
            "pulse_interval_s": PERIOD,
            "total_duration_s": PULSES * PERIOD,
            "free_fit_window_s_after_each_pulse": [0.3, 15.0],
            "gyro_filter_cutoff_hz_assumed": CUTOFF,
            "sensor_hz": IMU_HZ,
            "host_hz": HOST_HZ,
            "noise_trials": TRIALS,
            "gyro_bias_sd_deg_s": 0.05,
            "noise_density_deg_s_sqrt_hz": 0.0038,
            "gyro_adc_step_deg_s": 0.00875,
            "actuator_input": 0.03,
            "actuator_gain_assumed": 0.02,
            "inertia_assumed": 8e-5 + RHO * 5e-8,
        },
        "summary": summary,
        "limitations": [
            "The 1.9 Hz mode comes from filtered accelerometer data, not a validated actuator-to-gyro transfer function.",
            "The viscosity inversion is hypothetical and assumes density and damping-viscosity calibration are exactly known.",
            "The 20 Hz single-pole filter, actuator torque and constant bias are assumptions; no drift or model mismatch is included.",
            "100 noise trials repeat the same fluid and same five-pulse protocol; they are not 100 independent fluids or physical experiments.",
            "Output is noise-filtered before quantization; digital sensor architecture is simplified.",
        ],
    }
    (ROOT / "cinco_pulsos_resultados.json").write_text(json.dumps(result, indent=2))

    fig, axes = plt.subplots(2, 1, figsize=(11, 6), constrained_layout=True)
    axes[0].plot(host_time, np.rad2deg(first_gyro), linewidth=0.8)
    for start in np.arange(PULSES) * PERIOD:
        axes[0].axvspan(start, start + PULSE_DURATION, color="tab:red", alpha=0.5)
    axes[0].set(xlabel="Tiempo (s)", ylabel="Giroscopio (°/s)",
                title="Cinco pulsos y respuesta libre simulada")
    axes[0].grid(alpha=0.25)
    for count in (1, 5):
        values = [100 * (r["mu_estimate_pa_s"] / MU - 1)
                  for r in results if r["pulses_used"] == count]
        axes[1].hist(values, bins=20, alpha=0.55, label=f"{count} pulso(s)")
    axes[1].set(xlabel="Error relativo de viscosidad hipotética (%)",
                ylabel="Repeticiones de ruido")
    axes[1].legend()
    axes[1].grid(alpha=0.25)
    fig.savefig(ROOT / "cinco_pulsos.png", dpi=180)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
