import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import RBFInterpolator


ROOT = Path(__file__).parent
FILES = {
    "Fija 1 Hz": ROOT / "frecuencia_fija_1hz.csv",
    "Chirp fórmula anterior": ROOT / "chirp_anterior.csv",
    "Chirp lineal corregido": ROOT / "chirp_lineal.csv",
    "Multiseno RMS igualada": ROOT / "multisine_rmsmatched.csv",
    "Multiseno pico igualado": ROOT / "multisine_peakmatched.csv",
}
FEATURE_NAMES = ["ThetaMax", "AlphaMax", "Etheta", "Eomega", "R"]


def correlation(x, y):
    if np.std(x) == 0 or np.std(y) == 0:
        return None
    return float(np.corrcoef(x, y)[0, 1])


def main():
    datasets = {
        name: np.genfromtxt(path, delimiter=",", names=True)
        for name, path in FILES.items()
    }
    if any(len(data) != 5000 for data in datasets.values()):
        raise ValueError("Cada excitación debe contener exactamente 5000 casos.")

    split = np.random.RandomState(42).permutation(5000)
    train, test = split[:4000], split[4000:]
    results = {"cases": 5000, "train": len(train), "test": len(test), "methods": {}}
    for name, data in datasets.items():
        matrix = np.column_stack([data[column] for column in
                                  FEATURE_NAMES + ["rho", "mu"]])
        x, y = matrix[:, :len(FEATURE_NAMES)], matrix[:, len(FEATURE_NAMES):]
        center, scale = x[train].mean(axis=0), x[train].std(axis=0)
        scale[scale == 0] = 1
        x_scaled = (x - center) / scale
        model = RBFInterpolator(
            x_scaled[train], y[train], neighbors=40,
            kernel="thin_plate_spline", smoothing=1e-6,
        )
        prediction = model(x_scaled[test])
        errors = prediction - y[test]
        relative = 100 * np.abs(errors / y[test])
        metrics = {}
        for j, target in enumerate(("rho", "mu")):
            metrics[target] = {
                "mae": float(np.mean(np.abs(errors[:, j]))),
                "rmse": float(np.sqrt(np.mean(errors[:, j] ** 2))),
                "r2": float(1 - np.sum(errors[:, j] ** 2) /
                            np.sum((y[test, j] - np.mean(y[test, j])) ** 2)),
                "mape_percent": float(relative[:, j].mean()),
                "within_target_percent": float(np.mean(
                    relative[:, j] < (5 if target == "rho" else 10)) * 100),
            }
        results["methods"][name] = {
            "metrics": metrics,
            "correlations": {
                "ThetaMax_rho": correlation(data["ThetaMax"], data["rho"]),
                "Etheta_rho": correlation(data["Etheta"], data["rho"]),
                "Td_mu": correlation(data["Td"], data["mu"]),
            },
        }

    (ROOT / "comparacion_resultados.json").write_text(
        json.dumps(results, indent=2)
    )
    with (ROOT / "comparacion_resumen.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow([
            "Excitation", "rho_MAE", "rho_MAPE_percent", "rho_R2",
            "mu_MAE", "mu_MAPE_percent", "mu_R2",
            "corr_ThetaMax_rho", "corr_Etheta_rho", "corr_Td_mu",
        ])
        for name, result in results["methods"].items():
            metrics = result["metrics"]
            corr = result["correlations"]
            writer.writerow([
                name,
                metrics["rho"]["mae"], metrics["rho"]["mape_percent"],
                metrics["rho"]["r2"], metrics["mu"]["mae"],
                metrics["mu"]["mape_percent"], metrics["mu"]["r2"],
                corr["ThetaMax_rho"], corr["Etheta_rho"], corr["Td_mu"],
            ])

    fig, axes = plt.subplots(2, 2, figsize=(12, 9), constrained_layout=True)
    colors = ["tab:blue", "tab:orange", "tab:purple", "tab:green", "tab:red"]
    for (name, data), color in zip(datasets.items(), colors):
        axes[0, 0].scatter(data["rho"], data["Etheta"], s=4, alpha=0.25,
                           color=color, label=name)
        axes[0, 1].scatter(data["mu"], data["Td"], s=4, alpha=0.25,
                           color=color, label=name)
    axes[0, 0].set(xlabel="rho (kg/m³)", ylabel="Etheta",
                   title="Densidad vs energía de inclinación")
    axes[0, 1].set(xlabel="mu (Pa·s)", ylabel="Td",
                   title="Viscosidad vs tiempo de disipación")
    for ax in axes[0]:
        ax.grid(alpha=0.25)
        ax.legend(markerscale=3)

    labels = list(datasets)
    xloc = np.arange(len(labels))
    width = 0.34
    for j, target in enumerate(("rho", "mu")):
        values = [results["methods"][label]["metrics"][target]["mape_percent"]
                  for label in labels]
        axes[1, 0].bar(xloc + (j - 0.5) * width, values, width,
                       label=f"{target} MAPE")
    axes[1, 0].set_xticks(xloc, labels, rotation=15)
    axes[1, 0].set_ylabel("Error porcentual absoluto medio (%)")
    axes[1, 0].set_title("Reconstrucción en conjunto de prueba")
    axes[1, 0].grid(axis="y", alpha=0.25)
    axes[1, 0].legend()

    targets = ("rho", "mu")
    for j, target in enumerate(targets):
        values = [
            results["methods"][label]["metrics"][target]["within_target_percent"]
            for label in labels
        ]
        axes[1, 1].bar(xloc + (j - 0.5) * width, values, width,
                       label=f"{target}: dentro del umbral")
    axes[1, 1].set_xticks(xloc, labels, rotation=15)
    axes[1, 1].set_ylim(0, 105)
    axes[1, 1].set_ylabel("Casos del test (%)")
    axes[1, 1].set_title("Umbrales: rho <5%, mu <10%")
    axes[1, 1].grid(axis="y", alpha=0.25)
    axes[1, 1].legend()

    fig.suptitle("Comparación de excitaciones: 5000 casos sintéticos")
    fig.savefig(ROOT / "comparacion_excitaciones.png", dpi=150)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
