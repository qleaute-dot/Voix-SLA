# Comparer : « Vidéo — est-ce bien papa ? » (Bon = c'est lui) ; retire les séries déjà notées nA/nE/nAE/b2/b3
import json, os, subprocess
V="/root/voix"; P="/tmp/claude-0/-home-user-Voix-SLA/1c69338f-3c8e-524c-9834-35b5bd9a198c/scratchpad/publi/comparer"
man=json.load(open(f"{P}/manifest.json")); retire=("nA","nE","nAE","b2","b3","vid")
files={"comparer/manifest.json":"comparer/manifest.json"}
for p in man["paires"]:
    if p["version"] in retire[:-1]: files["comparer/"+p["clone"]]=None
old=[p for p in man["paires"] if p["version"] not in retire]
os.makedirs(f"{P}/vid",exist_ok=True); new=[]
for o in json.load(open(f"{V}/video/ds_video.json")):
    n=o["fichier"][:-4]; dst=f"{P}/vid/{n}.mp3"
    subprocess.run(["nice","ffmpeg","-loglevel","error","-y","-i",f"{V}/ds/wavs24/{n}.wav","-ac","1","-b:a","96k",dst],check=True)
    files[f"comparer/vid/{n}.mp3"]=f"comparer/vid/{n}.mp3"
    new.append({"id":f"vid-{n}","texte":o["texte"],"vrai":None,"clone":f"vid/{n}.mp3","version":"vid","nomVersion":"Extrait de la vidéo — « Bon » si c'est bien papa"})
man["paires"]=new+old; json.dump(man,open(f"{P}/manifest.json","w"),ensure_ascii=False,indent=0)
json.dump(files,open(f"{V}/pipe/vid_files.json","w")); print(len(new),"extraits,",sum(v is None for v in files.values()),"retirés,",len(files),"entrées")
