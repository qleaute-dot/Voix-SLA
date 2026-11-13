# Découpe la transcription de la vidéo en extraits de 2 à 12 s, à partir des mots horodatés
import json, re, difflib, soundfile as sf, numpy as np, os
T = json.load(open("/root/voix/video/transcription.json"))
x, sr = sf.read("/root/voix/video/son24.wav", dtype="float32")
ds = json.load(open("/root/voix/ds/dataset.json"))
anciens = [(c["fichier"][:-4], c["texte"]) for c in ds["train"] + ds["test"]]
tests = {c["fichier"][:-4] for c in ds["test"]}
PRIVE = re.compile(r"\b(rue|avenue|boulevard|impasse|all[ée]e|daudet|alphonse|code postal|t[ée]l[ée]phone|num[ée]ro)\b", re.I)
words = []
for s in T:
    if s["avg_logprob"] < -0.9 or s["no_speech"] > 0.5: continue
    for w in s["words"]: words.append(w)
clips, cur = [], []
def flush():
    if cur and cur[-1]["e"] - cur[0]["s"] >= 2.0: clips.append(list(cur))
for w in words:
    if cur and (w["s"] - cur[-1]["e"] > 0.6 or w["e"] - cur[0]["s"] > 12.0 or
                (cur[-1]["w"].strip()[-1:] in ".?!" and w["e"] - cur[0]["s"] > 4.0)):
        flush(); cur = []
    cur.append(w)
flush()
os.makedirs("/root/voix/video/clips", exist_ok=True)
out, ex = [], {"prive": 0, "doublon": 0, "test": 0, "flou": 0}
for i, c in enumerate(clips):
    txt = "".join(w["w"] for w in c).strip()
    if PRIVE.search(txt): ex["prive"] += 1; continue
    if np.mean([w["p"] for w in c]) < 0.6: ex["flou"] += 1; continue
    best = max(anciens, key=lambda a: difflib.SequenceMatcher(None, a[1].lower(), txt.lower()).ratio())
    r = difflib.SequenceMatcher(None, best[1].lower(), txt.lower()).ratio()
    if r > 0.6:
        ex["test" if best[0] in tests else "doublon"] += 1; continue
    a, b = max(0, c[0]["s"] - 0.15), c[-1]["e"] + 0.2
    f = f"/root/voix/video/clips/v{i:04d}.wav"; sf.write(f, x[int(a * sr):int(b * sr)], sr)
    out.append({"fichier": f, "texte": txt, "debut": round(a, 2), "duree": round(b - a, 2)})
json.dump(out, open("/root/voix/video/clips.json", "w"), ensure_ascii=False, indent=0)
print(len(clips), "extraits ;", len(out), "gardés,", round(sum(o["duree"] for o in out) / 60, 1), "min ; écartés", ex)
