# Panel des variantes de diction (toutes passées dans Applio époque 20)
import json, glob, os, subprocess
V = "/root/voix"; B = f"{V}/var/rvc"
P = "/tmp/claude-0/-home-user-Voix-SLA/1c69338f-3c8e-524c-9834-35b5bd9a198c/scratchpad/publi/comparer"
items = {x["id"]: x["texte"] for x in json.load(open(f"{V}/pipe/var_items.json"))}
NOMS = {"v_ep5": "Diction A · réglage de référence", "v_ep3": "Diction B · entraînement plus léger",
        "v_long": "Diction C · modèle d'intonation long", "v_expr": "Diction D · plus expressive", "v_lent": "Diction E · plus posée"}
wavs = {t: sorted(glob.glob(f"{B}/{t}/*_0.wav")) for t in NOMS}
allw = [w for v in wavs.values() for w in v]
json.dump(allw, open(f"{V}/pipe/pv_wavs.json", "w"))
subprocess.run(f"cd {V} && xtts/bin/python pipe/score_sim.py pipe/pv_wavs.json pipe/pv_sim.json > /dev/null 2>&1", shell=True)
sim = json.load(open(f"{V}/pipe/pv_sim.json"))
moy = {t: round(100 * sum(sim[w] for w in ws) / len(ws)) for t, ws in wavs.items() if ws}
files = {"comparer/manifest.json": "comparer/manifest.json"}; paires = []
for cid in items:  # regroupé par phrase : on compare les dictions sur la même phrase
    for t in NOMS:
        w = f"{B}/{t}/{cid}_0.wav"
        if not os.path.exists(w): continue
        os.makedirs(f"{P}/{t}", exist_ok=True)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", w, "-ac", "1", "-b:a", "80k", f"{P}/{t}/{cid}.mp3"], check=True)
        files[f"comparer/{t}/{cid}.mp3"] = f"comparer/{t}/{cid}.mp3"
        paires.append({"id": f"{t}-{cid}", "texte": items[cid], "vrai": f"vrai/{cid}.mp3", "clone": f"{t}/{cid}.mp3",
                       "version": t, "nomVersion": f"{NOMS[t]} · timbre {round(100*sim[w])}/100"})
m = json.load(open(f"{P}/manifest.json"))
keep = [p for p in m["paires"] if p["version"] in ("xA", "ft5", "qz")]
json.dump({"paires": paires + keep, "resume": moy}, open(f"{P}/manifest.json", "w"), ensure_ascii=False, indent=1)
json.dump(files, open(f"{V}/pipe/pv_files.json", "w"))
print(moy, len(paires), "paires", len(files), "fichiers")
