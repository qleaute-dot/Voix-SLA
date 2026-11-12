set -e
cd /root/voix
until grep -q EVALFINI pipe/serie_ft5.log; do sleep 15; done
xtts/bin/python pipe/gen_ft.py ft1/papa_epoque05.pth pipe/serie_items.json cmp/ft5 2 0.65 2>&1 | grep --line-buffered "^gen"
python3 -c "
import json,glob; P={x['id']:x['texte'] for x in json.load(open('pipe/serie_items.json'))}
fs=sorted(glob.glob('cmp/ft5/*.wav')); json.dump(fs,open('pipe/ft5_wavs.json','w'))
json.dump([[f,P[f.split('/')[-1].rsplit('_',1)[0]]] for f in fs],open('pipe/ft5_asr_in.json','w'),ensure_ascii=False)"
asr/bin/python asr_check.py pipe/ft5_asr_in.json pipe/ft5_asr.json > /dev/null 2>&1
xtts/bin/python pipe/score_sim.py pipe/ft5_wavs.json pipe/ft5_sim.json > /dev/null 2>&1
python3 pipe/choisir.py pipe/serie_items.json cmp/ft5 pipe/ft5_asr.json pipe/ft5_sim.json pipe/ft5_choix.json > pipe/ft5_choix.log
mkdir -p cmp/ft5best
python3 -c "
import json,shutil
for k,v in json.load(open('pipe/ft5_choix.json')).items(): shutil.copy(v['fichier'], 'cmp/ft5best/%s_0.wav'%k)
c=json.load(open('pipe/ft5_choix.json')); import statistics as s
print('wer moyen', round(s.mean(v['wer'] for v in c.values()),3), 'sim moyen', round(s.mean(v['sim'] for v in c.values()),4), 'mal dites', sum(v['wer']>0.15 for v in c.values()))"
echo QUALITEFINI
