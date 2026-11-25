from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

path = Path(__file__).parent
data = np.genfromtxt(path / "dataset_observabilidad.csv", delimiter=",", skip_header=1)
columns = ["ThetaMax", "OmegaMax", "AlphaMax", "Etheta", "Eomega", "Td", "R", "rho", "mu"]
fig, axes = plt.subplots(2, 2, figsize=(11, 8), constrained_layout=True)
for ax, x, y in zip(axes.flat, [7, 7, 8, 8], [0, 3, 5, 4]):
    ax.scatter(data[:, x], data[:, y], s=5, alpha=0.4)
    ax.set(xlabel=columns[x], ylabel=columns[y],
           title=f"{columns[x]} vs {columns[y]}")
    ax.grid(alpha=0.25)
fig.suptitle(f"Barrido de observabilidad: {len(data)} simulaciones")
fig.savefig(path / "nubes_5000.png", dpi=150)
