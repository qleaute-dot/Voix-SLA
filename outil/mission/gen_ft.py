# usage: gen_ft.py checkpoint.pth items.json outdir ntakes temperature
import sys, os, json, glob, time, torch, numpy as np, soundfile as sf
os.environ["COQUI_TOS_AGREED"] = "1"
torch.set_num_threads(4)
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
ck, items, out, n, temp = sys.argv[1], json.load(open(sys.argv[2])), sys.argv[3], int(sys.argv[4]), float(sys.argv[5])
X = glob.glob("/root/.cache/huggingface/hub/models--tts-hub--XTTS-v2/snapshots/*/")[0]
cfg = XttsConfig(); cfg.load_json(X + "config.json")
m = Xtts.init_from_config(cfg)
m.load_checkpoint(cfg, checkpoint_dir=X, checkpoint_path=ck, vocab_path=X + "vocab.json", use_deepspeed=False)
m.eval()
refs = json.load(open(os.environ.get("REFS", "/root/voix/refs_gardees.json")))
SPEED = float(os.environ.get("SPEED", "1.0"))
gpt, spk = m.get_conditioning_latents(audio_path=refs, gpt_cond_len=30, gpt_cond_chunk_len=6, max_ref_length=30)
os.makedirs(out, exist_ok=True)
for it in items:
    for k in range(n):
        f = f"{out}/{it['id']}_{k}.wav"
        if os.path.exists(f): continue
        torch.manual_seed(1000 * k + 7 + int(os.environ.get("SEEDOFF", "0"))); t = time.time()
        o = m.inference(it["texte"], "fr", gpt, spk, temperature=temp, repetition_penalty=5.0, top_p=0.85, speed=SPEED, enable_text_splitting=False)
        w = np.asarray(o["wav"], dtype="float32"); w = w / (np.abs(w).max() or 1) * 0.89
        sf.write(f, w, 24000); print("gen", it["id"], k, round(time.time() - t, 1), flush=True)
