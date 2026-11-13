# Panel « Phrases nouvelles » : phrases inventées, sans original, 3 dictions + Applio
import json, os, subprocess
V = "/root/voix"; B = f"{V}/nv/rvc"
P = "/tmp/claude-0/-home-user-Voix-SLA/1c69338f-3c8e-524c-9834-35b5bd9a198c/scratchpad/publi/comparer"
items = json.load(open(f"{V}/pipe/nouvelles.json"))
NOMS = {"nA": "Phrase nouvelle · diction A (référence)", "nE": "Phrase nouvelle · diction E (posée)", "nAE": "Phrase nouvelle · diction A+E (référence un peu plus posée)"}
files = {"comparer/manifest.json": "comparer/manifest.json"}; paires = []
for it in items:
    for t, nom in NOMS.items():
        w = f"{B}/{t}/{it['id']}_0.wav"
        if not os.path.exists(w): continue
        os.makedirs(f"{P}/{t}", exist_ok=True)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", w, "-ac", "1", "-b:a", "80k", f"{P}/{t}/{it['id']}.mp3"], check=True)
        files[f"comparer/{t}/{it['id']}.mp3"] = f"comparer/{t}/{it['id']}.mp3"
        paires.append({"id": f"{t}-{it['id']}", "texte": it["texte"], "vrai": None, "clone": f"{t}/{it['id']}.mp3", "version": t, "nomVersion": nom})
m = json.load(open(f"{P}/manifest.json"))
keep = [p for p in m["paires"] if not p["version"].startswith("n")]
json.dump({"paires": paires + keep}, open(f"{P}/manifest.json", "w"), ensure_ascii=False, indent=1)
json.dump(files, open(f"{V}/pipe/nv_files.json", "w"))
print(len(paires), "paires", len(files), "fichiers")
