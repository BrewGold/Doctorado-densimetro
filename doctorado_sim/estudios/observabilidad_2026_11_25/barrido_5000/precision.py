import importlib.util
from pathlib import Path

import numpy as np
from scipy.interpolate import RBFInterpolator

root = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("simulacion", root.parent / "simulacion_observabilidad.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
data = np.genfromtxt(root / "dataset_observabilidad.csv", delimiter=",", skip_header=1)
split = np.random.RandomState(42).permutation(len(data))
train, test = split[:4000], split[4000:]
center, scale = data[train, :7].mean(axis=0), data[train, :7].std(axis=0)
scale[scale == 0] = 1
model = RBFInterpolator((data[train, :7] - center) / scale, data[train, 7:],
                        neighbors=30, kernel="thin_plate_spline", smoothing=1e-8)
selected = test[np.linspace(0, len(test) - 1, 30, dtype=int)]
precise = np.array([module.simulate(*data[i, 7:], rtol=1e-8, atol=1e-10, max_step=0.02)
                    for i in selected])
prediction = model((precise - center) / scale)
error = 100 * np.abs((prediction - data[selected, 7:]) / data[selected, 7:])
print("precise holdout MAPE rho/mu:", error.mean(axis=0))
print("precise holdout max error rho/mu:", error.max(axis=0))
