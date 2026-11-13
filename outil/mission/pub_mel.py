# Ajoute en tête de « Choisir la meilleure prise » le test de mélodie : actuelle vs fin de phrase corrigée (ordre au hasard)
import json, os, subprocess, random
V="/root/voix"; R="/tmp/claude-0/-home-user-Voix-SLA/1c69338f-3c8e-524c-9834-35b5bd9a198c/scratchpad/publi"; P=f"{R}/prises"
sel=json.load(open(f"{V}/mel/sel.json")); random.seed(42); ordre={}; ph=[]; files={}
for s in sel:
    mid="m"+s["id"][1:]; src={"actuelle":f"{V}/p60/out{s['k']}/{s['id']}_0.wav","melodie":f"{V}/mel/out/{s['id']}_0.wav"}
    o=["actuelle","melodie"]; random.shuffle(o); ordre[mid]=o; pr=[]
    for j,name in enumerate(o):
        dst=f"{P}/{mid}_{j}.mp3"; subprocess.run(["ffmpeg","-loglevel","error","-y","-i",src[name],"-ac","1","-b:a","128k",dst],check=True)
        pr.append(f"prises/{mid}_{j}.mp3"); files[f"prises/{mid}_{j}.mp3"]=f"prises/{mid}_{j}.mp3"
    ph.append({"id":mid,"texte":"(Test mélodie) "+s["texte"],"prises":pr})
man=json.load(open(f"{P}/manifest.json")); man["phrases"]=[p for p in man["phrases"] if not p["id"].startswith("m")]
# les 19 phrases restantes du premier lot d'abord ? non : test mélodie en tête, il est court
man["phrases"]=ph+man["phrases"]; json.dump(man,open(f"{P}/manifest.json","w"),ensure_ascii=False,indent=1)
files["prises/manifest.json"]="prises/manifest.json"
json.dump(ordre,open(f"{V}/mel/ordre.json","w"),indent=0); json.dump(files,open(f"{V}/pipe/mel_files.json","w"))
print(len(ph),"phrases",len(files),"fichiers")
