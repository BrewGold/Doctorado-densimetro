import csv
import ctypes
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import least_squares


ROOT = Path(__file__).resolve().parent
HOST_COUNT = 1501
SENSOR_COUNT = 1561
PAIR_COUNT = 40
REPETITIONS = 3
AMPLITUDE = 0.003
LEVELS = [0.0, 0.1, 0.5]
METHODS = ["pulso", "frecuencia_fija", "retroalimentacion"]
PTR = np.ctypeslib.ndpointer(dtype=np.float64, ndim=1, flags="C_CONTIGUOUS")
lib = ctypes.CDLL(str(ROOT / "retroalimentacion.so"))
lib.simulate_closed_loop.argtypes = [
    ctypes.c_double, ctypes.c_double, ctypes.c_int, PTR, PTR, PTR,
    PTR, PTR, PTR, PTR, ctypes.POINTER(ctypes.c_int),
]
lib.simulate_closed_loop.restype = ctypes.c_int
lib.predict_closed_loop.argtypes = [ctypes.c_double, ctypes.c_double, PTR, PTR]
lib.predict_closed_loop.restype = ctypes.c_int


def simulate(rho, mu, mode, noise, bias, disturbance):
    arrays = [np.empty(HOST_COUNT) for _ in range(4)]
    clips = ctypes.c_int()
    status = lib.simulate_closed_loop(
        rho, mu, mode, noise, bias, disturbance, *arrays, ctypes.byref(clips),
    )
    if status:
        raise RuntimeError(f"Falló la simulación: {status}")
    return *arrays, clips.value


def predict(rho, mu, command):
    angle = np.empty(HOST_COUNT)
    status = lib.predict_closed_loop(rho, mu, command, angle)
    if status:
        raise RuntimeError(f"Falló el modelo directo: {status}")
    return angle


def estimate(signal, command):
    def residual(parameters):
        prediction = predict(parameters[0], np.exp(parameters[1]), command)
        error = prediction - signal
        return error - error.mean()

    fit = least_squares(
        residual, [1007, np.log(0.02)],
        bounds=([970, np.log(0.001)], [1050, np.log(0.1)]),
        x_scale=[10, 1], diff_step=1e-5,
        ftol=1e-9, xtol=1e-9, gtol=1e-9,
    )
    if not fit.success:
        raise RuntimeError(f"No convergió la estimación: {fit.message}")
    return float(fit.x[0]), float(np.exp(fit.x[1]))


def disturbances(rng):
    disturbance = np.zeros(HOST_COUNT)
    starts = rng.integers(100, 1380, size=6)
    signs = rng.choice([-1.0, 1.0], size=6)
    for start, sign in zip(starts, signs):
        disturbance[start:start + 12] += sign * AMPLITUDE
    return disturbance


def main():
    # Verify an ideal fit with a fixed, known input, independent of the simulator.
    command = np.zeros(HOST_COUNT)
    command[:20] = AMPLITUDE
    noiseless = predict(1007, 0.015, command)
    rho_check, mu_check = estimate(noiseless, command)
    if abs(rho_check - 1007) > 0.05 or abs(mu_check / 0.015 - 1) > 0.002:
        raise RuntimeError("El ajuste no recupera los parámetros sin ruido")

    rng = np.random.default_rng(20261125)
    rhos = rng.uniform(997.3, 1017.1, PAIR_COUNT)
    mus = np.exp(rng.uniform(np.log(0.005), np.log(0.05), PAIR_COUNT))
    values = np.empty((len(LEVELS), len(METHODS), PAIR_COUNT, REPETITIONS, 7))
    rows = []
    example = {}
    gyro_sigma = np.deg2rad(0.0038 * np.sqrt(52))
    acc_sigma = 70e-6 * 9.80665 * np.sqrt(52)
    for i, (rho, mu) in enumerate(zip(rhos, mus)):
        for rep in range(REPETITIONS):
            noise = np.ascontiguousarray(np.concatenate((
                rng.normal(0, acc_sigma, SENSOR_COUNT),
                rng.normal(0, acc_sigma, SENSOR_COUNT),
                rng.normal(0, gyro_sigma, SENSOR_COUNT),
            )))
            bias = np.ascontiguousarray(np.array([
                rng.normal(0, 0.005 * 9.80665),
                rng.normal(0, 0.005 * 9.80665),
                rng.normal(0, np.deg2rad(0.05)),
            ]))
            kicks = disturbances(rng)
            for level_index, level in enumerate(LEVELS):
                disturbance = np.ascontiguousarray(level * kicks)
                for mode, name in enumerate(METHODS):
                    angle, gyro, command, frequency, clips = simulate(
                        rho, mu, mode, noise, bias, disturbance,
                    )
                    rho_hat, mu_hat = estimate(angle, command)
                    boundary = int(
                        rho_hat < 970.001 or rho_hat > 1049.999
                        or mu_hat < 0.0010001 or mu_hat > 0.09999
                    )
                    last_frequency = float(np.mean(frequency[-300:])) if mode else 0
                    energy = float(np.sum(command[:-1] ** 2) / 100)
                    values[level_index, mode, i, rep] = [
                        rho_hat, mu_hat, clips, boundary,
                        last_frequency, energy, np.max(np.abs(gyro)),
                    ]
                    rows.append([
                        i, rep, level, name, rho, mu, rho_hat, mu_hat,
                        clips, boundary, last_frequency, energy, np.max(np.abs(gyro)),
                    ])
                    if i == 0 and rep == 0 and level == 0.5:
                        example[name] = (gyro.copy(), command.copy(), frequency.copy())
        if (i + 1) % 10 == 0:
            print(f"{i + 1}/{PAIR_COUNT} pares evaluados", flush=True)

    indexes = rng.integers(0, PAIR_COUNT, size=(5000, PAIR_COUNT))
    summaries = []
    for level_index, level in enumerate(LEVELS):
        for mode, name in enumerate(METHODS):
            data = values[level_index, mode]
            rho_error = data[:, :, 0] - rhos[:, None]
            mu_error = 100 * (data[:, :, 1] / mus[:, None] - 1)
            rho_pair_mae = np.abs(rho_error).mean(axis=1)
            mu_pair_mape = np.abs(mu_error).mean(axis=1)
            summaries.append({
                "rebound_peak_fraction": level,
                "method": name,
                "rho_mae_kg_m3": float(rho_pair_mae.mean()),
                "rho_mae_ci95": np.percentile(
                    rho_pair_mae[indexes].mean(axis=1), [2.5, 97.5],
                ).tolist(),
                "mu_mape_percent": float(mu_pair_mape.mean()),
                "mu_mape_ci95": np.percentile(
                    mu_pair_mape[indexes].mean(axis=1), [2.5, 97.5],
                ).tolist(),
                "mu_p95_absolute_error_percent": float(np.percentile(np.abs(mu_error), 95)),
                "sensor_clipping_events": int(data[:, :, 2].sum()),
                "estimates_at_bounds": int(data[:, :, 3].sum()),
                "mean_last_frequency_hz": float(data[:, :, 4].mean()) if mode else None,
                "mean_command_squared_integral": float(data[:, :, 5].mean()),
                "max_gyro_deg_per_s": float(np.rad2deg(data[:, :, 6].max())),
            })

    result = {
        "design": {
            "parameter_pairs": PAIR_COUNT,
            "noise_repetitions_per_pair": REPETITIONS,
            "temperature": "constant",
            "rho_range_kg_m3": [997.3, 1017.1],
            "mu_range_pa_s": [0.005, 0.05],
            "duration_s": 15,
            "actuator_peak_input": AMPLITUDE,
            "pulse_width_s": 0.2,
            "fixed_frequency_hz": 1.9,
            "adaptive_initial_frequency_hz": 1.7,
            "adaptive_frequency_limits_hz": [1.4, 2.4],
            "feedback": (
                "Gyroscope quadrature phase tracking, 0.8 s smoothing; "
                "frequency updated at 100 Hz with phase gain 0.015 Hz/s per radian."
            ),
            "disturbance": (
                "Six random signed 0.12 s torque-equivalent impulses between 1 "
                "and 13.8 s, with peak 0%, 10% or 50% of peak actuator input. "
                "Same disturbances and sensor-noise draws across methods."
            ),
            "fitting": (
                "Fit density and viscosity jointly to the accelerometer angle "
                "using the recorded actuator command; profile a constant angle offset. "
                "The estimator does not model or observe the disturbance."
            ),
            "limitations": [
                "Rebounds are hypothetical external torque impulses, not a measured liquid-noise model.",
                "The same synthetic dynamics generate and fit the signal, except for unmodeled disturbances and sensor bias.",
                "All methods have the same maximum actuator amplitude and duration, but continuous drive uses more integrated command energy.",
                "The controller uses gyro feedback but the inverse estimate uses angle only; closed-loop input correlates with sensor noise.",
                "Temperature drift, real translational acceleration and actual actuator and IMU response are not modeled.",
                "Confidence intervals resample parameter pairs only; they do not include structural uncertainty.",
            ],
        },
        "results": summaries,
    }
    (ROOT / "rebotes_control_resultados.json").write_text(json.dumps(result, indent=2))
    with (ROOT / "rebotes_control_predicciones.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow([
            "id", "rep", "rebote_fraccion", "metodo", "rho_real", "mu_real",
            "rho_estimada", "mu_estimada", "saturaciones", "limite_ajuste",
            "frecuencia_final_hz", "integral_comando_cuadrado", "max_gyro_rad_s",
        ])
        writer.writerows(rows)

    fig, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
    time = np.arange(HOST_COUNT) / 100
    for name in METHODS:
        gyro, command, frequency = example[name]
        axes[0, 0].plot(time, np.rad2deg(gyro), linewidth=0.7, label=name)
        if name != "pulso":
            axes[0, 1].plot(time, frequency, label=name)
    axes[0, 0].set(title="Ejemplo con rebotes del 50 %", xlabel="Tiempo (s)",
                   ylabel="Giroscopio (°/s)")
    axes[0, 1].set(title="Frecuencia de actuación", xlabel="Tiempo (s)", ylabel="Hz")
    axes[0, 0].legend()
    axes[0, 1].legend()
    for mode, name in enumerate(METHODS):
        method_rows = [r for r in summaries if r["method"] == name]
        axes[1, 0].plot(
            np.array(LEVELS) * 100, [r["rho_mae_kg_m3"] for r in method_rows],
            marker="o", label=name,
        )
        axes[1, 1].plot(
            np.array(LEVELS) * 100, [r["mu_mape_percent"] for r in method_rows],
            marker="o", label=name,
        )
    axes[1, 0].set(xlabel="Pico de rebote / pico del actuador (%)",
                   ylabel="MAE densidad (kg/m³)")
    axes[1, 1].set(xlabel="Pico de rebote / pico del actuador (%)",
                   ylabel="MAPE viscosidad (%)")
    for ax in axes.flat:
        ax.grid(alpha=0.25)
    axes[1, 1].legend()
    fig.savefig(ROOT / "rebotes_control.png", dpi=180)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
