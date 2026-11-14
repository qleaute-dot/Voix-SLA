# Reprise des phrases « Position » mal prononcées : 8 prises de plus, meilleure prise parmi les 11
cd /root/voix; B=/root/voix/n5; I=$B/items_r.json
SEEDOFF=300 REFS=/root/voix/refs_gardees.json xtts/bin/python pipe/gen_ft.py ft3/papa_epoque05.pth $I $B/raw2 8 0.65 2>&1 | grep --line-buffered "^gen"
python3 -c "
import json,glob; P={x['id']:x['texte'] for x in json.load(open('$I'))}
fs=sorted(glob.glob('$B/raw2/*.wav')); json.dump(fs,open('$B/wavs2.json','w'))
json.dump([[f,P[f.split('/')[-1].rsplit('_',1)[0]]] for f in fs],open('$B/asr_in2.json','w'),ensure_ascii=False)"
asr/bin/python asr_check.py $B/asr_in2.json $B/asr2.json > /dev/null 2>&1
xtts/bin/python pipe/score_sim.py $B/wavs2.json $B/sim2.json > /dev/null 2>&1
python3 - <<'PY'
import json,shutil,os
B='/root/voix/n5'; a={x['fichier']:x for x in json.load(open(B+'/asr.json'))+json.load(open(B+'/asr2.json'))}
s=json.load(open(B+'/sim.json')); s.update(json.load(open(B+'/sim2.json'))); c=json.load(open(B+'/choix.json'))
for it in json.load(open(B+'/items_r.json')):
  q=it['id']; fs=[f for f in a if os.path.basename(f).rsplit('_',1)[0]==q]
  best=min(fs,key=lambda f:(round(a[f]['wer'],2)>0.15,a[f]['wer'],-s.get(f,0)))
  c[q]={'texte':it['texte'],'fichier':best,'wer':a[best]['wer'],'sim':s.get(best),'entendu':a[best]['entendu']}
  shutil.copy(best,f'{B}/best/{q}_0.wav')
  for d in ('rvc','out'):
    for e in ('wav','mp3'):
      p=f'{B}/{d}/{q}_0.{e}'
      if os.path.exists(p): os.remove(p)
json.dump(c,open(B+'/choix.json','w'),ensure_ascii=False,indent=1)
print('mots faux >15%:',sum(x['wer']>0.15 for x in c.values()),'/',len(c))
for k,v in c.items():
  if v['wer']>0.15: print(k,v['wer'],v['entendu'])
PY
rvc/bin/python pipe/rvc_conv3.py /root/applio/logs/papa2/papa2_20e_1440s.pth $B/best $B/rvc 0 0.3 0.5 off 0 2>&1 | grep -c "^conv"
for f in $B/rvc/*.wav; do o=$B/out/$(basename $f .wav).mp3; [ -f $o ] || ffmpeg -loglevel error -y -i $f -af "highpass=f=60,afftdn=nr=12:nf=-40,deesser=i=0.4,lowpass=f=11000" -ac 1 -b:a 128k $o; done
echo REPRISEFINI
