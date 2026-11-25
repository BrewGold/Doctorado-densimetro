import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parent
FILES = [
    ("Nominal\n1000 pares", "ajuste_sensor_resultados.json"),
    ("Filtro real 15 Hz\n500 pares", "ajuste_sensor_resultados_filtro15.json"),
    ("Filtro real 25 Hz\n500 pares", "ajuste_sensor_resultados_filtro25.json"),
    ("Actuador real +5 %\n500 pares", "ajuste_sensor_resultados_ganancia105.json"),
]
entries = [(label, json.loads((ROOT/name).read_text())) for label, name in FILES]
values = [entry["mu_forward_model"]["mape_percent"] for _, entry in entries]
intervals = [entry["mu_forward_model"]["mape_ci95_percent"] for _, entry in entries]
errors = np.array([[v-ci[0], ci[1]-v] for v, ci in zip(values, intervals)]).T
fig, ax = plt.subplots(figsize=(11, 5), constrained_layout=True)
ax.bar(range(len(entries)), values, color=["#54a24b", "#4c78a8", "#4c78a8", "#f58518"])
ax.errorbar(range(len(entries)), values, yerr=errors, fmt="none",
            ecolor="black", capsize=5)
ax.set_xticks(range(len(entries)), [label for label, _ in entries])
ax.axhline(10, color="gray", linestyle="--", label="Objetivo de error medio: 10 %")
ax.set(ylabel="MAPE de viscosidad (%)",
       title="Sensibilidad del ajuste que modela la IMU (IC 95 %)")
ax.grid(axis="y", alpha=0.25)
ax.legend()
for i, value in enumerate(values):
    ax.text(i, value+0.12, f"{value:.3f} %", ha="center")
fig.savefig(ROOT/"ajuste_sensor_robustez.png", dpi=160)
