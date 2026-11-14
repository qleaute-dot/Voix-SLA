# usage: gen_vox.py items.json outdir  -- VoxCPM2 sans entraînement, 3 prises par phrase
# prise 0 : mode « clonage ultime » (extrait + son texte, pour l'accent et l'intonation) + référence de timbre
# prise 1 : référence de timbre seule ; prise 2 : autre extrait-modèle (c035)
import sys, os, json, time, torch, numpy as np, soundfile as sf
torch.set_num_threads(4)
from voxcpm import VoxCPM
items, out = json.load(open(sys.argv[1])), sys.argv[2]; os.makedirs(out, exist_ok=True)
D = "/root/voix/ds/wavs24/"
TX = {x["fichier"]: x["texte"] for x in json.load(open("/root/voix/ds/dataset.json"))["train"]}
TX["w000.wav"] = "Brièvement ? Attends, je n'ai pas entendu l'édition."
REF = D + "c058.wav"
m = VoxCPM.from_pretrained("/root/vxm", load_denoiser=False, optimize=False, device="cpu")
for it in items:
    for k in range(3):
        f = f"{out}/{it['id']}_{k}.wav"
        if os.path.exists(f): continue
        torch.manual_seed(11 + k); t = time.time()
        pr = ["c064.wav", None, "c035.wav"][k]
        kw = dict(prompt_wav_path=D + pr, prompt_text=TX[pr]) if pr else {}
        w = m.generate(text=it["texte"], reference_wav_path=REF, cfg_value=2.0, inference_timesteps=10, **kw)
        w = np.asarray(w, dtype="float32"); w = w / (np.abs(w).max() or 1) * 0.89
        sf.write(f, w, m.tts_model.sample_rate); print("gen", it["id"], k, round(time.time() - t, 1), flush=True)
