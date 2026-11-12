# Repère rires, soupirs, toux… dans l'enregistrement (classifieur AudioSet AST)
import json, numpy as np, soundfile as sf, librosa, torch
from transformers import AutoFeatureExtractor, ASTForAudioClassification
torch.set_num_threads(2)
M = "MIT/ast-finetuned-audioset-10-10-0.4593"
fe = AutoFeatureExtractor.from_pretrained(M); m = ASTForAudioClassification.from_pretrained(M).eval()
lab = m.config.id2label
WANT = {k: v for k, v in lab.items() if any(w in v for w in ["Laughter", "Chuckle", "Giggle", "Sigh", "Cough", "Throat clearing", "Humming", "Whistling", "Snicker", "Belly laugh", "Breathing"])}
x, sr = librosa.load("/root/voix/travail/enregistrement_nettoye.wav", sr=16000)
win, hop = 16000 * 1, 8000
res = []
with torch.no_grad():
    for s in range(0, len(x) - win, hop):
        inp = fe(x[s:s + win], sampling_rate=16000, return_tensors="pt")
        p = torch.sigmoid(m(**inp).logits)[0]
        top = {lab[k]: float(p[k]) for k in WANT if p[k] > 0.15}
        if top: res.append({"t": s / 16000, "sons": top, "speech": float(p[[k for k, v in lab.items() if v == "Speech"][0]])})
json.dump(res, open("/root/voix/travail/sons.json", "w"), indent=1)
for r in res: print(round(r["t"], 1), {k: round(v, 2) for k, v in r["sons"].items()}, "parole", round(r["speech"], 2))
print("SONSFINI", len(res))
