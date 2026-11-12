# usage: choisir.py items.json takesdir asr.json sim.json -> meilleure prise par phrase
import sys, json, glob, os
items = json.load(open(sys.argv[1])); d = sys.argv[2]
asr = {x["fichier"]: x for x in json.load(open(sys.argv[3]))}; sim = json.load(open(sys.argv[4]))
res = {}
for it in items:
    takes = sorted(glob.glob(f"{d}/{it['id']}_*.wav"))
    best = min(takes, key=lambda f: (round(asr[f]["wer"], 2) > 0.15, asr[f]["wer"], -sim.get(f, 0)))
    res[it["id"]] = {"texte": it["texte"], "fichier": best, "wer": asr[best]["wer"], "sim": sim.get(best), "entendu": asr[best]["entendu"]}
json.dump(res, open(sys.argv[5], "w"), ensure_ascii=False, indent=1)
for k, v in res.items(): print(k, v["wer"], v["sim"], v["entendu"])
