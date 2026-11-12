# Après l'entraînement : évalue les époques sur les 5 phrases jamais entendues, puis génère la série Comparer
set -e
cd /root/voix
python3 -c "
import json; d=json.load(open('ds/dataset.json'))
json.dump([{'id':r['fichier'][:-4],'texte':r['texte']} for r in d['test']], open('pipe/test_items.json','w'), ensure_ascii=False)"
B=$(ls -d /root/.cache/huggingface/hub/models--tts-hub--XTTS-v2/snapshots/*/)model.pth
xtts/bin/python pipe/gen_ft.py $B pipe/test_items.json eval/base 2 0.65 2>&1 | grep --line-buffered "^gen"
for e in 05 10 15; do
  [ -f ft1/papa_epoque$e.pth ] || continue
  xtts/bin/python pipe/gen_ft.py ft1/papa_epoque$e.pth pipe/test_items.json eval/ep$e 2 0.65 2>&1 | grep --line-buffered "^gen"
done
python3 -c "
import json,glob; P={x['id']:x['texte'] for x in json.load(open('pipe/test_items.json'))}
fs=sorted(glob.glob('eval/*/*.wav')); json.dump(fs,open('pipe/eval_wavs.json','w'))
json.dump([[f,P[f.split('/')[-1].rsplit('_',1)[0]]] for f in fs],open('pipe/eval_asr_in.json','w'),ensure_ascii=False)"
asr/bin/python asr_check.py pipe/eval_asr_in.json pipe/eval_asr.json > /dev/null 2>&1
xtts/bin/python pipe/score_sim.py pipe/eval_wavs.json pipe/eval_sim.json > /dev/null 2>&1
python3 - <<PY
import json,collections
a={x['fichier']:x['wer'] for x in json.load(open('pipe/eval_asr.json'))}; s=json.load(open('pipe/eval_sim.json'))
r=collections.defaultdict(list)
for f in s: r[f.split('/')[-2]].append((s[f],a[f]))
res={k:{'sim':round(sum(x for x,_ in v)/len(v),4),'wer':round(sum(y for _,y in v)/len(v),3)} for k,v in r.items()}
print(json.dumps(res,indent=1)); json.dump(res,open('pipe/eval_res.json','w'))
PY
echo EVALFINI
