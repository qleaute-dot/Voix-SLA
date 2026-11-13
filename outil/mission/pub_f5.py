# Comparer : F5 + Applio (« Essai A ») et version actuelle (« Essai B »), en tête de liste
import json, os, subprocess
V="/root/voix"; B=f"{V}/f5t"; P="/tmp/claude-0/-home-user-Voix-SLA/1c69338f-3c8e-524c-9834-35b5bd9a198c/scratchpad/publi/comparer"
items=json.load(open(f"{B}/items.json")); man=json.load(open(f"{P}/manifest.json"))
old=[p for p in man["paires"] if p["version"] not in ("f5a","f5b")]
new=[]; files={"comparer/manifest.json":"comparer/manifest.json"}
for d in ("f5a","f5b"): os.makedirs(f"{P}/{d}",exist_ok=True)
for i,it in enumerate(items):
    vrai=f"vrai/{it['id']}.mp3" if it["id"].startswith("c") else None
    pair=[]
    for d,src,nom in (("f5a",f"{B}/out_best/{it['id']}_0.wav","Essai A"),("f5b",f"{B}/out_act_in/{it['id']}_0.wav","Essai B")):
        dst=f"{P}/{d}/{it['id']}.mp3"; subprocess.run(["ffmpeg","-loglevel","error","-y","-i",src,"-ac","1","-b:a","128k",dst],check=True)
        files[f"comparer/{d}/{it['id']}.mp3"]=f"comparer/{d}/{it['id']}.mp3"
        pair.append({"id":f"{d}-{it['id']}","texte":it["texte"],"vrai":vrai,"clone":f"{d}/{it['id']}.mp3","version":d,"nomVersion":nom})
    if i%2: pair.reverse()
    new+=pair
man["paires"]=new+old; json.dump(man,open(f"{P}/manifest.json","w"),ensure_ascii=False,indent=0)
json.dump(files,open(f"{V}/pipe/f5_files.json","w")); print(len(new),"paires,",len(files),"fichiers")
