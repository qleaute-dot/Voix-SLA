# usage: gen_f5.py items.json outdir ntakes ref.wav "ref text" [ckpt] [vocab]
import sys, os, json, time, torch
torch.set_num_threads(4)
from f5_tts.api import F5TTS
items, out, n, ref, reftxt = json.load(open(sys.argv[1])), sys.argv[2], int(sys.argv[3]), sys.argv[4], sys.argv[5]
H = "/root/.cache/huggingface/hub/models--RASPIAUDIO--F5-French-MixedSpeakers-reduced/snapshots/bcad6ae266c8406dc572b33d1d6ffced4db114fe/"
ckpt = sys.argv[6] if len(sys.argv) > 6 else H + "model_last_reduced.pt"
vocab = sys.argv[7] if len(sys.argv) > 7 else H + "vocab.txt"
os.makedirs(out, exist_ok=True)
tts = F5TTS(model="F5TTS_Base", ckpt_file=ckpt, vocab_file=vocab, device="cpu")
for it in items:
    for k in range(n):
        f = f"{out}/{it['id']}_{k}.wav"
        if os.path.exists(f): continue
        t = time.time()
        tts.infer(ref, reftxt, it["texte"], file_wave=f, seed=1000 * k + 7, nfe_step=32, show_info=lambda *a: None, progress=None)
        print("gen", it["id"], k, round(time.time() - t, 1), flush=True)
