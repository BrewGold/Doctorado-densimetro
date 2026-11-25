from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp


ROOT = Path(__file__).parent
DT = 0.005
T = np.arange(0.0, 60.0 + DT / 2, DT)
FREQUENCIES = np.array([0.05, 0.1, 0.2, 0.4, 0.8, 1.6, 3.2, 6.4, 12.8])
PHASES = -np.pi * np.arange(9) * (np.arange(9) + 1) / 9
raw = np.sin(2 * np.pi * FREQUENCIES[:, None] * T + PHASES[:, None]).sum(axis=0)
peak_scale = 0.03 / np.max(np.abs(raw))
rms_scale = (0.03 / np.sqrt(2)) / np.sqrt(np.mean(raw**2))


def multisine(t, scale):
    return scale * sum(
        np.sin(2 * np.pi * f * t + phase)
        for f, phase in zip(FREQUENCIES, PHASES)
    )


drives = {
    "frecuencia_fija_1hz": lambda t: 0.03 * np.sin(2 * np.pi * t),
    "chirp_anterior": lambda t: 0.03 * np.sin(
        2 * np.pi * (0.1 + 1.9 * min(t / 60, 1)) * t
    ),
    "chirp_lineal": lambda t: 0.03 * np.sin(
        2 * np.pi * (0.1 * t + 1.9 * t * t / (2 * 60))
    ),
    "multisine_rmsmatched": lambda t: multisine(t, rms_scale),
    "multisine_peakmatched": lambda t: multisine(t, peak_scale),
}


def main():
    reports = {}
    for name, input_fn in drives.items():
        data = np.genfromtxt(ROOT / f"{name}.csv", delimiter=",", names=True)
        errors = []
        for i in np.linspace(0, len(data) - 1, 5, dtype=int):
            row = data[i]
            inertia = 8e-5 + row["rho"] * 5e-8
            stiffness = 5e-7 * row["rho"]
            damping = 5e-3 * np.sqrt(row["mu"] / 0.02)

            def rhs(t, x):
                return [
                    x[1],
                    (0.02 * input_fn(t) - damping * x[1] -
                     stiffness * np.sin(x[0])) / inertia,
                ]

            sol = solve_ivp(
                rhs, (0, 60), (0, 0), method="RK45", t_eval=T,
                rtol=1e-9, atol=1e-11, max_step=0.001,
            )
            theta, omega = sol.y
            alpha = np.array([rhs(t, [th, om])[1]
                              for t, th, om in zip(T, theta, omega)])
            reference = np.array([
                np.max(np.abs(theta)),
                np.max(np.abs(omega)),
                np.max(np.abs(alpha)),
                np.trapezoid(theta**2, T),
                np.trapezoid(omega**2, T),
            ])
            actual = np.array([
                row["ThetaMax"], row["OmegaMax"], row["AlphaMax"],
                row["Etheta"], row["Eomega"],
            ])
            errors.append(np.abs(actual - reference) /
                          np.maximum(np.abs(reference), 1e-15))
        reports[name] = {
            "median_relative_error": np.median(errors, axis=0).tolist(),
            "max_relative_error": np.max(errors, axis=0).tolist(),
        }
    print(reports)


if __name__ == "__main__":
    main()
