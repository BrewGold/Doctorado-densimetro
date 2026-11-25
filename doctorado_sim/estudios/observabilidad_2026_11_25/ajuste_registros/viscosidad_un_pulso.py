import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks

from densidad_un_pulso import (
    DAMPING0, MU0, N_TEST, N_TRAIN, REPS, first_order_density, free_mask,
    free_time, predicted_angle, second_order_fit, simulated_angle, transition_fit,
)


ROOT = Path(__file__).resolve().parent
NAMES = ["envolvente_primer_orden", "segundo_orden", "transicion", "combinado"]


def viscosity_from_decay(rho, decay):
    inertia = 8e-5 + rho * 5e-8
    return MU0 * (2 * inertia * decay / DAMPING0) ** 2


def first_order_decay(signal):
    y = signal[free_mask]
    center = np.mean(y)
    peaks, _ = find_peaks(np.abs(y - center), distance=20, prominence=0.00005)
    valid = peaks[(free_time[peaks] >= 0.5) & (free_time[peaks] < 13.5)]
    if len(valid) < 10:
        raise RuntimeError(f"No hay suficientes picos válidos: {len(valid)}")
    heights = np.abs(y[valid] - center)
    slope = np.polyfit(free_time[valid], np.log(heights), 1)[0]
    decay = -float(slope)
    if decay <= 0:
        raise RuntimeError(f"Envolvente no amortiguada: {decay}")
    return decay


def estimate(signal):
    first_rho = first_order_density(signal)
    first_mu = viscosity_from_decay(first_rho, first_order_decay(signal))
    second_rho, _, second_decay = second_order_fit(signal)
    second_mu = viscosity_from_decay(second_rho, second_decay)
    _, transition_mu = transition_fit(signal)
    return np.array([first_mu, second_mu, transition_mu])


def run_set(rng, n, label):
    # Same distributions and seeds as the density simulation.
    rho = rng.uniform(997.3, 1017.1, n)
    mu = np.exp(rng.uniform(np.log(0.005), np.log(0.05), n))
    predictions = np.empty((n, REPS, 3))
    for i in range(n):
        for rep in range(REPS):
            predictions[i, rep] = estimate(simulated_angle(rho[i], mu[i], rng))
        if (i + 1) % 20 == 0:
            print(f"{label}: {i + 1}/{n} pares", flush=True)
    return rho, mu, predictions


def metrics(estimates, truth, indexes):
    result = {}
    for i, name in enumerate(NAMES):
        error = estimates[:, :, i] - truth[:, None]
        relative = 100 * error / truth[:, None]
        pair_mape = np.abs(relative).mean(axis=1)
        result[name] = {
            "mape_percent": float(pair_mape.mean()),
            "mape_ci95_percent": np.percentile(
                pair_mape[indexes].mean(axis=1), [2.5, 97.5],
            ).tolist(),
            "mae_pa_s": float(np.abs(error).mean()),
            "bias_pa_s": float(error.mean()),
            "relative_bias_percent": float(relative.mean()),
            "error_sd_pa_s": float(error.std(ddof=1)),
            "p95_absolute_relative_percent": float(np.percentile(np.abs(relative), 95)),
        }
    return result


def main():
    noiseless = predicted_angle(1007, 0.015)
    if abs(transition_fit(noiseless)[1] - 0.015) > 1e-6:
        raise RuntimeError("El modelo de transición no recupera mu sin ruido")
    rho2, _, decay2 = second_order_fit(noiseless)
    if abs(viscosity_from_decay(rho2, decay2) / 0.015 - 1) > 0.02:
        raise RuntimeError("El modelo de segundo orden supera 2 % de error sin ruido")

    rng = np.random.default_rng(20261125)
    _, train_mu, train = run_set(rng, N_TRAIN, "calibración")
    test_rho, test_mu, test = run_set(rng, N_TEST, "evaluación")
    train_relative = train / train_mu[:, None, None] - 1
    train_bias = train_relative.mean(axis=(0, 1))
    corrected_train = train / (1 + train_bias)
    centered_relative = (corrected_train / train_mu[:, None, None] - 1).reshape(-1, 3)
    covariance = np.cov(centered_relative, rowvar=False)
    precision_times_one = np.linalg.solve(covariance, np.ones(3))
    weights = precision_times_one / precision_times_one.sum()

    def combine(predictions):
        combined = (predictions / (1 + train_bias)) @ weights
        return np.concatenate((predictions, combined[:, :, None]), axis=2)

    indexes = rng.integers(0, N_TEST, size=(5000, N_TEST))
    estimates = combine(test)
    summary = metrics(estimates, test_mu, indexes)
    mismatch = np.empty_like(test)
    for i in range(N_TEST):
        for rep in range(REPS):
            mismatch[i, rep] = estimate(
                simulated_angle(test_rho[i], test_mu[i], rng, damping_factor=1.05)
            )
        if (i + 1) % 20 == 0:
            print(f"coeficiente de amortiguamiento +5 %: {i + 1}/{N_TEST} pares",
                  flush=True)
    mismatch_summary = metrics(combine(mismatch), test_mu, indexes)

    result = {
        "parameters": {
            "rho_range_kg_m3": [997.3, 1017.1],
            "mu_range_pa_s": [0.005, 0.05],
            "train_distinct_pairs": N_TRAIN,
            "test_distinct_pairs": N_TEST,
            "noise_repetitions_per_pair": REPS,
            "pulse_width_s": 0.2,
            "observation_s": 15,
            "temperature": "constant",
        },
        "methods": {
            "envolvente_primer_orden": (
                "Fit an exponential to peaks of absolute angular response, "
                "with density inferred from first-order equilibrium."
            ),
            "segundo_orden": (
                "Fit a damped sinusoid and equilibrium, then invert the assumed "
                "damping-viscosity relation."
            ),
            "transicion": (
                "Fit full pulse response, simultaneously estimating density and "
                "viscosity while profiling out a constant angular offset."
            ),
            "combinado": (
                "Combine bias-corrected estimates using relative-error covariance "
                "learned on independent training pairs."
            ),
        },
        "combination_weights": weights.tolist(),
        "summary": summary,
        "damping_mismatch": {
            "actual_damping_coefficient_factor": 1.05,
            "assumed_damping_coefficient_factor": 1,
            "summary": mismatch_summary,
        },
        "limitations": [
            "This is the same synthetic 1.9 Hz oscillator as the density comparison; the real relationship between density, viscosity and damping has not been identified.",
            "The forward and inverse models match in the nominal experiment; reported errors are optimistic and are not laboratory performance.",
            "The first- and second-order methods fit the held samples without explicitly modeling the 104-to-100 Hz sampling and filter, unlike the transition model.",
            "Angular accelerometer data are simulated without real translation, time-varying drift or verified hardware filter response.",
            "Methods share the same signal and their errors are correlated.",
            "Confidence intervals resample independent parameter pairs and exclude structural uncertainty.",
        ],
    }
    (ROOT / "viscosidad_un_pulso_resultados.json").write_text(json.dumps(result, indent=2))
    with (ROOT / "viscosidad_un_pulso_predicciones.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["id", "rep", "rho_real", "mu_real", *NAMES])
        for i in range(N_TEST):
            for rep in range(REPS):
                writer.writerow([i, rep, test_rho[i], test_mu[i], *estimates[i, rep]])

    fig, ax = plt.subplots(figsize=(10, 5), constrained_layout=True)
    for offset, data, label, color in (
        (-0.19, summary, "Modelo coincidente", "#4c78a8"),
        (0.19, mismatch_summary, "Amortiguamiento real +5 %", "#f58518"),
    ):
        values = [data[name]["mape_percent"] for name in NAMES]
        intervals = [data[name]["mape_ci95_percent"] for name in NAMES]
        errors = np.array([[v - ci[0], ci[1] - v]
                           for v, ci in zip(values, intervals)]).T
        x = np.arange(4) + offset
        ax.bar(x, values, width=0.38, color=color, label=label)
        ax.errorbar(x, values, yerr=errors, fmt="none", ecolor="black", capsize=3)
    ax.set_xticks(range(4), ["Envolvente\n1.er orden", "2.º orden",
                             "Transición", "Combinados"])
    ax.set_ylabel("MAPE de viscosidad (%)")
    ax.set_title("Un pulso: estimación sintética de viscosidad; IC 95 % por par")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    fig.savefig(ROOT / "viscosidad_un_pulso.png", dpi=180)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
