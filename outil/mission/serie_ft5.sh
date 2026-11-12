set -e
cd /root/voix
B=$(ls -d /root/.cache/huggingface/hub/models--tts-hub--XTTS-v2/snapshots/*/)model.pth
xtts/bin/python pipe/gen_ft.py $B pipe/test_items.json eval/base 1 0.65 2>&1 | grep --line-buffered "^gen"
# série complète : phrases de test d'abord
python3 -c "
import json; t=json.load(open('pipe/test_items.json')); ids={x['id'] for x in t}
a=[x for x in json.load(open('pipe/cmp_items.json')) if x['id'] not in ids]
json.dump(t+a, open('pipe/serie_items.json','w'), ensure_ascii=False)"
xtts/bin/python pipe/gen_ft.py ft1/papa_epoque05.pth pipe/serie_items.json cmp/ft5 1 0.65 2>&1 | grep --line-buffered "^gen"
echo GENFINI
python3 -c "
import json,glob; P={x['id']:x['texte'] for x in json.load(open('pipe/test_items.json'))}
fs=sorted(glob.glob('eval/base/*.wav'))+sorted(f for f in glob.glob('cmp/ft5/*.wav') if f.split('/')[-1].rsplit('_',1)[0] in P)
json.dump(fs,open('pipe/eval_wavs.json','w'))
json.dump([[f,P[f.split('/')[-1].rsplit('_',1)[0]]] for f in fs],open('pipe/eval_asr_in.json','w'),ensure_ascii=False)"
asr/bin/python asr_check.py pipe/eval_asr_in.json pipe/eval_asr.json > /dev/null 2>&1
xtts/bin/python pipe/score_sim.py pipe/eval_wavs.json pipe/eval_sim.json > /dev/null 2>&1
python3 - <<PY
import json,collections
a={x['fichier']:x['wer'] for x in json.load(open('pipe/eval_asr.json'))}; s=json.load(open('pipe/eval_sim.json'))
r=collections.defaultdict(list)
for f in s: r[f.split('/')[-2]].append((s[f],a[f]))
print(json.dumps({k:{'sim':round(sum(x for x,_ in v)/len(v),4),'wer':round(sum(y for _,y in v)/len(v),3)} for k,v in r.items()},indent=1))
PY
echo EVALFINI
