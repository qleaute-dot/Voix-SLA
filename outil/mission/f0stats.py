# Statistiques de mélodie (F0, demi-tons) : étendue, pente finale, débit
import sys, json, glob, numpy as np, parselmouth
def st(f):
    s = parselmouth.Sound(f); p = s.to_pitch(time_step=0.01, pitch_floor=70, pitch_ceiling=300)
    f0 = p.selected_array['frequency']; v = f0[f0 > 0]
    if len(v) < 20: return None
    sem = 12*np.log2(v/100.0)
    tail = sem[-max(5,len(sem)//6):]; head = sem[:len(sem)//2]
    return dict(med=float(np.median(v)), sd=float(np.std(sem)), rng=float(np.percentile(sem,95)-np.percentile(sem,5)),
                fin=float(np.median(tail)-np.median(sem)), dur=s.duration, vfrac=len(v)/len(f0))
res = {}
for f in sys.argv[2:]:
    for g in sorted(glob.glob(f)):
        r = st(g)
        if r: res[g] = r
json.dump(res, open(sys.argv[1], "w"), indent=0)
a = np.array([[r['med'], r['sd'], r['rng'], r['fin']] for r in res.values()])
print(len(res), "med %.0f Hz  sd %.2f st  rng %.1f st  fin %.2f st" % tuple(a.mean(0)))
