import csv
import json
import zipfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import optimize, signal


ROOT = Path(__file__).resolve().parent
ZIP = ROOT.parents[3] / "references/tfm/datos_udp.zip"
FS = 100.0
TRAIN_START, TRAIN_END, TEST_END = 5.0, 15.0, 25.0
SOS = signal.butter(4, [1.0, 3.0], btype="bandpass", fs=FS, output="sos")


def load(archive, name):
    with archive.open(name) as stream:
        data = np.genfromtxt(stream, delimiter=",", names=True)
    if not np.all(np.isfinite(data["t_ms"])) or not np.all(np.isfinite(data["ang_deg"])):
        raise ValueError(f"{name}: datos no finitos")
    delta = np.diff(data["t_ms"])
    resets = np.flatnonzero(delta <= 0)
    start = int(resets[-1]+1) if len(resets) else 0
    data = data[start:]
    t = (data["t_ms"]-data["t_ms"][0])/1000
    if t[-1] < TEST_END:
        raise ValueError(f"{name}: menos de {TEST_END} s")
    dt = np.diff(t)
    if np.any(dt <= 0):
        raise ValueError(f"{name}: tiempo no creciente tras el reinicio")
    if np.any(dt[(t[:-1] < TEST_END)] > 0.1):
        return None, {"file": Path(name).name, "reason": "hueco >100 ms antes de 25 s"}
    grid = np.arange(0, TEST_END, 1/FS)
    y = np.interp(grid, t, data["ang_deg"])
    band = signal.sosfilt(SOS, y-y[0])
    return {
        "name": Path(name).name,
        "time": grid,
        "raw": y,
        "band": band,
        "discarded_prefix": start,
        "max_gap": float(np.max(dt[(t[:-1] < TEST_END)])),
    }, None


def design(t, frequency, decay):
    envelope = np.exp(-decay*t)
    phase = 2*np.pi*frequency*t
    return np.column_stack((envelope*np.cos(phase), envelope*np.sin(phase)))


def fit_mode(t, y):
    def residual(parameters):
        matrix = design(t, *parameters)
        amplitude = np.linalg.lstsq(matrix, y, rcond=None)[0]
        return matrix@amplitude-y

    best = None
    for frequency in np.linspace(1.5, 2.3, 9):
        result = optimize.least_squares(
            residual, [frequency, 0.08],
            bounds=([1.5, 0], [2.3, 1]),
            ftol=1e-10, xtol=1e-10, gtol=1e-10, max_nfev=150,
        )
        if not result.success:
            raise RuntimeError(f"No convergió el ajuste: {result.message}")
        cost = float(np.sum(result.fun**2))
        if best is None or cost < best[0]:
            best = (cost, result.x)
    frequency, decay = best[1]
    coefficients = np.linalg.lstsq(design(t, frequency, decay), y, rcond=None)[0]
    return float(frequency), float(decay), coefficients


def score(t_train, y_train, t_test, y_test, frequency, decay):
    coefficients = np.linalg.lstsq(design(t_train, frequency, decay), y_train, rcond=None)[0]
    predicted = design(t_test, frequency, decay)@coefficients
    zero_error = np.sum(y_test**2)
    if zero_error <= 0:
        raise ValueError("La ventana de prueba tiene energía nula")
    return float(1-np.sum((y_test-predicted)**2)/zero_error), predicted


def main():
    trials = []
    excluded = []
    with zipfile.ZipFile(ZIP) as archive:
        for name in sorted(archive.namelist()):
            if name.endswith(".csv"):
                item, reason = load(archive, name)
                if reason:
                    excluded.append(reason)
                else:
                    trials.append(item)
    if len(trials) < 19:
        raise ValueError(f"Se esperaban al menos 19 registros válidos, hay {len(trials)}")

    for trial in trials:
        t = trial["time"]
        train = (t >= TRAIN_START) & (t < TRAIN_END)
        test = (t >= TRAIN_END) & (t < TEST_END)
        tt, tv = t[train]-TRAIN_START, t[test]-TRAIN_START
        yt, yv = trial["band"][train], trial["band"][test]
        frequency, decay, coefficients = fit_mode(tt, yt)
        natural = np.hypot(2*np.pi*frequency, decay)
        trial["f"] = frequency
        trial["decay"] = decay
        trial["fn"] = natural/(2*np.pi)
        trial["zeta"] = decay/natural
        trial["train_r2"] = float(
            1 - np.sum((yt-design(tt, frequency, decay)@coefficients)**2) /
            np.sum(yt**2)
        )
        trial["within_r2"], trial["within_prediction"] = score(
            tt, yt, tv, yv, frequency, decay)

    train_trials, heldout_trials = trials[:12], trials[12:]
    common_f = float(np.median([trial["f"] for trial in train_trials]))
    common_decay = float(np.median([trial["decay"] for trial in train_trials]))
    for trial in heldout_trials:
        t = trial["time"]
        train = (t >= TRAIN_START) & (t < TRAIN_END)
        test = (t >= TRAIN_END) & (t < TEST_END)
        trial["common_r2"], trial["common_prediction"] = score(
            t[train]-TRAIN_START, trial["band"][train],
            t[test]-TRAIN_START, trial["band"][test],
            common_f, common_decay,
        )

    rng = np.random.default_rng(42)
    bootstrap = rng.integers(0, len(train_trials), size=(10000, len(train_trials)))
    f_train = np.array([trial["f"] for trial in train_trials])
    decay_train = np.array([trial["decay"] for trial in train_trials])
    ci_f = np.percentile(np.median(f_train[bootstrap], axis=1), [2.5, 97.5])
    ci_decay = np.percentile(np.median(decay_train[bootstrap], axis=1), [2.5, 97.5])
    common_omega = np.hypot(2*np.pi*common_f, common_decay)
    summary = {
        "files_input": len(trials)+len(excluded),
        "files_accepted": len(trials),
        "excluded": excluded,
        "files_training": len(train_trials),
        "files_validation": len(heldout_trials),
        "preprocess": (
            "ang_deg, datos reinterpolados a 100 Hz, filtro causal Butterworth "
            "orden 4 banda 1-3 Hz; inicio 5s, ajuste 5-15s, validacion 15-25s"
        ),
        "common_fit": {
            "damped_frequency_hz_median": common_f,
            "damped_frequency_hz_ci95_bootstrap": ci_f.tolist(),
            "decay_per_s_median": common_decay,
            "decay_per_s_ci95_bootstrap": ci_decay.tolist(),
            "natural_frequency_hz": common_omega/(2*np.pi),
            "damping_ratio": common_decay/common_omega,
            "a1_per_s": 2*common_decay,
            "a0_per_s2": common_omega**2,
        },
        "training_single_mode_r2_median": float(np.median([r["train_r2"] for r in train_trials])),
        "validation_common_model_r2_median": float(np.median([r["common_r2"] for r in heldout_trials])),
        "validation_common_model_r2": [r["common_r2"] for r in heldout_trials],
        "validation_common_model_beats_zero": sum(r["common_r2"]>0 for r in heldout_trials),
        "validation_per_record_r2_median": float(np.median([r["within_r2"] for r in heldout_trials])),
        "validation_note": (
            "Frecuencia y decaimiento compartidos, aprendidos de los primeros 12 registros; "
            "para cada registro de validación solo se ajustan amplitud y fase en 5–15 s; "
            "la ventana 15–25 s no se usa en ningún ajuste."
        ),
    }
    (ROOT/"resultados_ajuste.json").write_text(json.dumps(summary, indent=2))
    with (ROOT/"parametros_por_registro.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["archivo","grupo","prefijo_descartado","max_hueco_s",
                         "fd_Hz","lambda_s_1","fn_Hz","zeta","R2_ajuste",
                         "R2_prueba_individual","R2_prueba_comun"])
        for i, trial in enumerate(trials):
            writer.writerow([
                trial["name"], "ajuste" if i<len(train_trials) else "validacion",
                trial["discarded_prefix"], trial["max_gap"],
                trial["f"], trial["decay"], trial["fn"], trial["zeta"],
                trial["train_r2"], trial["within_r2"], trial.get("common_r2", ""),
            ])

    selected = heldout_trials[len(heldout_trials)//2]
    t = selected["time"]
    fit_window = (t>=TRAIN_START)&(t<TRAIN_END)
    test_window = (t>=TRAIN_END)&(t<TEST_END)
    fit_t = t[fit_window]-TRAIN_START
    fit_y = selected["band"][fit_window]
    fitted_coefs = np.linalg.lstsq(design(fit_t, common_f, common_decay),fit_y,rcond=None)[0]
    tt = t[t>=TRAIN_START]-TRAIN_START
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
    axes[0, 0].plot(t, selected["raw"], lw=.7)
    axes[0, 0].set(title=f"Ángulo observado: {selected['name']}",
                   xlabel="Tiempo (s)", ylabel="ang_deg")
    axes[0, 1].plot(t[t>=TRAIN_START], selected["band"][t>=TRAIN_START],
                    lw=.9, label="Observado (banda 1–3 Hz)")
    axes[0, 1].plot(t[t>=TRAIN_START], design(tt,common_f,common_decay)@fitted_coefs,
                    lw=1, label="Modo identificado")
    axes[0, 1].axvline(TRAIN_END, color="black", ls="--", label="Inicio de prueba")
    axes[0, 1].set(title=f"Ejemplo: R² prueba = {selected['common_r2']:.2f}",
                   xlabel="Tiempo (s)", ylabel="Señal filtrada (°)")
    axes[0, 1].legend(fontsize=8)
    axes[1, 0].hist([r["f"] for r in train_trials], bins=10, alpha=.7, label="Ajuste")
    axes[1, 0].hist([r["f"] for r in heldout_trials], bins=10, alpha=.7, label="Validación")
    axes[1, 0].axvline(common_f, color="black", ls="--", label="Mediana de ajuste")
    axes[1, 0].set(title="Frecuencias individuales en 5–15 s",
                   xlabel="Frecuencia amortiguada (Hz)", ylabel="Ensayos")
    axes[1, 0].legend(fontsize=8)
    scores = [r["common_r2"] for r in heldout_trials]
    axes[1, 1].bar(np.arange(len(scores)), scores)
    axes[1, 1].axhline(0, color="black", lw=1)
    axes[1, 1].set(title="Validación temporal en ensayos independientes",
                   xlabel="Registro de validación", ylabel="R² frente a señal nula")
    for ax in axes.flat:
        ax.grid(alpha=.2)
    fig.suptitle("Identificación exploratoria: registros de respuesta libre del TFM")
    fig.savefig(ROOT/"ajuste_registros.png", dpi=160)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
