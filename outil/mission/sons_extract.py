import json, os, subprocess, numpy as np, soundfile as sf, re
audio, sr = sf.read("/root/voix/travail/enregistrement_nettoye.wav", dtype="float32")
T = json.load(open("/root/voix/travail/transcription.json"))
out = "/tmp/claude-0/-home-user-Voix-SLA/1c69338f-3c8e-524c-9834-35b5bd9a198c/scratchpad/publi/sons"
os.makedirs(out, exist_ok=True)
def cut(a, b, name):
    x = audio[int(a*sr):int(b*sr)].copy(); f = int(sr*0.04); x[:f] *= np.linspace(0,1,f); x[-f:] *= np.linspace(1,0,f)
    sf.write("/tmp/s.wav", x, sr)
    subprocess.run(["ffmpeg","-loglevel","error","-y","-i","/tmp/s.wav","-ac","1","-b:a","96k",f"{out}/{name}.mp3"],check=True)
items = []
for i,(a,b,lab) in enumerate([(142.3,144.6,"Rire"),(302.9,305.6,"Rire"),(145.7,147.6,"Soupir"),(300.4,302.1,"Soupir"),(44.0,45.6,"Soupir"),(319.6,321.2,"Raclement de gorge")]):
    n=f"s{i:02d}"; cut(a,b,n); items.append({"id":n,"label":lab,"fichier":n+".mp3","source":"détecté"})
words=[w for s in T for w in s["words"]]
want={"voilà":"« Voilà »","bah":"« Bah »","ben":"« Ben »","bon":"« Bon »","oui":"« Oui »","non":"« Non »"}
seen={}
for w in words:
    k=re.sub(r"[^a-zàâéèêëîïôûüç]","",w["w"].lower())
    if k in want and w["p"]>0.75 and seen.get(k,0)<2 and w["e"]-w["s"]>0.15:
        seen[k]=seen.get(k,0)+1; n=f"m{len(items):02d}"
        cut(max(0,w["s"]-0.12), w["e"]+0.18, n); items.append({"id":n,"label":want[k],"fichier":n+".mp3","source":"mot"})
json.dump({"sons":items},open(f"{out}/manifest.json","w"),ensure_ascii=False,indent=1)
print(len(items), [x["label"] for x in items])
