set -e
cd /root/voix
xtts/bin/python pipe/gen_xtts.py pipe/essai_items.json prises/xtts 3 0.65 2>&1 | grep --line-buffered "^gen"
cbx/bin/python pipe/gen_cbx.py pipe/essai_items.json prises/cbx 3 0.5 0.5 2>&1 | grep --line-buffered "^gen"
cbx/bin/python pipe/gen_cbx.py pipe/essai_items.json prises/cbx2 3 0.7 0.35 2>&1 | grep --line-buffered "^gen"
python3 -c "
import json,glob; P={x['id']:x['texte'] for x in json.load(open('pipe/essai_items.json'))}
fs=sorted(glob.glob('prises/*/*.wav')); json.dump(fs,open('pipe/wavs.json','w'))
json.dump([[f,P[f.split('/')[-1].rsplit('_',1)[0]]] for f in fs],open('pipe/asr_in.json','w'),ensure_ascii=False)"
asr/bin/python asr_check.py pipe/asr_in.json pipe/asr.json > /dev/null 2>&1
xtts/bin/python pipe/score_sim.py pipe/wavs.json pipe/sim.json > /dev/null 2>&1
for v in xtts cbx cbx2; do echo "== $v"; python3 pipe/choisir.py pipe/essai_items.json prises/$v pipe/asr.json pipe/sim.json pipe/choix_$v.json; done
echo FINI
