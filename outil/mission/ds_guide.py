# Jeu d'entraînement guidé : vraies phrases de papa + prises choisies notées >= 4 (après Applio)
import json, glob, os, librosa, soundfile as sf
V="/root/voix"; D=f"{V}/ds"
choix={}
for f in glob.glob(f"{V}/avis_pr/prises/*.json"):
    d=json.load(open(f)); d=d.get("data",d); choix[os.path.basename(f)[:-5]]=d
items={x["id"]:x["texte"] for x in json.load(open(f"{V}/pipe/p60_items.json"))}
rows=[l for l in open(f"{D}/train.csv").read().splitlines()[1:]]
os.makedirs(f"{D}/wavs22", exist_ok=True); n=0
for pid,d in sorted(choix.items()):
    k=d.get("choix"); e=d.get("etoiles") or 0
    if k is None or k<0 or e<4: continue
    w=f"{V}/p60/out{k}/{pid}_0.wav"
    y,sr=librosa.load(w,sr=22050); out=f"g_{pid}.wav"; sf.write(f"{D}/wavs22/{out}",y,22050)
    rep = 2 if e==5 else 1   # les 5/5 comptent double
    for _ in range(rep): rows.append(f"wavs22/{out}|{items[pid]}|papa"); n+=1
with open(f"{D}/train_guide.csv","w") as f: f.write("audio_file|text|speaker_name\n"+"\n".join(rows)+"\n")
print("exemples guidés ajoutés:", n, "total:", len(rows))
