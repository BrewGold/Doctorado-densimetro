import csv
import json
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import RBFInterpolator


OUT = Path(__file__).parent
N = 2000
COLUMNS = [
    "ThetaMax", "OmegaMax", "AlphaMax", "Etheta", "Eomega",
    "Td", "R", "rho", "mu",
]


def simulate(rho, mu, rtol=1e-3, atol=1e-6, max_step=6.0):
    inertia = 8e-5 + rho * 5e-8
    stiffness = 5e-4 * (rho / 1000)
    damping = 5e-3 * np.sqrt(mu / 0.02)

    def rhs(t, x):
        freq = 0.10 + (2.00 - 0.10) * min(t / 60, 1)
        u = 0.03 * np.sin(2 * np.pi * freq * t)
        return [x[1], (0.02 * u - damping * x[1] -
                       stiffness * np.sin(x[0])) / inertia]

    sol = solve_ivp(rhs, (0, 60), (0, 0), method="RK45",
                    rtol=rtol, atol=atol, max_step=max_step)
    if not sol.success:
        raise RuntimeError(sol.message)
    t = sol.t
    theta, omega = sol.y
    alpha = np.gradient(omega) / np.gradient(t)
    theta_max = np.max(np.abs(theta))
    e_theta = np.trapezoid(theta**2, t)
    e_omega = np.trapezoid(omega**2, t)
    idx = np.flatnonzero(np.abs(theta) > 0.05 * theta_max)
    td = t[idx[-1]] if len(idx) else 0
    return np.array([theta_max, np.max(np.abs(omega)), np.max(np.abs(alpha)),
                     e_theta, e_omega, td, e_theta / (e_omega + np.finfo(float).eps)])


def main():
    rng = np.random.RandomState(1)
    data = np.zeros((N, 9))
    count = 0
    start = time.monotonic()
    for k in range(N):
        rho = 800 + 600 * rng.rand()
        mu = 0.001 + 0.099 * rng.rand()
        feat = simulate(rho, mu)
        if not np.all(np.isfinite(feat)):
            continue
        data[count] = [*feat, rho, mu]
        count += 1
        if (k + 1) % 100 == 0:
            print(f"{k + 1}/{N}: {time.monotonic()-start:.1f}s", flush=True)
    data = data[:count]
    with (OUT / "dataset_observabilidad.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(COLUMNS)
        writer.writerows(data)

    fig, axes = plt.subplots(2, 2, figsize=(11, 8), constrained_layout=True)
    for ax, x, y in zip(axes.flat, [7, 7, 8, 8], [0, 3, 5, 4]):
        ax.scatter(data[:, x], data[:, y], s=5, alpha=0.4)
        ax.set(xlabel=COLUMNS[x], ylabel=COLUMNS[y],
               title=f"{COLUMNS[x]} vs {COLUMNS[y]}")
        ax.grid(alpha=0.25)
    fig.suptitle(f"Barrido de observabilidad: {count} simulaciones")
    fig.savefig(OUT / "nubes_observabilidad.png", dpi=150)
    plt.close(fig)

    corr = np.corrcoef(data, rowvar=False)
    fig, ax = plt.subplots(figsize=(10, 8), constrained_layout=True)
    im = ax.imshow(corr, vmin=-1, vmax=1, cmap="RdBu_r")
    ax.set_xticks(range(9), COLUMNS, rotation=45, ha="right")
    ax.set_yticks(range(9), COLUMNS)
    for i in range(9):
        for j in range(9):
            ax.text(j, i, f"{corr[i, j]:.2f}", ha="center", va="center",
                    color="white" if abs(corr[i, j]) > 0.6 else "black", fontsize=8)
    ax.set_title("Matriz de correlación de Pearson")
    fig.colorbar(im, ax=ax)
    fig.savefig(OUT / "matriz_correlacion.png", dpi=150)
    plt.close(fig)

    # Compare default integration with a tighter solve on a representative subset.
    selected = np.linspace(0, count - 1, min(30, count), dtype=int)
    precise = np.array([simulate(*data[i, 7:], rtol=1e-8, atol=1e-10, max_step=0.02)
                        for i in selected])
    rel = np.abs(data[selected, :7] - precise) / np.maximum(np.abs(precise), 1e-15)
    # Fit only the ideal synthetic data; test points were not used for training.
    split = np.random.RandomState(42).permutation(count)
    train, test = split[:int(count * 0.8)], split[int(count * 0.8):]
    x = data[:, :7]
    center, scale = x[train].mean(axis=0), x[train].std(axis=0)
    scale[scale == 0] = 1
    x = (x - center) / scale
    y = data[:, 7:]
    interpolator = RBFInterpolator(x[train], y[train], neighbors=30,
                                   kernel="thin_plate_spline", smoothing=1e-8)
    predictions = interpolator(x[test])
    metrics = {}
    for j, name in enumerate(COLUMNS[7:]):
        errors = predictions[:, j] - y[test, j]
        metrics[name] = {
            "mae": float(np.mean(np.abs(errors))),
            "rmse": float(np.sqrt(np.mean(errors**2))),
            "r2": float(1 - np.sum(errors**2) /
                        np.sum((y[test, j] - np.mean(y[test, j]))**2)),
        }
    results = {
        "valid": count, "correlation": corr.tolist(),
        "td_at_60": int(np.count_nonzero(data[:, 5] == 60)),
        "integration_relative_error_median": np.median(rel, axis=0).tolist(),
        "integration_relative_error_max": np.max(rel, axis=0).tolist(),
        "holdout": metrics,
    }
    (OUT / "resultados.json").write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2), flush=True)


if __name__ == "__main__":
    main()
