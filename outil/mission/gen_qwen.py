# usage: gen_qwen.py items.json outdir ntakes ref.wav "ref text" [modele]
import sys, os, json, time, torch, numpy as np, soundfile as sf
torch.set_num_threads(2)
from qwen_tts import Qwen3TTSModel
items, out, n, ref, reftxt = json.load(open(sys.argv[1])), sys.argv[2], int(sys.argv[3]), sys.argv[4], sys.argv[5]
M = sys.argv[6] if len(sys.argv) > 6 else "Qwen/Qwen3-TTS-12Hz-0.6B-Base"
os.makedirs(out, exist_ok=True)
t = time.time()
m = Qwen3TTSModel.from_pretrained(M, device_map="cpu", dtype=torch.float32)
print("charge", round(time.time() - t), m.get_supported_languages(), flush=True)
prompt = m.create_voice_clone_prompt(ref_audio=ref, ref_text=reftxt)
for it in items:
    for k in range(n):
        f = f"{out}/{it['id']}_{k}.wav"
        if os.path.exists(f): continue
        torch.manual_seed(1000 * k + 7); t = time.time()
        wavs, sr = m.generate_voice_clone(text=it["texte"], language="French", voice_clone_prompt=prompt)
        w = np.asarray(wavs[0], dtype="float32"); w = w / (np.abs(w).max() or 1) * 0.89
        sf.write(f, w, sr); print("gen", it["id"], k, round(time.time() - t, 1), flush=True)
