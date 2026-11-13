# Tri strict : fenêtres de 1 s (pas 0,25 s) sur chaque extrait ; on ne garde que les portions continues
# où TOUTES les fenêtres ressemblent à sa voix (seuil = 5e centile des fenêtres de ses phrases connues).
import sys, os, json, subprocess, numpy as np, soundfile as sf, torch, torchaudio
os.environ["VOIX_PAPA_DOSSIER"] = "/root/voix/travail"; os.environ["COQUI_TOS_AGREED"] = "1"
sys.path.insert(0, "/home/user/Voix-SLA/outil"); import voix_papa as vp
torch.set_num_threads(4); m = vp.Voix._modele()
x, sr = sf.read("/root/voix/video/son24.wav", dtype="float32")
x16 = torchaudio.functional.resample(torch.tensor(x)[None], sr, 16000)[0]
def emb(a, b):
    e = m.hifigan_decoder.speaker_encoder.forward(x16[int(a*16000):int(b*16000)][None], l2_norm=True).squeeze().detach().numpy()
    return e / np.linalg.norm(e)
U = json.load(open("/root/voix/video/unites.json"))
known = [u for u in U if u["old"]]
cv = np.mean([emb(u["a"], u["b"]) for u in known], 0); cv /= np.linalg.norm(cv)
def wins(a, b):
    t = np.arange(a, max(a + 0.01, b - 2.0) + 1e-6, 0.5)
    return [(s, float(emb(s, min(b, s + 2.0)) @ cv)) for s in t]
kw = [s for u in known if u["b"] - u["a"] >= 2.5 for _, s in wins(u["a"], u["b"])]
seuil = float(np.percentile(kw, 10)); print("fenêtres de ses phrases connues : p5 %.3f p50 %.3f p10 -> seuil %.3f" % (np.percentile(kw, 5), np.median(kw), seuil))
T = json.load(open("/root/voix/video/transcription.json"))
words = [w for s in T for w in s["words"]]
ds = json.load(open("/root/voix/video/ds_video.json")); out = []; perdu = 0
for o in ds:
    a = o["debut"]; b = a + o["duree"]; W = wins(a, b)
    ok = np.zeros(int(round((b - a) * 100)) + 1, bool)   # au centième de seconde : couvert seulement par des fenêtres valides
    bad = np.zeros_like(ok)
    for s, v in W:
        i, j = int((s - a) * 100), int((min(b, s + 2.0) - a) * 100)
        (ok if v >= seuil else bad)[i:j + 1] = True
    good = ok & ~bad
    runs, i = [], 0
    while i < len(good):
        if good[i]:
            j = i
            while j < len(good) and good[j]: j += 1
            runs.append((a + i / 100, a + j / 100)); i = j
        else: i += 1
    for ra, rb in runs:
        ws = [w for w in words if w["s"] >= ra - 0.05 and w["e"] <= rb + 0.05]
        if not ws: continue
        ca, cb = max(ra, ws[0]["s"] - 0.1), min(rb, ws[-1]["e"] + 0.15)
        if cb - ca < 1.5: continue
        out.append({"debut": round(ca, 2), "duree": round(cb - ca, 2), "texte": "".join(w["w"] for w in ws).strip(), "de": o["fichier"]})
    perdu += o["duree"] - sum(r["duree"] for r in out if r["de"] == o["fichier"])
for i, r in enumerate(out):
    n = f"w{i:03d}"; r["fichier"] = n + ".wav"
    sf.write(f"/root/voix/ds/wavs24/{n}.wav", x[int(r['debut']*sr):int((r['debut']+r['duree'])*sr)], sr)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", f"/root/voix/ds/wavs24/{n}.wav", "-ar", "22050", f"/root/voix/ds/wavs22/{n}.wav"], check=True)
json.dump(out, open("/root/voix/video/ds_strict.json", "w"), ensure_ascii=False, indent=0)
base = [l for l in open("/root/voix/ds/train.csv").read().rstrip("\n").split("\n")]
with open("/root/voix/ds/train_w.csv", "w") as f:
    f.write("\n".join(base) + "\n" + "".join(f"wavs22/{r['fichier']}|{r['texte']}|papa\n" for r in out))
print(len(ds), "extraits ->", len(out), "extraits stricts,", round(sum(r["duree"] for r in out) / 60, 2), "min (perdu %.0f s)" % perdu)
