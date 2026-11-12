# Construit le dossier publi/comparer : vraies phrases + clones, manifest
import json, os, subprocess, glob
S = "/tmp/claude-0/-home-user-Voix-SLA/1c69338f-3c8e-524c-9834-35b5bd9a198c/scratchpad/publi/comparer"
os.makedirs(S + "/vrai", exist_ok=True)
VERSIONS = json.load(open("/root/voix/pipe/cmp_versions.json"))  # [{dir, tag, nom, map?}]
items = {x["id"]: x["texte"] for x in json.load(open("/root/voix/pipe/cmp_items.json"))}
def mp3(src, dst):
    if not os.path.exists(dst):
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-ac", "1", "-b:a", "64k", dst], check=True)
paires = []
for v in VERSIONS:
    os.makedirs(f"{S}/{v['tag']}", exist_ok=True)
    for f in sorted(glob.glob(f"{v['dir']}/*_0.wav")):
        k = os.path.basename(f).rsplit("_", 1)[0]
        cid = v.get("map", {}).get(k, k)
        if cid not in items: continue
        mp3(f"/root/voix/ds/wavs24/{cid}.wav", f"{S}/vrai/{cid}.mp3")
        mp3(f, f"{S}/{v['tag']}/{cid}.mp3")
        paires.append({"id": f"{v['tag']}-{cid}", "texte": items[cid], "vrai": f"vrai/{cid}.mp3",
                       "clone": f"{v['tag']}/{cid}.mp3", "version": v["tag"], "nomVersion": v["nom"]})
json.dump({"paires": paires}, open(S + "/manifest.json", "w"), ensure_ascii=False, indent=1)
files = {}
for root, _, fs in os.walk(S):
    for x in fs:
        rel = os.path.relpath(os.path.join(root, x), os.path.dirname(S))
        files[rel] = rel
json.dump(files, open("/root/voix/pipe/publi_files.json", "w"))
print(len(paires), "paires", len(files), "fichiers")
