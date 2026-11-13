# Assemble les phrases de papa trouvées dans la vidéo (sim >= 0.55, nouvelles) en extraits d'entraînement
import json, os, subprocess, soundfile as sf
U = sorted([u for u in json.load(open("/root/voix/video/unites.json")) if not u["old"] and u["sim"] >= 0.55], key=lambda u: u["a"])
x, sr = sf.read("/root/voix/video/son24.wav", dtype="float32")
G, cur = [], []
for u in U:
    if cur and (u["a"] - cur[-1]["b"] > 0.8 or u["b"] - cur[0]["a"] > 12): G.append(cur); cur = []
    cur.append(u)
if cur: G.append(cur)
os.makedirs("/root/voix/ds/wavs24", exist_ok=True); os.makedirs("/root/voix/ds/wavs22", exist_ok=True)
out = []
for i, g in enumerate(G):
    a, b = max(0, g[0]["a"] - 0.12), g[-1]["b"] + 0.18
    if b - a < 1.5: continue
    t = " ".join(u["texte"] for u in g)
    n = f"v{i:03d}"; f24 = f"/root/voix/ds/wavs24/{n}.wav"
    sf.write(f24, x[int(a * sr):int(b * sr)], sr)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", f24, "-ar", "22050", f"/root/voix/ds/wavs22/{n}.wav"], check=True)
    out.append({"fichier": f"{n}.wav", "texte": t, "duree": round(b - a, 2), "sim": round(min(u["sim"] for u in g), 3), "debut": round(a, 1)})
json.dump(out, open("/root/voix/video/ds_video.json", "w"), ensure_ascii=False, indent=0)
base = open("/root/voix/ds/train.csv").read().rstrip("\n").split("\n")
with open("/root/voix/ds/train_v.csv", "w") as f:
    f.write("\n".join(base) + "\n")
    for o in out: f.write(f"wavs22/{o['fichier']}|{o['texte']}|papa\n")
print(len(out), "extraits,", round(sum(o["duree"] for o in out) / 60, 1), "min ajoutées ; train_v.csv :", len(base) - 1 + len(out), "lignes")
