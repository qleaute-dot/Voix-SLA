# F5-TTS au vol : chaque prise k utilise la référence k de l'item (extrait de sa vraie voix + texte)
# usage: gen_f5b.py items.json outdir [ckpt] [vocab]
import sys, os, json, time, torch
torch.set_num_threads(4)
from f5_tts.api import F5TTS
items, out = json.load(open(sys.argv[1])), sys.argv[2]
H = "/root/.cache/huggingface/hub/models--RASPIAUDIO--F5-French-MixedSpeakers-reduced/snapshots/bcad6ae266c8406dc572b33d1d6ffced4db114fe/"
ckpt = sys.argv[3] if len(sys.argv) > 3 else H + "model_last_reduced.pt"
vocab = sys.argv[4] if len(sys.argv) > 4 else H + "vocab.txt"
os.makedirs(out, exist_ok=True)
tts = F5TTS(model="F5TTS_Base", ckpt_file=ckpt, vocab_file=vocab, device="cpu")
for it in items:
    for k, (ref, rt) in enumerate(it["refs"]):
        f = f"{out}/{it['id']}_{k}.wav"
        if os.path.exists(f): continue
        t = time.time()
        tts.infer(ref, rt, it["texte"], file_wave=f, seed=1000 * k + 7, nfe_step=32, show_info=lambda *a: None, progress=None)
        print("gen", it["id"], k, round(time.time() - t, 1), flush=True)
