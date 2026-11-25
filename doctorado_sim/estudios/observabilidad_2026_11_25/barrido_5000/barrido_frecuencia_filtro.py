import csv
import ctypes
import json
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import least_squares

from ajustar_sensor import LENGTH, PTR


ROOT = Path(__file__).resolve().parent
FREQUENCIES_HZ = [0.05, 0.1, 0.2, 0.5, 1.0, 1.9, 3.0]
FILTER_CUTOFFS_HZ = [0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 40.0]
PAIR_COUNT = 60
REPETITIONS = 3

lib = ctypes.CDLL(str(ROOT / "ajuste_sensor.so"))
lib.generate_sweep_trial.argtypes = [
    ctypes.c_double, ctypes.c_double, ctypes.c_ulonglong,
    ctypes.c_double, ctypes.c_double, PTR, PTR,
]
lib.generate_sweep_trial.restype = ctypes.c_int
lib.predict_sweep_gyro.argtypes = [
    ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double,
    PTR, PTR,
]
lib.predict_sweep_gyro.restype = ctypes.c_int


def forward(rho, log_mu, cutoff, frequency):
    predicted = np.empty(LENGTH)
    jacobian = np.empty(LENGTH)
    status = lib.predict_sweep_gyro(
        rho, log_mu, cutoff, frequency, predicted, jacobian,
    )
    if status:
        raise RuntimeError("Falló la evaluación del modelo directo")
    return predicted, jacobian


def fit_mu(gyro, rho, cutoff, frequency):
    cached = {}

    def evaluate(x):
        key = float(x[0])
        if key not in cached:
            predicted, jacobian = forward(rho, key, cutoff, frequency)
            residual = predicted - gyro
            cached.clear()
            cached[key] = (
                residual - residual.mean(),
                jacobian - jacobian.mean(),
            )
        return cached[key]

    result = least_squares(
        lambda x: evaluate(x)[0],
        x0=np.array([np.log(0.02)]),
        jac=lambda x: evaluate(x)[1][:, None],
        bounds=(np.log(0.001), np.log(0.1)),
        xtol=1e-11, ftol=1e-11, gtol=1e-11, max_nfev=100,
    )
    if not result.success:
        raise RuntimeError(f"No convergió el ajuste: {result.message}")
    return float(np.exp(result.x[0]))


def main():
    cases = np.genfromtxt(
        ROOT / "imu_casos.csv", delimiter=",", names=True,
        dtype=None, encoding="utf-8",
    )
    test = cases[cases["set"] == "test"].reshape(5, 1000)
    selected = np.linspace(0, 999, PAIR_COUNT, dtype=int)
    rho = test["rho"][0, selected]
    mu = test["mu"][0, selected]
    pair_ids = test["id"][0, selected]

    # Confirm the direct model and its analytic sensitivity are self-consistent.
    point = np.log(0.025)
    predicted, analytic = forward(1100, point, 5.0, 0.5)
    plus, _ = forward(1100, point + 1e-5, 5.0, 0.5)
    minus, _ = forward(1100, point - 1e-5, 5.0, 0.5)
    numerical = (plus - minus) / 2e-5
    if np.max(np.abs(analytic - numerical)) > 1e-7:
        raise RuntimeError("La sensibilidad analítica no coincide con diferencias finitas")
    if abs(fit_mu(predicted, 1100, 5.0, 0.5) - 0.025) > 1e-7:
        raise RuntimeError("El ajuste no recupera los parámetros sin ruido")

    rng = np.random.default_rng(20261125)
    bootstrap_indexes = rng.integers(0, PAIR_COUNT, size=(5000, PAIR_COUNT))
    rows = []
    start = time.monotonic()
    completed = 0
    total = (
        len(FREQUENCIES_HZ) * len(FILTER_CUTOFFS_HZ)
        * REPETITIONS * PAIR_COUNT
    )

    for frequency in FREQUENCIES_HZ:
        for cutoff in FILTER_CUTOFFS_HZ:
            relative_errors = np.empty((REPETITIONS, PAIR_COUNT))
            clips = 0
            for rep in range(REPETITIONS):
                for i, pair_id in enumerate(pair_ids):
                    gyro = np.empty(LENGTH)
                    values = np.empty(15)
                    seed = 89123001 + int(pair_id) * 11 + rep
                    status = lib.generate_sweep_trial(
                        rho[i], mu[i], seed, cutoff, frequency, gyro, values,
                    )
                    if status:
                        raise RuntimeError(
                            f"Falló la simulación: f={frequency} Hz, "
                            f"corte={cutoff} Hz, id={pair_id}, rep={rep}"
                        )
                    clips += int(values[14])
                    estimate = fit_mu(gyro, rho[i], cutoff, frequency)
                    relative_errors[rep, i] = estimate / mu[i] - 1
                    completed += 1
                if completed % 500 == 0:
                    print(
                        f"{completed}/{total} simulaciones; "
                        f"{time.monotonic()-start:.1f} s",
                        flush=True,
                    )

            abs_percent_by_pair = 100 * np.mean(np.abs(relative_errors), axis=0)
            bootstrap_mape = abs_percent_by_pair[bootstrap_indexes].mean(axis=1)
            all_percent = 100 * relative_errors.ravel()
            rows.append({
                "excitation_frequency_hz": frequency,
                "filter_cutoff_hz": cutoff,
                "mape_percent": float(np.mean(np.abs(all_percent))),
                "mape_ci95_percent": np.percentile(
                    bootstrap_mape, [2.5, 97.5],
                ).tolist(),
                "signed_mean_error_percent": float(np.mean(all_percent)),
                "p95_absolute_error_percent": float(
                    np.percentile(np.abs(all_percent), 95),
                ),
                "sensor_saturation_events": clips,
                "pairs": PAIR_COUNT,
                "repetitions_per_pair": REPETITIONS,
            })

    with (ROOT / "barrido_frecuencia_filtro.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    best = min(rows, key=lambda row: row["mape_percent"])
    baseline = next(
        row for row in rows
        if row["excitation_frequency_hz"] == 1.9
        and row["filter_cutoff_hz"] == 20.0
    )
    result = {
        "design": {
            "excitation_frequencies_hz": FREQUENCIES_HZ,
            "filter_cutoffs_hz": FILTER_CUTOFFS_HZ,
            "distinct_parameter_pairs": PAIR_COUNT,
            "noise_repetitions_per_pair": REPETITIONS,
            "actuator_gain": "fixed at nominal",
            "temperature": "fixed; no temperature-dependent drift modeled",
            "fit_assumptions": (
                "True density supplied to isolate viscosity error. The inverse "
                "model knows the excitation frequency and the single-pole filter cutoff."
            ),
            "bootstrap_unit": "parameter pair; repetitions averaged within each pair",
            "limitations": (
                "Exploratory synthetic results under a matched model. The swept "
                "cutoffs are idealized single-pole filters, not verified LSM6DSOX "
                "register settings; actuator dynamics and gain uncertainty are excluded."
            ),
        },
        "best_synthetic_combination": best,
        "reference_1p9hz_20hz": baseline,
        "scenarios": rows,
    }
    (ROOT / "barrido_frecuencia_filtro.json").write_text(
        json.dumps(result, indent=2),
    )

    mape = np.array([
        [next(row["mape_percent"] for row in rows
              if row["excitation_frequency_hz"] == frequency
              and row["filter_cutoff_hz"] == cutoff)
         for cutoff in FILTER_CUTOFFS_HZ]
        for frequency in FREQUENCIES_HZ
    ])
    fig, ax = plt.subplots(figsize=(10, 6), constrained_layout=True)
    image = ax.imshow(mape, aspect="auto", origin="lower", cmap="magma")
    ax.set_xticks(range(len(FILTER_CUTOFFS_HZ)), FILTER_CUTOFFS_HZ)
    ax.set_yticks(range(len(FREQUENCIES_HZ)), FREQUENCIES_HZ)
    ax.set_xlabel("Corte del filtro idealizado (Hz)")
    ax.set_ylabel("Frecuencia de excitación sinusoidal (Hz)")
    ax.set_title("MAPE de viscosidad con frecuencia y filtro conocidos en el ajuste")
    for y in range(len(FREQUENCIES_HZ)):
        for x in range(len(FILTER_CUTOFFS_HZ)):
            ax.text(x, y, f"{mape[y, x]:.1f}%", ha="center", va="center",
                    color="white" if mape[y, x] < np.nanmedian(mape) else "black")
    fig.colorbar(image, ax=ax, label="MAPE de μ (%)")
    fig.savefig(ROOT / "barrido_frecuencia_filtro.png", dpi=180)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
