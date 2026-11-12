# usage: gen_cbx.py items.json outdir ntakes exaggeration cfg
import sys, os, json, time, torch, librosa, numpy as np, soundfile as sf
torch.set_num_threads(4)
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
from chatterbox.models.s3tokenizer import S3_SR
items, out, n, exag, cfg = json.load(open(sys.argv[1])), sys.argv[2], int(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
os.makedirs(out, exist_ok=True)
refs = json.load(open("/root/voix/refs_gardees.json"))
m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
main = refs[int(np.argmax([sf.info(r).duration for r in refs]))]
m.prepare_conditionals(main, exaggeration=exag)
ve = torch.from_numpy(m.ve.embeds_from_wavs([librosa.load(r, sr=S3_SR)[0] for r in refs], sample_rate=S3_SR)).mean(axis=0, keepdim=True)
m.conds.t3.speaker_emb = ve
for it in items:
    for k in range(n):
        f = f"{out}/{it['id']}_{k}.wav"
        if os.path.exists(f): continue
        torch.manual_seed(1000 * k + 7)
        t = time.time()
        w = m.generate(it["texte"], language_id="fr", exaggeration=exag, cfg_weight=cfg, temperature=0.75).squeeze().numpy()
        sf.write(f, w / (np.abs(w).max() or 1) * 0.89, m.sr)
        print("gen", it["id"], k, round(time.time() - t, 1), flush=True)
