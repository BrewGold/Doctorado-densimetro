import csv
from pathlib import Path

import numpy as np

root = Path(__file__).parent
data = np.genfromtxt(root / "frecuencia_fija_1hz.csv", delimiter=",", names=True)
order = np.random.RandomState(42).permutation(len(data))
with (root / "imu_casos.csv").open("w", newline="") as stream:
    writer = csv.writer(stream)
    writer.writerow(["id", "set", "rep", "rho", "mu"])
    for i in order[:4000]:
        writer.writerow([i, "train", 0, data["rho"][i], data["mu"][i]])
    for rep in range(5):
        for i in order[4000:]:
            writer.writerow([i, "test", rep, data["rho"][i], data["mu"][i]])
