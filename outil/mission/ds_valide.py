# Garde uniquement les extraits de la vidéo confirmés « Bon » par l'utilisateur (avis vid-wNNN)
import json, glob
ok = set()
for f in glob.glob("/root/voix/avis_vid/avis/vid-*.json"):
    d = json.load(open(f)); d = d.get("data", d)
    if d.get("note") == "bon": ok.add(f.split("/")[-1][4:-5])
S = [o for o in json.load(open("/root/voix/video/ds_strict.json")) if o["fichier"][:-4] in ok]
base = open("/root/voix/ds/train.csv").read().rstrip("\n").split("\n")
with open("/root/voix/ds/train_ok.csv", "w") as f:
    f.write("\n".join(base) + "\n" + "".join(f"wavs22/{o['fichier']}|{o['texte']}|papa\n" for o in S))
print(len(ok), "confirmés ;", len(S), "extraits,", round(sum(o["duree"] for o in S) / 60, 2), "min ajoutées")
