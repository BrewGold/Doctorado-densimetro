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
FS_IMU = 104
FS_HOST = 100
DURATION = 30
SPLIT = 15
F_EXCITATION = 1.9
AMPLITUDE = 0.001
FILTER_HZ = 20
G = 9.80665
ACC_NOISE = 70e-6 * G * np.sqrt(FS_IMU / 2)
GYRO_NOISE = np.deg2rad(0.0038 * np.sqrt(FS_IMU / 2))
ACC_QUANTUM = 0.000061 * G
GYRO_QUANTUM = np.deg2rad(0.00875)
FILTER_ALPHA = 1 - np.exp(-2 * np.pi * FILTER_HZ / FS_IMU)
TS = np.arange(DURATION * FS_IMU + 1) / FS_IMU
TH = np.arange(DURATION * FS_HOST + 1) / FS_HOST
HOST_INDEX = np.floor(TH * FS_IMU + 1e-9).astype(int)
TRAIN = TH < SPLIT
TEST = TH >= SPLIT
W = 2 * np.pi * F_EXCITATION
REPETITIONS = 12


def lowpass(x):
    return lfilter([FILTER_ALPHA], [1, -(1 - FILTER_ALPHA)], x,
                   zi=[(1 - FILTER_ALPHA) * x[0]])[0]


def basis(frequency, decay):
    wd = 2 * np.pi * frequency
    c, s = np.cos(wd * TS), np.sin(wd * TS)
    envelope = np.exp(-decay * TS)
    initial_cos = envelope * c
    initial_sin = envelope * s
    velocity_cos = envelope * (-decay * c - wd * s)
    velocity_sin = envelope * (-decay * s + wd * c)

    wave = np.exp(1j * W * TS)
    common = (decay + 1j * W) / wd
    homogeneous = envelope * (c + common * s)
    homogeneous_dot = envelope * (
        1j * W * c - (wd + decay * common) * s
    )
    denominator = wd**2 + decay**2 - W**2 + 2j * decay * W
    forced = AMPLITUDE * np.imag((wave - homogeneous) / denominator)
    forced_velocity = AMPLITUDE * np.imag(
        (1j * W * wave - homogeneous_dot) / denominator
    )
    return np.array([forced, initial_cos, initial_sin]), np.array(
        [forced_velocity, velocity_cos, velocity_sin]
    )


def signals(params, coefficients):
    theta = np.zeros_like(TS)
    omega = np.zeros_like(TS)
    for (frequency, decay), coef in zip(np.asarray(params).reshape(-1, 2),
                                         np.asarray(coefficients).reshape(-1, 3)):
        angle_basis, gyro_basis = basis(frequency, decay)
        theta += coef @ angle_basis
        omega += coef @ gyro_basis
    return theta, omega


def simulate(params, coefficients, rng, lever_m=0):
    theta, omega = signals(params, coefficients)
    # Tangential sensor acceleration for a specified illustrative lever arm.
    acceleration = np.gradient(omega, 1 / FS_IMU, edge_order=2)
    true_acc = lowpass(G * np.sin(theta) + lever_m * acceleration)
    true_gyro = lowpass(omega)
    bias_acc = rng.normal(0, 0.005 * G)
    bias_gyro = rng.normal(0, np.deg2rad(0.05))
    acc = lowpass(
        G * np.sin(theta) + lever_m * acceleration
        + bias_acc + rng.normal(0, ACC_NOISE, len(TS))
    )
    gyro = lowpass(omega + bias_gyro + rng.normal(0, GYRO_NOISE, len(TS)))
    if np.max(np.abs(acc)) >= 2 * G or np.max(np.abs(gyro)) >= np.deg2rad(250):
        raise RuntimeError("Saturación del sensor")
    acc = np.round(acc / ACC_QUANTUM) * ACC_QUANTUM
    gyro = np.round(gyro / GYRO_QUANTUM) * GYRO_QUANTUM
    return (
        acc[HOST_INDEX], gyro[HOST_INDEX],
        true_acc[HOST_INDEX], true_gyro[HOST_INDEX],
        bias_acc, bias_gyro, float(np.max(np.abs(theta))),
    )


def design(params):
    a_columns = []
    g_columns = []
    for frequency, decay in np.asarray(params).reshape(-1, 2):
        a_basis, g_basis = basis(frequency, decay)
        for angle, velocity in zip(a_basis, g_basis):
            a_columns.append(lowpass(G * angle)[HOST_INDEX])
            g_columns.append(lowpass(velocity)[HOST_INDEX])
    a = np.column_stack(a_columns)
    g = np.column_stack(g_columns)
    # Separate constant offsets for the two physical sensors.
    return (
        np.column_stack([a, np.ones(len(TH)), np.zeros(len(TH))]),
        np.column_stack([g, np.zeros(len(TH)), np.ones(len(TH))]),
    )


def fit(acc, gyro, n_modes):
    def evaluate(params):
        a, g = design(params)
        matrix = np.vstack((a[TRAIN] / ACC_NOISE, g[TRAIN] / GYRO_NOISE))
        target = np.concatenate((acc[TRAIN] / ACC_NOISE, gyro[TRAIN] / GYRO_NOISE))
        coefficients, _, rank, _ = np.linalg.lstsq(matrix, target, rcond=None)
        if rank != matrix.shape[1]:
            raise RuntimeError("La matriz de estimación es singular")
        return matrix @ coefficients - target, coefficients, a, g

    starts = ([[1.9, 0.065], [1.8, 0.08], [2.05, 0.1]] if n_modes == 1
              else [[1.9, 0.065, 1.8, 0.08],
                    [1.9, 0.065, 2.05, 0.08],
                    [1.85, 0.05, 1.98, 0.12]])
    bounds = ([1.5, 0.005] * n_modes, [2.3, 0.3] * n_modes)
    best = None
    for start in starts:
        result = least_squares(
            lambda x: evaluate(x)[0], start, bounds=bounds,
            max_nfev=160, ftol=1e-8, xtol=1e-8, gtol=1e-8,
        )
        if result.success:
            cost = float(np.dot(result.fun, result.fun))
            if best is None or cost < best[0]:
                best = (cost, result.x)
    if best is None:
        raise RuntimeError(f"No convergió el ajuste de {n_modes} modos")
    _, coefficients, a, g = evaluate(best[1])
    return best[1], coefficients, a @ coefficients, g @ coefficients


def score(pred, truth):
    residual = pred[TEST] - truth[TEST]
    centered_truth = truth[TEST] - np.mean(truth[TEST])
    denominator = np.sqrt(np.mean(centered_truth**2))
    if denominator <= 0:
        raise ValueError("Señal de referencia constante")
    return float(100 * np.sqrt(np.mean(residual**2)) / denominator)


def main():
    # Exact noiseless sampled model with independent sensor offsets.
    params = [1.9, 0.064, 1.83, 0.08]
    truth = design(params)
    coefficients = np.array([153.846, 0, 0, 53.846, 0, 0, 0.02, 0.0005])
    acc, gyro = truth[0] @ coefficients, truth[1] @ coefficients
    fitted = fit(acc, gyro, 2)
    if score(fitted[2], acc - coefficients[-2]) > 0.1:
        # Compare after removing the fitted offset; the truth excludes its bias.
        if score(fitted[2] - fitted[1][-2], acc - coefficients[-2]) > 0.1:
            raise RuntimeError("El ajuste de dos modos no recupera señal ideal")

    rng = np.random.default_rng(20261125)
    scenarios = [
        ("un_modo", 1, 0.0),
        ("dos_modos", 2, 0.0),
        ("dos_modos_aceleracion_tangencial", 2, 0.03),
    ]
    rows = []
    example = {}
    for name, mode_count, lever in scenarios:
        for rep in range(REPETITIONS):
            f1 = rng.uniform(1.885, 1.915)
            d1 = rng.uniform(0.055, 0.075)
            params = [f1, d1]
            coef = [153.846, 0, 0]
            if mode_count == 2:
                f2 = rng.uniform(1.81, 1.85)
                d2 = rng.uniform(0.05, 0.10)
                params += [f2, d2]
                coef += [53.846, 0, 0]
            acc, gyro, clean_acc, clean_gyro, ba, bg, max_angle = simulate(
                params, coef, rng, lever,
            )
            for candidate in (1, 2):
                p, c, pred_acc, pred_gyro = fit(acc, gyro, candidate)
                # Bias is estimated, not supplied to the model.
                acc_score = score(pred_acc - ba, clean_acc)
                gyro_score = score(pred_gyro - bg, clean_gyro)
                rows.append({
                    "scenario": name,
                    "trial": rep,
                    "model_modes": candidate,
                    "acc_normalized_rmse_percent": acc_score,
                    "gyro_normalized_rmse_percent": gyro_score,
                    "estimated_poles": p.tolist(),
                    "true_poles": params,
                    "maximum_angle_deg": float(np.rad2deg(max_angle)),
                    "at_pole_bounds": int(np.any(np.isclose(
                        p, [1.5, 0.005] * candidate, atol=1e-4))
                        or np.any(np.isclose(p, [2.3, 0.3] * candidate, atol=1e-4))),
                })
                if rep == 0 and name == "dos_modos":
                    example[candidate] = (pred_acc.copy(), pred_gyro.copy())
            if rep == 0 and name == "dos_modos":
                example["truth"] = (acc.copy(), gyro.copy())
            print(f"{name}: {rep+1}/{REPETITIONS}", flush=True)

    summary = {}
    for name, _, _ in scenarios:
        summary[name] = {}
        for candidate in (1, 2):
            subset = [r for r in rows if r["scenario"] == name
                      and r["model_modes"] == candidate]
            summary[name][str(candidate)] = {
                "median_acc_normalized_rmse_percent": float(np.median(
                    [r["acc_normalized_rmse_percent"] for r in subset])),
                "median_gyro_normalized_rmse_percent": float(np.median(
                    [r["gyro_normalized_rmse_percent"] for r in subset])),
                "max_acc_normalized_rmse_percent": float(np.max(
                    [r["acc_normalized_rmse_percent"] for r in subset])),
                "pole_bound_count": sum(r["at_pole_bounds"] for r in subset),
            }
    result = {
        "design": {
            "excitation_hz": F_EXCITATION,
            "excitation_amplitude_arbitrary_units": AMPLITUDE,
            "duration_s": DURATION,
            "training_s": [0, SPLIT],
            "validation_s": [SPLIT, DURATION],
            "sampling_sensor_hz": FS_IMU,
            "sampling_host_hz": FS_HOST,
            "assumed_lowpass_hz": FILTER_HZ,
            "repetitions_per_scenario": REPETITIONS,
            "second_mode_frequency_range_hz": [1.81, 1.85],
            "second_mode_input_gain_fraction": 0.35,
            "state_model": (
                "Independent oscillators driven by the same sinusoidal actuator; "
                "angle and angular velocity are sums of the mode outputs."
            ),
            "noise_and_offsets": (
                "Gaussian sensor noise, constant independent biases, idealized "
                "low-pass and quantization; angular output via g*sin(theta)."
            ),
            "tangential_lever_arm_m": 0.03,
            "fit": (
                "Joint linearized accelerometer and gyro model, fitted offsets, "
                "per-mode free initial conditions and input gains; fixed input "
                "frequency and modeled filter; no information on rho or mu."
            ),
            "test_metric": (
                "RMS test-window difference from noiseless physical signal, "
                "including bias-estimation error, divided by centered true "
                "test-window signal RMS; truth is available only in simulation."
            ),
        },
        "summary": summary,
        "trials": rows,
        "limitations": [
            "Synthetic experiment; mode coupling, gains, lever arm and noise are assumptions.",
            "Two-mode generator shares its modal structure with the two-mode inverse model.",
            "The 3 cm lever arm is illustrative; sensor location and rigid body kinematics are not validated.",
            "The second mode is not inferred to be a physical liquid mode.",
            "One fixed frequency and finite transient can yield weak or correlated parameter estimates.",
            "The comparison does not estimate density or viscosity or establish real device precision.",
        ],
    }
    (ROOT / "espacio_estados_uno_dos_resultados.json").write_text(json.dumps(result, indent=2))
    with (ROOT / "espacio_estados_uno_dos_resultados.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    fig, axes = plt.subplots(2, 1, figsize=(11, 6), sharex=True, constrained_layout=True)
    for index, (ax, ylabel, factor) in enumerate((
        (axes[0], "Acelerómetro (m/s²)", 1),
        (axes[1], "Giroscopio (°/s)", 180 / np.pi),
    )):
        ax.plot(TH, example["truth"][index] * factor, color="black", linewidth=0.6,
                alpha=0.6, label="Señal simulada")
        for candidate, color in ((1, "tab:orange"), (2, "tab:blue")):
            ax.plot(TH, example[candidate][index] * factor, color=color,
                    linewidth=0.8, label=f"Ajuste {candidate} modo(s)")
        ax.axvline(SPLIT, linestyle="--", color="gray")
        ax.set_ylabel(ylabel)
        ax.grid(alpha=0.2)
    axes[0].set_title("Ejemplo: planta simulada de dos modos; línea separa ajuste y predicción")
    axes[1].set_xlabel("Tiempo (s)")
    axes[0].legend()
    fig.savefig(ROOT / "espacio_estados_uno_dos.png", dpi=160)
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
