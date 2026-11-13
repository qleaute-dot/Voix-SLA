# Corrige la fin de phrase : la voix clonée remonte en fin de phrase (+2 demi-tons),
# papa termine à plat (0). On abaisse progressivement la mélodie sur la fin (Praat PSOLA),
# puis Applio refait le timbre à partir de cette mélodie.
# usage: melodie.py in.wav out.wav texte [cible_st]
import sys, numpy as np, parselmouth
from parselmouth.praat import call
fi, fo, txt = sys.argv[1], sys.argv[2], sys.argv[3]
cible = float(sys.argv[4]) if len(sys.argv) > 4 else -0.2
s = parselmouth.Sound(fi)
man = call(s, "To Manipulation", 0.01, 70, 300)
pt = call(man, "Extract pitch tier")
n = call(pt, "Get number of points")
ts = np.array([call(pt, "Get time from index", i + 1) for i in range(n)])
fs = np.array([call(pt, "Get value at index", i + 1) for i in range(n)])
sem = 12 * np.log2(fs / 100)
question = txt.strip().endswith("?")
tail = sem[ts >= ts[0] + 0.83 * (ts[-1] - ts[0])]
exces = np.median(tail) - (np.median(sem) + cible)
if question or exces < 0.4 or n < 20:
    s.save(fo, "WAV"); print("inchangé", round(float(exces), 2)); sys.exit()
t0 = ts[0] + 0.6 * (ts[-1] - ts[0])
r = np.clip((ts - t0) / (ts[-1] - t0) * 1.6, 0, 1)
new = 100 * 2 ** ((sem - exces * r) / 12)
call(pt, "Remove points between", 0, s.duration)
for t, f in zip(ts, new): call(pt, "Add point", float(t), float(f))
call([man, pt], "Replace pitch tier")
o = call(man, "Get resynthesis (overlap-add)")
o.save(fo, "WAV"); print("corrigé", round(float(exces), 2))
