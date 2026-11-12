# usage: gen_xtts.py items.json outdir ntakes temperature
import sys, os, json, time, torch
os.environ["VOIX_PAPA_DOSSIER"] = "/root/voix/travail"; os.environ["COQUI_TOS_AGREED"] = "1"
sys.path.insert(0, "/home/user/Voix-SLA/outil")
import voix_papa as vp, soundfile as sf
torch.set_num_threads(4)
items, out, n, temp = json.load(open(sys.argv[1])), sys.argv[2], int(sys.argv[3]), float(sys.argv[4])
os.makedirs(out, exist_ok=True)
v = vp.Voix.charger()
for it in items:
    for k in range(n):
        f = f"{out}/{it['id']}_{k}.wav"
        if os.path.exists(f): continue
        torch.manual_seed(1000 * k + 7)
        t = time.time(); sf.write(f, v.dire(it["texte"], temperature=temp), vp.SR)
        print("gen", it["id"], k, round(time.time() - t, 1), flush=True)
