# Construit le panel Comparer : toutes les variantes disponibles, mesurées, meilleures en tête
import json, glob, os, subprocess, collections
V = "/root/voix"
P = "/tmp/claude-0/-home-user-Voix-SLA/1c69338f-3c8e-524c-9834-35b5bd9a198c/scratchpad/publi/comparer"
items = {x["id"]: x["texte"] for x in json.load(open(f"{V}/pipe/cmp_items.json"))}
fils_txt = {"f04": "Bonjour ! Je suis content de vous voir.", "f05": "J'ai besoin d'aide, s'il vous plaît.", "f06": "Je vous aime. Merci d'être là."}
import sys
last = int(sys.argv[1]) if len(sys.argv) > 1 else sorted([int(d.split("/e")[-1]) for d in glob.glob(f"{V}/rvcout/e*")] or [0])[-1]
E = f"{V}/rvcout/e{last}"
VARS = [  # tag, dossier, nom
 ("fA", f"{E}/fils", "Ta voix + Applio"),


 ("qA", f"{E}/qz", "Voix de synthèse + Applio"),


 ("xA", f"{E}/ft5", "Clone entraîné + Applio"),
]
wavs = {tag: sorted(glob.glob(d + "/*_0.wav")) for tag, d, _ in VARS}
allw = [w for v in wavs.values() for w in v]
json.dump(allw, open(f"{V}/pipe/panel_wavs.json", "w"))
subprocess.run(f"cd {V} && xtts/bin/python pipe/score_sim.py pipe/panel_wavs.json pipe/panel_sim.json > /dev/null 2>&1", shell=True)
sim = json.load(open(f"{V}/pipe/panel_sim.json"))
moy = {tag: round(100 * sum(sim[w] for w in ws) / len(ws)) for tag, ws in wavs.items() if ws}
order = sorted(moy, key=lambda t: -moy[t])
paires, files = [], {"comparer/manifest.json": "comparer/manifest.json"}
for tag in order:
    nom = dict((t, n) for t, _, n in VARS)[tag]
    os.makedirs(f"{P}/{tag}", exist_ok=True)
    for w in wavs[tag]:
        cid = os.path.basename(w)[:-6]
        dst = f"{P}/{tag}/{cid}.mp3"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", w, "-ac", "1", "-b:a", "80k", dst], check=True)
        files[f"comparer/{tag}/{cid}.mp3"] = f"comparer/{tag}/{cid}.mp3"
        has_real = cid in items
        if has_real and not os.path.exists(f"{P}/vrai/{cid}.mp3"):
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", f"{V}/ds/wavs24/{cid}.wav", "-ac", "1", "-b:a", "64k", f"{P}/vrai/{cid}.mp3"], check=True)
            files[f"comparer/vrai/{cid}.mp3"] = f"comparer/vrai/{cid}.mp3"
        paires.append({"id": f"{tag}-e{last}-{cid}", "texte": items.get(cid) or fils_txt.get(cid, cid), "vrai": f"vrai/{cid}.mp3" if has_real else None,
                       "clone": f"{tag}/{cid}.mp3", "version": tag, "nomVersion": f"{nom} · timbre {round(100*sim[w])}/100"})
m = json.load(open(f"{P}/manifest.json"))
keep = [p for p in m["paires"] if p["version"] in ("ft5", "qz")]
json.dump({"paires": paires + keep, "resume": {t: moy[t] for t in order}}, open(f"{P}/manifest.json", "w"), ensure_ascii=False, indent=1)
json.dump(files, open(f"{V}/pipe/panel_files.json", "w"))
print("epoque", last, {t: moy[t] for t in order}, len(paires), "paires", len(files), "fichiers")
