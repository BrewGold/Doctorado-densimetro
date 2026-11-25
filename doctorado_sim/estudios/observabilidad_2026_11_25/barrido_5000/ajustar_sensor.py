import argparse
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


ROOT = Path(__file__).resolve().parent
EQ_REFERENCE = -0.9746388227722308
EQ_SLOPE = 0.0021440041612968324
EQ_WIDTH = 0.45
LENGTH = 6001
PTR = np.ctypeslib.ndpointer(dtype=np.float64, ndim=1, flags="C_CONTIGUOUS")
lib = ctypes.CDLL(str(ROOT / "ajuste_sensor.so"))
lib.generate_trial.argtypes = [ctypes.c_double, ctypes.c_double,
                               ctypes.c_ulonglong, ctypes.c_double,
                               ctypes.c_double, PTR, PTR]
lib.generate_trial.restype = ctypes.c_int
lib.predict_gyro.argtypes = [ctypes.c_double, ctypes.c_double, PTR, PTR]
lib.predict_gyro.restype = ctypes.c_int


def forward(rho, log_mu):
    predicted = np.empty(LENGTH)
    jacobian = np.empty(LENGTH)
    if lib.predict_gyro(rho, log_mu, predicted, jacobian):
        raise RuntimeError("Falló la evaluación del modelo de IMU")
    return predicted, jacobian


def fit_mu(gyro, rho):
    cached = {}

    def evaluate(x):
        key = float(x[0])
        if key not in cached:
            predicted, jacobian = forward(rho, key)
            residual = predicted-gyro
            cached.clear()
            cached[key] = (residual-residual.mean(), jacobian-jacobian.mean())
        return cached[key]

    result = least_squares(
        lambda x: evaluate(x)[0],
        x0=np.array([np.log(0.02)]),
        jac=lambda x: evaluate(x)[1][:, None],
        bounds=(np.log(0.001), np.log(0.1)),
        xtol=1e-11, ftol=1e-11, gtol=1e-11,
        max_nfev=100,
    )
    if not result.success:
        raise RuntimeError(f"No convergió el ajuste: {result.message}")
    return float(np.exp(result.x[0])), int(result.nfev)


def summarize(truth, predicted, indexes, threshold):
    error = predicted-truth
    percent = 100*np.abs(error/truth)
    bootstrap = percent.mean(axis=0)[indexes].mean(axis=1)
    return {
        "mape_percent": float(percent.mean()),
        "mape_ci95_percent": np.percentile(bootstrap, [2.5, 97.5]).tolist(),
        "mae": float(np.abs(error).mean()),
        "error_sd": float(error.std(ddof=1)),
        "bias": float(error.mean()),
        "p95_relative_percent": float(np.percentile(percent, 95)),
        "under_threshold_percent": float(np.mean(percent < threshold)*100),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pairs", type=int, default=1000)
    parser.add_argument("--cutoff", type=float, default=20)
    parser.add_argument("--actuator-factor", type=float, default=1)
    parser.add_argument("--tag", default="")
    args = parser.parse_args()
    if not 1 <= args.pairs <= 1000:
        raise ValueError("--pairs debe estar entre 1 y 1000")
    if args.cutoff <= 0 or args.actuator_factor <= 0:
        raise ValueError("La frecuencia y el factor deben ser positivos")
    if args.tag and not args.tag.replace("_", "").isalnum():
        raise ValueError("El sufijo solo puede contener letras, números y guiones bajos")
    suffix = f"_{args.tag}" if args.tag else ""

    # Check the sensitivity used by the optimizer against finite differences.
    point = np.log(0.025)
    predicted, analytic = forward(1100, point)
    plus, _ = forward(1100, point+1e-5)
    minus, _ = forward(1100, point-1e-5)
    numerical = (plus-minus)/(2e-5)
    err = np.max(np.abs(analytic-numerical))
    if err > 1e-7:
        raise ValueError(f"Jacobiano incorrecto: {err}")
    if abs(fit_mu(predicted, 1100)[0]-0.025) > 1e-7:
        raise ValueError("El ajuste no recupera los parámetros sin ruido")

    data = np.genfromtxt(ROOT/"imu_casos.csv", delimiter=",", names=True,
                         dtype=None, encoding="utf-8")
    test = data[data["set"] == "test"].reshape(5, 1000)[:, :args.pairs]
    shape = test.shape
    rho = test["rho"].copy()
    mu = test["mu"].copy()
    rho_est = np.empty(shape)
    mu_before = np.empty(shape)
    mu_ratio = np.empty(shape)
    mu_corrected = np.empty(shape)
    nfev = np.empty(shape, dtype=int)
    clipped = 0
    start = time.monotonic()

    for r in range(shape[0]):
        for i in range(shape[1]):
            row = test[r, i]
            gyro = np.empty(LENGTH)
            output = np.empty(15)
            seed = 89123001 + int(row["id"])*11 + r
            if lib.generate_trial(row["rho"], row["mu"], seed, args.cutoff,
                                  args.actuator_factor, gyro, output):
                raise RuntimeError(f"Falló el caso {row['id']} repetición {r}")
            clipped += int(output[14])
            a, b, gain = output[8:11]
            free_a, free_b, theta_eq = output[11:14]
            angle = (EQ_REFERENCE-theta_eq)/EQ_WIDTH
            if min(a, b, gain, free_a, free_b) <= 0 or abs(angle) >= np.pi/2:
                raise ValueError(f"Ajuste físico anterior inválido: id {row['id']}, rep {r}")
            rho_est[r, i] = 1000 + EQ_WIDTH/EQ_SLOPE*np.tan(angle)
            if 8e-5 + rho_est[r, i]*5e-8 <= 0:
                raise ValueError(f"Inercia inválida para id {row['id']}")
            mu_before[r, i] = 0.02*(
                a*(8e-5+rho_est[r, i]*5e-8)/0.005)**2
            mu_ratio[r, i] = 0.02*(a*0.02/gain/0.005)**2
            mu_corrected[r, i], nfev[r, i] = fit_mu(gyro, rho_est[r, i])
            if (r*shape[1]+i+1) % 500 == 0:
                print(f"{r*shape[1]+i+1}/{shape[0]*shape[1]} "
                      f"{time.monotonic()-start:.1f}s", flush=True)

    rng = np.random.default_rng(2027)
    indexes = rng.integers(0, args.pairs, size=(5000, args.pairs))
    summary = {
        "distinct_test_pairs": args.pairs,
        "repetitions": shape[0],
        "true_sensor_lowpass_hz": args.cutoff,
        "assumed_sensor_lowpass_hz": 20,
        "true_actuator_factor": args.actuator_factor,
        "assumed_actuator_factor": 1,
        "description": "bootstrap emparejado por par de parametros; modelo fijo",
        "rho_fit_second_order": summarize(rho, rho_est, indexes, 5),
        "mu_previous_coupling": summarize(mu, mu_before, indexes, 10),
        "mu_previous_gain_ratio": summarize(mu, mu_ratio, indexes, 10),
        "mu_forward_model": summarize(mu, mu_corrected, indexes, 10),
        "sensor_saturation_events": clipped,
        "optimizer_mean_nfev": float(nfev.mean()),
    }
    difference = (100*np.abs((mu_corrected-mu)/mu) -
                  100*np.abs((mu_before-mu)/mu)).mean(axis=0)
    summary["paired_difference_new_minus_old_pp"] = {
        "mean": float(difference.mean()),
        "ci95": np.percentile(difference[indexes].mean(axis=1), [2.5, 97.5]).tolist(),
    }
    (ROOT/f"ajuste_sensor_resultados{suffix}.json").write_text(json.dumps(summary, indent=2))
    with (ROOT/f"ajuste_sensor_predicciones{suffix}.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["id", "rep", "rho", "mu", "rho_segundo_orden",
                         "mu_correcion_anterior", "mu_ratio_ganancia",
                         "mu_modelo_imu", "nfev"])
        for r in range(shape[0]):
            for i in range(shape[1]):
                writer.writerow([
                    test["id"][r, i], r, rho[r, i], mu[r, i], rho_est[r, i],
                    mu_before[r, i], mu_ratio[r, i], mu_corrected[r, i], nfev[r, i],
                ])
    metrics = [summary["mu_previous_coupling"], summary["mu_previous_gain_ratio"],
               summary["mu_forward_model"]]
    values = [m["mape_percent"] for m in metrics]
    intervals = [m["mape_ci95_percent"] for m in metrics]
    error = np.array([[v-ci[0], ci[1]-v] for v, ci in zip(values, intervals)]).T
    fig, ax = plt.subplots(figsize=(9, 5), constrained_layout=True)
    ax.bar(range(3), values, color=["#c74e46", "#f0a54b", "#54a24b"])
    ax.errorbar(range(3), values, yerr=error, fmt="none", ecolor="black", capsize=5)
    ax.set_xticks(range(3), ["Corrección anterior", "Cociente de G(s)", "Modelo con IMU"])
    ax.set_ylabel("Error porcentual absoluto medio de μ (%)")
    ax.set_title(f"Viscosidad: {args.pairs} pares, cinco repeticiones; IC 95 %")
    ax.grid(axis="y", alpha=0.25)
    fig.savefig(ROOT/f"ajuste_sensor_comparacion{suffix}.png", dpi=160)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
