import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import RBFInterpolator


ROOT = Path(__file__).parent
METHODS = {
    "Fija 1 Hz": "fija",
    "Chirp anterior": "chirp_anterior",
    "Chirp lineal": "chirp_lineal",
    "Multiseno": "multiseno_pico",
}
FEATURES = ["ThetaMax", "OmegaMax", "AlphaMax", "Etheta", "Eomega", "R"]
TARGETS = ["rho", "mu"]


def ci_mean_per_case(values, indexes):
    per_case = values.mean(axis=0)
    boot = per_case[indexes].mean(axis=1)
    return np.percentile(boot, [2.5, 97.5]).tolist()


def main():
    bootstrap_rng = np.random.default_rng(2027)
    indexes = bootstrap_rng.integers(0, 1000, size=(5000, 1000))
    summary = {
        "train_parameters": 4000,
        "test_parameters": 1000,
        "test_repetitions": 5,
        "bootstrap": "5000 remuestreos agrupados por par rho-mu",
        "features": FEATURES,
        "results": {},
    }
    predictions = {}
    real_targets = None
    with (ROOT / "imu_predicciones.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["method", "id", "rep", "rho", "mu", "rho_pred", "mu_pred"])
        for label, name in METHODS.items():
            path = ROOT / f"imu_{name}.csv"
            data = np.genfromtxt(path, delimiter=",", names=True, dtype=None, encoding="utf-8")
            if len(data) != 9000 or np.sum(data["set"] == "train") != 4000:
                raise ValueError(f"Datos incompletos: {path}")
            train = data[data["set"] == "train"]
            test = data[data["set"] == "test"]
            if not np.all(np.isfinite(np.column_stack([data[f] for f in FEATURES + TARGETS]))):
                raise ValueError(f"Hay valores no finitos en {path}")
            x_train = np.column_stack([train[f] for f in FEATURES])
            x_test = np.column_stack([test[f] for f in FEATURES])
            y_train = np.column_stack([train[f] for f in TARGETS])
            y_test = np.column_stack([test[f] for f in TARGETS])
            center = x_train.mean(axis=0)
            scale = x_train.std(axis=0)
            if np.any(scale == 0):
                raise ValueError(f"Característica constante en {label}")
            model = RBFInterpolator(
                (x_train - center) / scale, y_train,
                neighbors=40, kernel="thin_plate_spline", smoothing=1e-3,
            )
            predicted = model((x_test - center) / scale)
            if not np.isfinite(predicted).all():
                raise ValueError(f"Predicciones no finitas en {label}")
            errors = predicted - y_test
            per_target = {}
            for j, target in enumerate(TARGETS):
                err = errors[:, j].reshape(5, 1000)
                rel = 100 * err / y_test[:, j].reshape(5, 1000)
                abs_err = np.abs(err)
                abs_rel = np.abs(rel)
                per_target[target] = {
                    "signed_bias": float(err.mean()),
                    "signed_error_sd": float(err.std(ddof=1)),
                    "mean_within_case_prediction_sd": float(
                        predicted[:, j].reshape(5, 1000).std(axis=0, ddof=1).mean()
                    ),
                    "mae": float(abs_err.mean()),
                    "mae_ci95": ci_mean_per_case(abs_err, indexes),
                    "rmse": float(np.sqrt(np.mean(err**2))),
                    "mape_percent": float(abs_rel.mean()),
                    "mape_ci95_percent": ci_mean_per_case(abs_rel, indexes),
                    "signed_error_sd_percent": float(rel.std(ddof=1)),
                    "threshold_percent": float(np.mean(
                        abs_rel < (5 if target == "rho" else 10)) * 100),
                }
            summary["results"][label] = {
                "targets": per_target,
                "saturated_cases": int(np.count_nonzero(data["clips"])),
            }
            predictions[label] = predicted.reshape(5, 1000, 2)
            if real_targets is None:
                real_targets = y_test.reshape(5, 1000, 2)
            elif not np.array_equal(real_targets, y_test.reshape(5, 1000, 2)):
                raise ValueError("Los parámetros no coinciden entre excitaciones")
            for row, output in zip(test, predicted):
                writer.writerow([
                    label, row["id"], row["rep"], row["rho"], row["mu"],
                    output[0], output[1],
                ])

    comparison = {}
    for j, target in enumerate(TARGETS):
        fixed = 100 * np.abs(
            (predictions["Chirp lineal"][:, :, j] - real_targets[:, :, j]) /
            real_targets[:, :, j]
        )
        multi = 100 * np.abs(
            (predictions["Multiseno"][:, :, j] - real_targets[:, :, j]) /
            real_targets[:, :, j]
        )
        delta = multi - fixed
        comparison[target] = {
            "mape_difference_multiseno_minus_chirp_pp": float(delta.mean()),
            "ci95_pp": ci_mean_per_case(delta, indexes),
        }
    summary["paired_comparison"] = comparison
    (ROOT / "imu_resultados.json").write_text(json.dumps(summary, indent=2))

    fig, axes = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)
    labels = list(METHODS)
    for j, (ax, target) in enumerate(zip(axes, TARGETS)):
        values = [summary["results"][name]["targets"][target]["mape_percent"]
                  for name in labels]
        intervals = [summary["results"][name]["targets"][target]["mape_ci95_percent"]
                     for name in labels]
        errors = np.array([[v - ci[0], ci[1] - v]
                           for v, ci in zip(values, intervals)]).T
        ax.bar(np.arange(len(labels)), values, color=["#4878a8", "#f58518", "#a57abb", "#54a24b"])
        ax.errorbar(np.arange(len(labels)), values, yerr=errors,
                    fmt="none", ecolor="black", capsize=4)
        ax.set_xticks(np.arange(len(labels)), labels, rotation=20, ha="right")
        ax.set_ylabel("Error porcentual absoluto medio (%)")
        ax.set_title(f"{target}: MAPE e IC del 95 %")
        ax.grid(axis="y", alpha=0.25)
    fig.suptitle("Comparación con modelo de IMU y datos sintéticos")
    fig.savefig(ROOT / "imu_comparacion_ic.png", dpi=160)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
