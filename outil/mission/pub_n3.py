# Panel n3 (20 phrases neuves) : versions à l'aveugle, ordre mélangé ; ajoute les versions disponibles
import json, os, subprocess, random, sys
V="/root/voix"; B=f"{V}/n3"; P="/tmp/claude-0/-home-user-Voix-SLA/1c69338f-3c8e-524c-9834-35b5bd9a198c/scratchpad/publi/comparer"
VERS=[("n3a","out_ft3","Version 1"),("n3b","out_ft2","Version 2"),("n3c","out_ft3b","Version 3"),("n3d","out_f5","Version 4")]
VERS=[v for v in VERS if os.path.isdir(f"{B}/{v[1]}") and len(os.listdir(f"{B}/{v[1]}"))>=20]
items=json.load(open(f"{V}/pipe/n3_items.json")); man=json.load(open(f"{P}/manifest.json"))
old=[p for p in man["paires"] if not p["version"].startswith("n3")]
files={"comparer/manifest.json":"comparer/manifest.json"}; new=[]; random.seed(3)
for it in items:
    grp=[]
    for vid,d,nom in VERS:
        os.makedirs(f"{P}/{vid}",exist_ok=True); dst=f"{P}/{vid}/{it['id']}.mp3"
        if not os.path.exists(dst): subprocess.run(["ffmpeg","-loglevel","error","-y","-i",f"{B}/{d}/{it['id']}_0.wav","-ac","1","-b:a","128k",dst],check=True)
        files[f"comparer/{vid}/{it['id']}.mp3"]=f"comparer/{vid}/{it['id']}.mp3"
        grp.append({"id":f"{vid}-{it['id']}","texte":it["texte"],"vrai":None,"clone":f"{vid}/{it['id']}.mp3","version":vid,"nomVersion":nom})
    random.shuffle(grp); new+=grp
man["paires"]=new+old; json.dump(man,open(f"{P}/manifest.json","w"),ensure_ascii=False,indent=0)
json.dump(files,open(f"{V}/pipe/n3_files.json","w")); print([v[0]+"="+v[1] for v in VERS], len(new), "paires")
