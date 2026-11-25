from pathlib import Path
import zipfile

import numpy as np
from scipy import signal


ROOT = Path(__file__).resolve().parent
ZIP = ROOT.parents[3] / "references/tfm/datos_udp.zip"
with zipfile.ZipFile(ZIP) as archive:
    for name in sorted(archive.namelist()):
        if not name.endswith(".csv"):
            continue
        with archive.open(name) as stream:
            data = np.genfromtxt(stream, delimiter=",", names=True)
        t = (data["t_ms"]-data["t_ms"][0])/1000
        delta = np.diff(t)
        positive = delta[delta > 0]
        freq, power = signal.welch(
            data["ang_deg"], fs=1/np.median(positive),
            nperseg=min(2048, len(t)),
        )
        mask = (freq >= .3) & (freq <= 5)
        peak = freq[mask][np.argmax(power[mask])]
        std = [
            np.std(data["ang_deg"][(t>=a)&(t<a+5)])
            for a in (0, 5, 10, 15, 25, 50)
        ]
        print(
            Path(name).name, "t", round(t[-1], 1),
            "dt", round(np.median(positive), 4),
            "bad", np.count_nonzero(delta<=0),
            "gaps", np.count_nonzero(delta>.03),
            "f", round(peak, 3),
            "std_0,5,10,15,25,50", *[round(x, 3) for x in std]
        )
