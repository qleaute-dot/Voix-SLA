# Ses vraies paroles : phrases réelles découpées large (rires, respirations conservés)
import json, os, subprocess, numpy as np, soundfile as sf
T = json.load(open("/root/voix/travail/transcription.json"))
audio, sr = sf.read("/root/voix/travail/enregistrement_nettoye.wav", dtype="float32")
segs = [s for s in T if s["words"]]
out = "/tmp/claude-0/-home-user-Voix-SLA/1c69338f-3c8e-524c-9834-35b5bd9a198c/scratchpad/publi/vraies"
os.makedirs(out, exist_ok=True)
# regroupe les segments en passages de 3 à 15 s, coupés dans les silences
groups, cur = [], []
for s in segs:
    if cur and (s["end"] - cur[0]["start"] > 15 or s["start"] - cur[-1]["end"] > 1.2):
        groups.append(cur); cur = []
    cur.append(s)
if cur: groups.append(cur)
items = []
for i, g in enumerate(groups):
    a, b = g[0]["start"], g[-1]["end"]
    if b - a < 2.5: continue
    txt = " ".join(s["text"] for s in g).strip()
    if "Daudet" in txt or "rue" in txt.lower().split(): continue  # adresse : jamais publiée
    # marges larges : jusqu'au milieu du silence voisin (max 0,6 s)
    pa = max(0, a - 0.6); pb = min(len(audio) / sr, b + 0.6)
    x = audio[int(pa * sr): int(pb * sr)].copy(); f = int(sr * 0.03)
    x[:f] *= np.linspace(0, 1, f); x[-f:] *= np.linspace(1, 0, f)
    n = f"v{i:03d}.mp3"
    sf.write("/tmp/v.wav", x, sr)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", "/tmp/v.wav", "-ac", "1", "-b:a", "96k", f"{out}/{n}"], check=True)
    items.append({"id": n[:-4], "texte": txt, "fichier": n, "duree": round(pb - pa, 1)})
json.dump({"passages": items}, open(f"{out}/manifest.json", "w"), ensure_ascii=False, indent=1)
print(len(items), "passages", round(sum(x["duree"] for x in items)), "s")
