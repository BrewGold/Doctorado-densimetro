import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import least_squares, minimize_scalar
from scipy.signal import lfilter


ROOT = Path(__file__).resolve().parent
G = 9.80665
RHO0 = 1000.0
MU0 = 0.02
EQ_REFERENCE = -0.9746388227722308
EQ_SLOPE = 0.0021440041612968324
EQ_WIDTH = 0.45
OMEGA_D0 = 2 * np.pi * 1.89991
DECAY0 = 0.06447
I0 = 8e-5 + RHO0 * 5e-8
STIFFNESS0 = I0 * (OMEGA_D0**2 + DECAY0**2)
DAMPING0 = 2 * I0 * DECAY0
PULSE_WIDTH = 0.2
SENSOR_HZ = 104
HOST_HZ = 100
DURATION = 15
FILTER_HZ = 20
N_TRAIN = 80
N_TEST = 100
REPS = 3

sensor_time = np.arange(DURATION * SENSOR_HZ + 1) / SENSOR_HZ
host_time = np.arange(DURATION * HOST_HZ + 1) / HOST_HZ
host_indexes = np.floor(host_time * SENSOR_HZ + 1e-9).astype(int)
free_mask = host_time >= PULSE_WIDTH + 0.3
free_time = host_time[free_mask] - (PULSE_WIDTH + 0.3)
lowpass_alpha = 1 - np.exp(-2 * np.pi * FILTER_HZ / SENSOR_HZ)


def equilibrium(rho):
    return EQ_REFERENCE - EQ_WIDTH * np.arctan(
        EQ_SLOPE * (rho - RHO0) / EQ_WIDTH
    )


def inverse_equilibrium(theta):
    angle = (EQ_REFERENCE - theta) / EQ_WIDTH
    if not abs(angle) < np.pi / 2:
        raise ValueError(f"Ángulo fuera del dominio de calibración: {theta}")
    return RHO0 + EQ_WIDTH / EQ_SLOPE * np.tan(angle)


def physical_angle(rho, mu, stiffness_factor=1, damping_factor=1):
    inertia = 8e-5 + rho * 5e-8
    stiffness = STIFFNESS0 * rho / RHO0 * stiffness_factor
    damping = damping_factor * DAMPING0 * np.sqrt(mu / MU0)
    decay = damping / (2 * inertia)
    wd_squared = stiffness / inertia - decay**2
    if wd_squared <= 0:
        raise ValueError("El modelo dejó de ser subamortiguado")
    wd = np.sqrt(wd_squared)
    acceleration = 0.02 * 0.03 / inertia
    result = np.zeros_like(sensor_time)
    for start, sign in ((0.0, 1), (PULSE_WIDTH, -1)):
        lag = sensor_time - start
        mask = lag >= 0
        t = lag[mask]
        result[mask] += sign * acceleration * inertia / stiffness * (
            1 - np.exp(-decay * t) *
            (np.cos(wd * t) + decay / wd * np.sin(wd * t))
        )
    return equilibrium(rho) + result


def filter_axis(values):
    return lfilter(
        [lowpass_alpha], [1, -(1 - lowpass_alpha)], values,
        zi=[(1 - lowpass_alpha) * values[0]],
    )[0]


def predicted_angle(rho, mu):
    angle = physical_angle(rho, mu)
    ax = filter_axis(G * np.sin(angle))
    az = filter_axis(G * np.cos(angle))
    return np.arctan2(ax, az)[host_indexes]


def simulated_angle(rho, mu, rng, stiffness_factor=1, damping_factor=1):
    angle = physical_angle(rho, mu, stiffness_factor, damping_factor)
    sigma = 70e-6 * G * np.sqrt(52)
    bias_x, bias_z = rng.normal(0, 0.005 * G, size=2)
    ax = G * np.sin(angle) + bias_x + rng.normal(0, sigma, size=angle.size)
    az = G * np.cos(angle) + bias_z + rng.normal(0, sigma, size=angle.size)
    if np.max(np.abs(ax)) >= 2 * G or np.max(np.abs(az)) >= 2 * G:
        raise RuntimeError("Saturación del acelerómetro")
    quantum = 0.000061 * G
    ax = np.round(filter_axis(ax) / quantum) * quantum
    az = np.round(filter_axis(az) / quantum) * quantum
    return np.arctan2(ax, az)[host_indexes]


def linear_fit(signal, basis):
    coefficients, _, _, _ = np.linalg.lstsq(basis, signal, rcond=None)
    return coefficients, basis @ coefficients - signal


def first_order_density(signal):
    y = signal[free_mask]

    def evaluate(log_tau):
        basis = np.column_stack((np.ones_like(free_time),
                                 np.exp(-free_time / np.exp(log_tau))))
        coef, residual = linear_fit(y, basis)
        return coef, residual

    result = minimize_scalar(
        lambda value: np.dot(evaluate(value)[1], evaluate(value)[1]),
        bounds=(np.log(0.05), np.log(30)), method="bounded",
    )
    if not result.success:
        raise RuntimeError("Falló el ajuste de primer orden")
    return inverse_equilibrium(evaluate(result.x)[0][0])


def second_order_fit(signal):
    y = signal[free_mask]

    def evaluate(params):
        frequency, decay = params
        envelope = np.exp(-decay * free_time)
        phase = 2 * np.pi * frequency * free_time
        basis = np.column_stack((
            np.ones_like(free_time), envelope * np.cos(phase),
            envelope * np.sin(phase),
        ))
        return linear_fit(y, basis)

    fit = least_squares(
        lambda x: evaluate(x)[1], x0=[1.9, DECAY0],
        bounds=([1.7, 0.01], [2.1, 0.2]),
        ftol=1e-9, xtol=1e-9, gtol=1e-9,
    )
    if not fit.success:
        raise RuntimeError("Falló el ajuste de segundo orden")
    return inverse_equilibrium(evaluate(fit.x)[0][0]), *fit.x


def second_order_density(signal):
    return second_order_fit(signal)[0]


def transition_fit(signal):
    # An unknown constant angle bias is profiled out, so density here is
    # identified from transient shape rather than absolute equilibrium.
    def residual(parameters):
        rho, log_mu = parameters
        error = predicted_angle(rho, np.exp(log_mu)) - signal
        return error - error.mean()

    fit = least_squares(
        residual, x0=[1007, np.log(MU0)],
        bounds=([970, np.log(0.001)], [1050, np.log(0.1)]),
        x_scale=[10, 1], ftol=1e-9, xtol=1e-9, gtol=1e-9,
    )
    if not fit.success:
        raise RuntimeError("Falló el ajuste del modelo de transición")
    return float(fit.x[0]), float(np.exp(fit.x[1]))


def transition_density(signal):
    return transition_fit(signal)[0]


def estimate(signal):
    return np.array([
        first_order_density(signal),
        second_order_density(signal),
        transition_density(signal),
    ])


def run_set(rng, n, label):
    rho = rng.uniform(997.3, 1017.1, n)
    mu = np.exp(rng.uniform(np.log(0.005), np.log(0.05), n))
    predictions = np.empty((n, REPS, 3))
    for i in range(n):
        for rep in range(REPS):
            predictions[i, rep] = estimate(simulated_angle(rho[i], mu[i], rng))
        if (i + 1) % 20 == 0:
            print(f"{label}: {i + 1}/{n} pares", flush=True)
    return rho, mu, predictions


def main():
    # The forward transition model must recover a noiseless case.
    sample = predicted_angle(1007, 0.015)
    if abs(transition_density(sample) - 1007) > 0.05:
        raise RuntimeError("El ajuste físico no recupera la densidad sin ruido")
    if abs(second_order_density(sample) - 1007) > 0.05:
        raise RuntimeError("El ajuste de segundo orden no recupera el equilibrio")

    rng = np.random.default_rng(20261125)
    train_rho, _, train = run_set(rng, N_TRAIN, "calibración")
    test_rho, test_mu, test = run_set(rng, N_TEST, "evaluación")
    train_error = train - train_rho[:, None, None]
    train_bias = train_error.mean(axis=(0, 1))
    centered = (train_error - train_bias).reshape(-1, 3)
    covariance = np.cov(centered, rowvar=False)
    precision_times_one = np.linalg.solve(covariance, np.ones(3))
    weights = precision_times_one / precision_times_one.sum()
    combined = (test - train_bias) @ weights
    estimates = np.concatenate((test, combined[:, :, None]), axis=2)
    names = ["primer_orden", "segundo_orden", "transicion", "combinado"]
    indexes = rng.integers(0, N_TEST, size=(5000, N_TEST))
    summary = {}
    for i, name in enumerate(names):
        error = estimates[:, :, i] - test_rho[:, None]
        pair_mae = np.abs(error).mean(axis=1)
        bootstrap = pair_mae[indexes].mean(axis=1)
        summary[name] = {
            "mae_kg_m3": float(pair_mae.mean()),
            "mae_ci95_kg_m3": np.percentile(bootstrap, [2.5, 97.5]).tolist(),
            "rmse_kg_m3": float(np.sqrt(np.mean(error**2))),
            "bias_kg_m3": float(error.mean()),
            "error_sd_kg_m3": float(error.std(ddof=1)),
            "p95_absolute_error_kg_m3": float(np.percentile(np.abs(error), 95)),
        }

    # Test sensitivity to a small unmodeled change in stiffness.
    mismatch = np.empty_like(test)
    for i in range(N_TEST):
        for rep in range(REPS):
            mismatch[i, rep] = estimate(
                simulated_angle(test_rho[i], test_mu[i], rng, 1.005)
            )
        if (i + 1) % 20 == 0:
            print(f"rigidez +0,5 %: {i + 1}/{N_TEST} pares", flush=True)
    mismatch_combined = (mismatch - train_bias) @ weights
    mismatch_estimates = np.concatenate(
        (mismatch, mismatch_combined[:, :, None]), axis=2,
    )
    mismatch_summary = {}
    for i, name in enumerate(names):
        error = mismatch_estimates[:, :, i] - test_rho[:, None]
        pair_mae = np.abs(error).mean(axis=1)
        mismatch_summary[name] = {
            "mae_kg_m3": float(pair_mae.mean()),
            "mae_ci95_kg_m3": np.percentile(
                pair_mae[indexes].mean(axis=1), [2.5, 97.5],
            ).tolist(),
            "bias_kg_m3": float(error.mean()),
        }

    result = {
        "parameters": {
            "rho_range_kg_m3": [997.3, 1017.1],
            "mu_range_pa_s": [0.005, 0.05],
            "mode_at_rho1000_mu002_hz": 1.89991,
            "decay_at_rho1000_mu002_per_s": DECAY0,
            "pulse_width_s": PULSE_WIDTH,
            "observation_s": DURATION,
            "filter_cutoff_hz_assumed": FILTER_HZ,
            "acceleration_bias_sd_g": 0.005,
            "train_distinct_pairs": N_TRAIN,
            "test_distinct_pairs": N_TEST,
            "noise_repetitions_per_pair": REPS,
        },
        "combination": {
            "method": "bias-corrected covariance weighting learned on independent training pairs",
            "weights_order_first_second_transition": weights.tolist(),
            "training_bias_kg_m3": train_bias.tolist(),
            "note": "The three estimates share measurements; they are not independent.",
        },
        "summary": summary,
        "stiffness_mismatch": {
            "true_stiffness_factor": 1.005,
            "assumed_stiffness_factor": 1,
            "summary": mismatch_summary,
        },
        "limitations": [
            "The equilibrium-density relation is hypothetical, extrapolated only over the small reference interval.",
            "The assumed dynamic dependencies k proportional to rho, c proportional to sqrt(mu), and effective inertia are not experimentally calibrated.",
            "The transition method profiles a constant angular bias; no time-varying drift or translational acceleration is modeled.",
            "The sensor is a simulated accelerometer with assumed single-pole filter, not the verified hardware response.",
            "Training and test cases use the same physical generator: this is an optimistic matched-model synthetic experiment.",
            "Only the transition method uses the known pulse waveform; the other two estimate equilibrium from free response.",
            "CI bootstrap resamples parameter pairs, not model uncertainty or experimental calibration.",
        ],
    }
    (ROOT / "densidad_un_pulso_resultados.json").write_text(json.dumps(result, indent=2))
    with (ROOT / "densidad_un_pulso_predicciones.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["id", "rep", "rho_real", "mu_real", *names])
        for i in range(N_TEST):
            for rep in range(REPS):
                writer.writerow([i, rep, test_rho[i], test_mu[i], *estimates[i, rep]])

    fig, ax = plt.subplots(figsize=(10, 5), constrained_layout=True)
    for offset, metrics, label, color in (
        (-0.19, summary, "Modelo coincidente", "#4c78a8"),
        (0.19, mismatch_summary, "Rigidez real +0,5 %", "#f58518"),
    ):
        values = [metrics[name]["mae_kg_m3"] for name in names]
        intervals = [metrics[name]["mae_ci95_kg_m3"] for name in names]
        errors = np.array([[v - ci[0], ci[1] - v]
                           for v, ci in zip(values, intervals)]).T
        x = np.arange(4) + offset
        ax.bar(x, values, width=0.38, color=color, label=label)
        ax.errorbar(x, values, yerr=errors, fmt="none", ecolor="black", capsize=3)
    ax.set_xticks(range(4), ["1.er orden", "2.º orden", "Transición", "Combinados"])
    ax.set_ylabel("MAE de densidad (kg/m³)")
    ax.set_title("Un pulso: comparación sintética; IC 95 % por par")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    fig.savefig(ROOT / "densidad_un_pulso.png", dpi=180)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
