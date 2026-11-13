# Publie prises/manifest.json avec les prises disponibles (out0, out1, out2)
import json, os, subprocess, glob
V="/root/voix"; P="/tmp/claude-0/-home-user-Voix-SLA/1c69338f-3c8e-524c-9834-35b5bd9a198c/scratchpad/publi/prises"
os.makedirs(P, exist_ok=True)
items=json.load(open(f"{V}/pipe/p60_items.json")); files={"prises/manifest.json":"prises/manifest.json"}; ph=[]
for it in items:
    pr=[]
    for k in range(3):
        w=f"{V}/p60/out{k}/{it['id']}_0.wav"
        if not os.path.exists(w): continue
        dst=f"{P}/{it['id']}_{k}.mp3"
        if not os.path.exists(dst): subprocess.run(["ffmpeg","-loglevel","error","-y","-i",w,"-ac","1","-b:a","128k",dst],check=True)
        pr.append(f"prises/{it['id']}_{k}.mp3"); files[f"prises/{it['id']}_{k}.mp3"]=f"prises/{it['id']}_{k}.mp3"
    if pr: ph.append({"id":it["id"],"texte":it["texte"],"prises":pr})
json.dump({"phrases":ph},open(f"{P}/manifest.json","w"),ensure_ascii=False,indent=1)
json.dump(files,open(f"{V}/pipe/prises_files.json","w")); print(len(ph),"phrases",len(files),"fichiers")
