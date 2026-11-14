# Panel n4 : 8 phrases difficiles, 3 essais Version 3 (n4x) + 2 essais VoxCPM2 (n4v), à l'aveugle, mélangés.
# Retire du panneau les Versions 4 et 5 (F5, abandonné, déjà notées).
import json, os, subprocess, random
V="/root/voix"; B=f"{V}/n4"; P="/tmp/claude-0/-home-user-Voix-SLA/1c69338f-3c8e-524c-9834-35b5bd9a198c/scratchpad/publi/comparer"
items=json.load(open(f"{B}/items8.json")); man=json.load(open(f"{P}/manifest.json"))
files={"comparer/manifest.json":"comparer/manifest.json"}
gone=[p for p in man["paires"] if p["version"] in ("n3d","n3e")]
for p in gone: files["comparer/"+p["clone"]]=None
old=[p for p in man["paires"] if p["version"] not in ("n3d","n3e") and not p["version"].startswith("n4")]
SRC=[("n4x","out_x",3),("n4v","out_vx",2)]; new=[]; random.seed(4)
for it in items:
    grp=[]
    for vid,d,n in SRC:
        for r in range(n):
            s=f"{B}/{d}/{it['id']}r{r}_0.wav"
            if not os.path.exists(s): continue
            os.makedirs(f"{P}/{vid}",exist_ok=True); k=f"{it['id']}r{r}"; dst=f"{P}/{vid}/{k}.mp3"
            subprocess.run(["ffmpeg","-loglevel","error","-y","-i",s,"-ac","1","-b:a","128k",dst],check=True)
            files[f"comparer/{vid}/{k}.mp3"]=f"comparer/{vid}/{k}.mp3"
            grp.append({"id":f"{vid}-{k}","texte":it["texte"],"vrai":None,"clone":f"{vid}/{k}.mp3","version":vid,"nomVersion":""})
    random.shuffle(grp)
    for i,g in enumerate(grp): g["nomVersion"]="Essai "+"ABCDE"[i]
    new+=grp
man["paires"]=new+old; json.dump(man,open(f"{P}/manifest.json","w"),ensure_ascii=False,indent=0)
json.dump(files,open(f"{V}/pipe/n4_files.json","w")); print(len(new),"essais,",len(gone),"retirés")
