import importlib.util
from pathlib import Path

root = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("simulacion", root / "simulacion_observabilidad.py")
simulacion = importlib.util.module_from_spec(spec)
spec.loader.exec_module(simulacion)
simulacion.N = 5000
simulacion.OUT = Path(__file__).resolve().parent
simulacion.main()
