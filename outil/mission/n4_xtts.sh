# 5 nouvelles prises Version 3 (ft3 + Applio papa2) sur les 8 phrases imparfaites ; questions aussi avec des extraits-questions comme modèle
cd /root/voix; B=/root/voix/n4
SEEDOFF=500 REFS=/root/voix/refs_gardees.json xtts/bin/python pipe/gen_ft.py ft3/papa_epoque05.pth $B/items8.json $B/raw_n 5 0.65 2>&1 | grep --line-buffered "^gen"
SEEDOFF=900 REFS=$B/refs_q.json xtts/bin/python pipe/gen_ft.py ft3/papa_epoque05.pth $B/itemsq.json $B/raw_q 5 0.65 2>&1 | grep --line-buffered "^gen"
python3 -c "
import json,glob; P={x['id']:x['texte'] for x in json.load(open('$B/items8.json'))}
fs=sorted(glob.glob('$B/raw_*/*.wav')); json.dump(fs,open('$B/wavs.json','w'))
json.dump([[f,P[f.split('/')[-1].rsplit('_',1)[0]]] for f in fs],open('$B/asr_in.json','w'),ensure_ascii=False)"
asr/bin/python asr_check.py $B/asr_in.json $B/asr.json > /dev/null 2>&1
xtts/bin/python pipe/score_sim.py $B/wavs.json $B/sim.json > /dev/null 2>&1
python3 - <<'PY'
import json,shutil,os,collections
B='/root/voix/n4'; asr={x['fichier']:x for x in json.load(open(B+'/asr.json'))}; sim=json.load(open(B+'/sim.json'))
g=collections.defaultdict(list)
for f in asr: g[os.path.basename(f).rsplit('_',1)[0]].append(f)
os.makedirs(B+'/best_x',exist_ok=True); choix={}
for q,fs in sorted(g.items()):
  fs.sort(key=lambda f:(round(asr[f]['wer'],2)>0.15, -sim.get(f,0)))
  for r,f in enumerate(fs[:3]):
    shutil.copy(f,f'{B}/best_x/{q}r{r}_0.wav'); choix[f'{q}r{r}']={'src':f,'wer':asr[f]['wer'],'sim':sim.get(f)}
json.dump(choix,open(B+'/choix_x.json','w'),indent=1)
for k,v in choix.items(): print(k,v)
PY
rvc/bin/python pipe/rvc_conv3.py /root/applio/logs/papa2/papa2_20e_1440s.pth $B/best_x $B/rvc_x 0 0.3 0.5 off 0 2>&1 | grep -c "^conv"
mkdir -p $B/out_x; for f in $B/rvc_x/*.wav; do ffmpeg -loglevel error -y -i $f -af "highpass=f=60,afftdn=nr=12:nf=-40,deesser=i=0.4,lowpass=f=11000" $B/out_x/$(basename $f); done
echo XTTSFINI
