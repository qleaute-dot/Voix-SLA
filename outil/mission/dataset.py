# Construit le jeu de données (phrases de papa + texte) à partir de la transcription
import json, os, numpy as np, soundfile as sf, librosa, random
T = json.load(open("/root/voix/travail/transcription.json"))
audio, sr = sf.read("/root/voix/travail/enregistrement_nettoye.wav", dtype="float32")
words = [w for s in T for w in s["words"]]
clips, cur = [], []
def flush():
    global cur
    if cur:
        a, b = cur[0]["s"], cur[-1]["e"]
        if 2.5 <= b - a <= 11.0:
            txt = "".join(w["w"] for w in cur).strip()
            p = float(np.mean([w["p"] for w in cur]))
            clips.append({"s": a, "e": b, "texte": txt, "p": p})
    cur = []
for i, w in enumerate(words):
    if cur:
        gap = w["s"] - cur[-1]["e"]; dur = w["e"] - cur[0]["s"]
        end_sent = cur[-1]["w"].strip()[-1:] in ".?!"
        if dur > 11.0 or (gap > 0.6) or (end_sent and cur[-1]["e"] - cur[0]["s"] > 3) or (gap > 0.3 and cur[-1]["e"] - cur[0]["s"] > 7):
            flush()
    cur.append(w)
flush()
clips = [c for c in clips if c["p"] >= 0.6]
random.seed(3)
# phrases de test : 5 phrases nettes de 3,5 à 8 s, réparties dans l'enregistrement
cand = [c for c in clips if 3.5 <= c["e"] - c["s"] <= 8 and c["p"] > 0.85]
test = [cand[i] for i in np.linspace(0, len(cand) - 1, 5).astype(int)]
for d in ["/root/voix/ds/wavs22", "/root/voix/ds/wavs24"]: os.makedirs(d, exist_ok=True)
tr, te = [], []
for i, c in enumerate(clips):
    a = max(0, int((c["s"] - 0.08) * sr)); b = min(len(audio), int((c["e"] + 0.12) * sr))
    x = audio[a:b].copy(); f = int(sr * 0.01); x[:f] *= np.linspace(0, 1, f); x[-f:] *= np.linspace(1, 0, f)
    n = f"c{i:03d}.wav"
    sf.write(f"/root/voix/ds/wavs24/{n}", x, sr)
    sf.write(f"/root/voix/ds/wavs22/{n}", librosa.resample(x, orig_sr=sr, target_sr=22050), 22050)
    row = {"fichier": n, "texte": c["texte"], "duree": round(c["e"] - c["s"], 2)}
    (te if c in test else tr).append(row)
json.dump({"train": tr, "test": te}, open("/root/voix/ds/dataset.json", "w"), ensure_ascii=False, indent=1)
for name, rows in [("train", tr), ("eval", te)]:
    with open(f"/root/voix/ds/{name}.csv", "w") as f:
        f.write("audio_file|text|speaker_name\n")
        for r in rows: f.write(f"wavs22/{r['fichier']}|{r['texte']}|papa\n")
print(len(tr), "train", round(sum(r["duree"] for r in tr)), "s |", len(te), "test")
for r in te: print("TEST", r)
