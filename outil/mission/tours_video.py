# Découpe fine (phrase par phrase, à chaque segment Whisper et ponctuation) puis reconnaissance de la voix de papa
# sur chaque morceau, par rapport à son centre de voix DANS la vidéo (extraits déjà connus = doublons).
import sys, os, re, json, difflib, numpy as np, soundfile as sf, torch, torchaudio
os.environ["VOIX_PAPA_DOSSIER"] = "/root/voix/travail"; os.environ["COQUI_TOS_AGREED"] = "1"
sys.path.insert(0, "/home/user/Voix-SLA/outil"); import voix_papa as vp
torch.set_num_threads(4); m = vp.Voix._modele()
x, sr = sf.read("/root/voix/video/son24.wav", dtype="float32")
x16 = torchaudio.functional.resample(torch.tensor(x)[None], sr, 16000)[0]
def emb_t(a, b):
    seg = x16[int(a * 16000):int(b * 16000)][None]
    e = m.hifigan_decoder.speaker_encoder.forward(seg, l2_norm=True).squeeze().detach().numpy(); return e / np.linalg.norm(e)
T = json.load(open("/root/voix/video/transcription.json"))
units = []
for s in T:
    if s["avg_logprob"] < -0.9 or s["no_speech"] > 0.5: continue
    cur = []
    for w in s["words"]:
        cur.append(w)
        if w["w"].strip()[-1:] in ".?!" and cur[-1]["e"] - cur[0]["s"] >= 1.0: units.append(cur); cur = []
    if cur: units.append(cur)
units = [u for u in units if u[-1]["e"] - u[0]["s"] >= 1.0]
ds = json.load(open("/root/voix/ds/dataset.json")); anciens = [(c["fichier"][:-4], c["texte"]) for c in ds["train"] + ds["test"]]
def best_old(t):
    b = max(anciens, key=lambda a: difflib.SequenceMatcher(None, a[1].lower(), t.lower()).ratio())
    return b[0], difflib.SequenceMatcher(None, b[1].lower(), t.lower()).ratio()
U = []
for u in units:
    t = "".join(w["w"] for w in u).strip(); a, b = u[0]["s"], u[-1]["e"]
    o, r = best_old(t)
    U.append({"a": a, "b": b, "texte": t, "p": float(np.mean([w["w"] and w["p"] for w in u])), "old": o if r > 0.55 else None, "e": emb_t(a, b)})
known = [k["e"] for k in U if k["old"]]
cv = np.mean(known, 0); cv /= np.linalg.norm(cv)
for k in U: k["sim"] = float(k["e"] @ cv)
sk = np.array([k["sim"] for k in U if k["old"]]); su = np.array([k["sim"] for k in U if not k["old"]])
print(len(U), "phrases ;", len(known), "déjà connues (papa). Sim connues p10/50 :", np.round(np.percentile(sk, [10, 50]), 3))
print("Sim nouvelles :", np.histogram(su, bins=[-1, .3, .4, .5, .55, .6, .65, .7, .8, 1])[0].tolist())
json.dump([{k2: v for k2, v in k.items() if k2 != "e"} for k in U], open("/root/voix/video/unites.json", "w"), ensure_ascii=False, indent=0)
