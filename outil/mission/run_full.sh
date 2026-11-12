# usage: run_full.sh moteur(cbx|cbx2|xtts)
set -e
cd /root/voix; V=$1; D=full/$V; mkdir -p $D
gen() { # $1=items $2=ntakes
  if [ $V = xtts ]; then xtts/bin/python pipe/gen_xtts.py $1 $D $2 0.65 2>&1 | grep --line-buffered "^gen";
  elif [ $V = cbx ]; then cbx/bin/python pipe/gen_cbx.py $1 $D $2 0.5 0.5 2>&1 | grep --line-buffered "^gen";
  else cbx/bin/python pipe/gen_cbx.py $1 $D $2 0.7 0.35 2>&1 | grep --line-buffered "^gen"; fi; }
check() {
  python3 -c "
import json,glob; P={x['id']:x['texte'] for x in json.load(open('pipe/items_all.json'))}
fs=sorted(glob.glob('$D/*.wav')); json.dump(fs,open('$D.wavs.json','w'))
json.dump([[f,P[f.split('/')[-1].rsplit('_',1)[0]]] for f in fs],open('$D.asr_in.json','w'),ensure_ascii=False)"
  asr/bin/python asr_check.py $D.asr_in.json $D.asr.json > /dev/null 2>&1
  python3 - <<PY
import json,collections
a=json.load(open('$D.asr.json')); best=collections.defaultdict(lambda:9)
for x in a:
    k=x['fichier'].split('/')[-1].rsplit('_',1)[0]; best[k]=min(best[k],x['wer'])
items=json.load(open('pipe/items_all.json'))
bad=[it for it in items if best[it['id']]>0.15]
json.dump(bad,open('$D.retry.json','w'),ensure_ascii=False); print('a refaire',len(bad),flush=True)
PY
}
gen pipe/items_all.json 1; check
for n in 2 3 4; do
  [ "$(python3 -c "import json;print(len(json.load(open('$D.retry.json'))))")" = 0 ] && break
  gen $D.retry.json $n; check
done
xtts/bin/python pipe/score_sim.py $D.wavs.json $D.sim.json > /dev/null 2>&1
python3 pipe/choisir.py pipe/items_all.json $D $D.asr.json $D.sim.json $D.choix.json | awk '$2>0.15' 
echo FINI
