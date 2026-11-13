# Garde les extraits de la vidéo dont la voix ressemble à celle de papa (encodeur XTTS), seuil calé sur ses vrais extraits
import sys, os, json, glob, torch, torchaudio, numpy as np, soundfile as sf
os.environ["VOIX_PAPA_DOSSIER"] = "/root/voix/travail"; os.environ["COQUI_TOS_AGREED"] = "1"
sys.path.insert(0, "/home/user/Voix-SLA/outil")
import voix_papa as vp
torch.set_num_threads(4)
m = vp.Voix._modele()
def emb(path):
    x, sr = sf.read(path, dtype="float32")
    if x.ndim > 1: x = x.mean(1)
    x = torchaudio.functional.resample(torch.tensor(x)[None], sr, 16000)
    e = m.hifigan_decoder.speaker_encoder.forward(x, l2_norm=True).squeeze().detach().numpy()
    return e / np.linalg.norm(e)
refs = json.load(open("/root/voix/refs_gardees.json"))
c = np.mean([emb(r) for r in refs], 0); c /= np.linalg.norm(c)
vrais = sorted(glob.glob("/root/voix/ds/wavs24/c*.wav"))
sv = np.array([emb(f) @ c for f in vrais])
clips = json.load(open("/root/voix/video/clips.json"))
for k in clips: k["sim"] = round(float(emb(k["fichier"]) @ c), 4)
seuil = float(np.percentile(sv, 5)) - 0.03
print("papa : min %.3f p5 %.3f médiane %.3f ; seuil %.3f" % (sv.min(), np.percentile(sv, 5), np.median(sv), seuil))
h = np.histogram([k["sim"] for k in clips], bins=[-1, .3, .4, .5, .6, .65, .7, .75, .8, .85, 1])
print("histogramme vidéo :", list(zip([round(b, 2) for b in h[1][:-1]], h[0].tolist())))
for k in clips: k["papa"] = k["sim"] >= seuil
json.dump(clips, open("/root/voix/video/clips.json", "w"), ensure_ascii=False, indent=0)
g = [k for k in clips if k["papa"]]
print(len(g), "/", len(clips), "extraits gardés,", round(sum(k["duree"] for k in g) / 60, 1), "min")
