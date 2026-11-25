import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import RBFInterpolator


ROOT = Path(__file__).parent
EQ_REFERENCE = -0.9746388227722308
EQ_SLOPE = 0.0021440041612968324
EQ_WIDTH = 0.45
DYNAMIC = ["ThetaMax", "OmegaMax", "AlphaMax", "Etheta", "Eomega", "R"]


def fit_predict(train, test, features, outputs):
    x_train = np.column_stack([train[col] for col in features])
    x_test = np.column_stack([test[col] for col in features])
    center, scale = x_train.mean(axis=0), x_train.std(axis=0)
    if np.any(scale == 0):
        raise ValueError(f"Característica constante: {features}")
    model = RBFInterpolator(
        (x_train-center)/scale,
        np.column_stack([train[col] for col in outputs]),
        neighbors=40, kernel="thin_plate_spline", smoothing=1e-3,
    )
    return model((x_test-center)/scale)


def stats(pred, truth, boot_indexes, threshold):
    error = (pred-truth).reshape(5, 1000)
    relative = 100*error/truth.reshape(5, 1000)
    absolute = np.abs(error)
    relative_absolute = np.abs(relative)

    def ci(values):
        per_pair = values.mean(axis=0)
        return np.percentile(per_pair[boot_indexes].mean(axis=1), [2.5, 97.5]).tolist()

    return {
        "bias": float(error.mean()),
        "sd_error": float(error.std(ddof=1)),
        "mean_repeatability_sd": float(error.std(axis=0, ddof=1).mean()),
        "mae": float(absolute.mean()),
        "mae_ci95": ci(absolute),
        "mape_percent": float(relative_absolute.mean()),
        "mape_ci95_percent": ci(relative_absolute),
        "percent_under_threshold": float(np.mean(relative_absolute < threshold)*100),
        "p95_absolute_error": float(np.percentile(absolute, 95)),
    }


def main():
    data = np.genfromtxt(ROOT/"dos_etapas.csv", delimiter=",", names=True,
                         dtype=None, encoding="utf-8")
    if len(data) != 9000 or np.sum(data["set"] == "train") != 4000:
        raise ValueError("Número de observaciones incorrecto")
    train, test = data[data["set"] == "train"], data[data["set"] == "test"]
    cols = DYNAMIC+[
        "ThetaEq", "rho", "mu", "eq_drift", "drive_a", "drive_b",
        "drive_gain", "free_a", "free_b", "free_eq",
    ]
    if not np.isfinite(np.column_stack([data[x] for x in cols])).all():
        raise ValueError("Hay valores no finitos")
    dynamic_mu = fit_predict(train, test, DYNAMIC, ["mu"])[:, 0]
    joint = fit_predict(train, test, ["ThetaEq"]+DYNAMIC, ["rho", "mu"])
    angle = (EQ_REFERENCE-test["ThetaEq"])/EQ_WIDTH
    if np.any(np.abs(angle) >= np.pi/2):
        raise ValueError("Equilibrio fuera del dominio invertible de la calibración sintética")
    equilibrium_rho = 1000+(EQ_WIDTH/EQ_SLOPE)*np.tan(angle)
    free_angle = (EQ_REFERENCE-test["free_eq"])/EQ_WIDTH
    valid_g = (test["drive_a"] > 0) & (test["drive_b"] > 0) & (test["drive_gain"] > 0)
    valid_free = ((test["free_a"] > 0) & (test["free_b"] > 0) &
                  (np.abs(free_angle) < np.pi/2))
    if not valid_g.all() or not valid_free.all():
        raise ValueError(
            f"Ajustes no físicos: G={np.sum(~valid_g)}, respuesta libre={np.sum(~valid_free)}"
        )
    free_rho = 1000+(EQ_WIDTH/EQ_SLOPE)*np.tan(free_angle)
    mu_g = 0.02*(test["drive_a"]*0.02/test["drive_gain"]/0.005)**2
    mu_coupled = 0.02*(
        test["drive_a"]*(8e-5 + 5e-8*free_rho)/0.005
    )**2
    if not np.isfinite(joint).all() or not np.isfinite(dynamic_mu).all():
        raise ValueError("Predicciones no finitas")
    indexes = np.random.default_rng(2027).integers(0, 1000, size=(5000, 1000))
    result = {
        "total_distinct_parameters": 5000,
        "train_distinct_parameters": 4000,
        "test_distinct_parameters": 1000,
        "test_noise_realizations_per_pair": 5,
        "rho_baseline_equilibrium_only": stats(equilibrium_rho, test["rho"], indexes, 5),
        "rho_fit_second_order": stats(free_rho, test["rho"], indexes, 5),
        "rho_joint": stats(joint[:, 0], test["rho"], indexes, 5),
        "mu_baseline_dynamic_only": stats(dynamic_mu, test["mu"], indexes, 10),
        "mu_from_G_gain": stats(mu_g, test["mu"], indexes, 10),
        "mu_from_G_and_rho": stats(mu_coupled, test["mu"], indexes, 10),
        "mu_joint": stats(joint[:, 1], test["mu"], indexes, 10),
        "cases_saturated": int(np.count_nonzero(data["clips"])),
        "eq_window_drift_p95_rad": float(np.percentile(np.abs(test["eq_drift"]), 95)),
    }
    results_file = ROOT/"dos_etapas_resultados.json"
    results_file.write_text(json.dumps(result, indent=2))
    with (ROOT/"dos_etapas_predicciones.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["id", "rep", "rho", "mu", "rho_equilibrio",
                         "rho_segundo_orden", "rho_conjunta", "mu_dinamica",
                         "mu_G", "mu_G_y_rho", "mu_conjunta"])
        for i, row in enumerate(test):
            writer.writerow([row["id"], row["rep"], row["rho"], row["mu"],
                             equilibrium_rho[i], free_rho[i], joint[i, 0],
                             dynamic_mu[i], mu_g[i], mu_coupled[i], joint[i, 1]])

    fig, axes = plt.subplots(1, 2, figsize=(11, 5), constrained_layout=True)
    comparisons = [
        ("Densidad", ["rho_baseline_equilibrium_only", "rho_fit_second_order"],
         ["Media reposo", "Ajuste 2.º orden"]),
        ("Viscosidad", ["mu_from_G_gain", "mu_from_G_and_rho"],
         ["G(s), ganancia", "G(s) y densidad"]),
    ]
    for ax, (title, keys, labels) in zip(axes, comparisons):
        metrics = [result[key] for key in keys]
        values = [m["mape_percent"] for m in metrics]
        intervals = [m["mape_ci95_percent"] for m in metrics]
        uncertainty = np.array([[v-c[0], c[1]-v] for v, c in zip(values, intervals)]).T
        ax.bar([0, 1], values, color=["#4878a8", "#54a24b"])
        ax.errorbar([0, 1], values, yerr=uncertainty, fmt="none",
                    ecolor="black", capsize=5)
        ax.set_xticks([0, 1], labels)
        ax.set(title=title, ylabel="Error porcentual absoluto medio (%)")
        ax.grid(axis="y", alpha=0.25)
    fig.suptitle("Chirp → pulso → reposo: error con IMU simulada (IC 95 %)")
    fig.savefig(ROOT/"dos_etapas_comparacion.png", dpi=160)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
