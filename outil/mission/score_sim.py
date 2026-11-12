# usage: score_sim.py wavs.json out.json  -> similarité au timbre de papa (encodeur XTTS)
import sys, os, json, torch, torchaudio, numpy as np, soundfile as sf
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
res = {f: round(float(emb(f) @ c), 4) for f in json.load(open(sys.argv[1]))}
json.dump(res, open(sys.argv[2], "w"), indent=1); print(json.dumps(res, indent=1))
