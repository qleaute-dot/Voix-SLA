# Après l'entraînement ft3 (avec la vidéo) : 20 phrases neuves, ancienne voix (ft2) vs nouvelle (ft3),
# meilleure de 3 prises, Applio doux + débruitage
cd /root/voix; B=/root/voix/n3
while pgrep -f "train_xtts.py 5 1e-5 /root/voix/ft3" >/dev/null; do sleep 30; done
[ -f ft3/papa_epoque05.pth ] || { echo "PAS DE SAUVEGARDE ft3"; exit 1; }
for v in ft2 ft3; do
  REFS=/root/voix/refs_gardees.json SPEED=1.0 xtts/bin/python pipe/gen_ft.py $v/papa_epoque05.pth pipe/n3_items.json $B/raw_$v 3 0.65 2>&1 | grep --line-buffered "^gen"
done
python3 -c "
import json,glob; P={x['id']:x['texte'] for x in json.load(open('pipe/n3_items.json'))}
fs=sorted(glob.glob('$B/raw_*/*.wav')); json.dump(fs,open('$B/wavs.json','w'))
json.dump([[f,P[f.split('/')[-1].rsplit('_',1)[0]]] for f in fs],open('$B/asr_in.json','w'),ensure_ascii=False)"
asr/bin/python asr_check.py $B/asr_in.json $B/asr.json > /dev/null 2>&1
xtts/bin/python pipe/score_sim.py $B/wavs.json $B/sim.json > /dev/null 2>&1
for v in ft2 ft3; do
  python3 pipe/choisir.py pipe/n3_items.json $B/raw_$v $B/asr.json $B/sim.json $B/choix_$v.json > /dev/null
  mkdir -p $B/best_$v; python3 -c "
import json,shutil
for k,x in json.load(open('$B/choix_$v.json')).items(): shutil.copy(x['fichier'], '$B/best_$v/%s_0.wav'%k)"
  rvc/bin/python pipe/rvc_conv2.py /root/applio/logs/papa/papa_20e_1180s.pth $B/best_$v $B/rvc_$v 0 0.3 0.5 off 0 2>&1 | grep -c "^conv"
  mkdir -p $B/out_$v; for f in $B/rvc_$v/*.wav; do ffmpeg -loglevel error -y -i $f -af "highpass=f=60,afftdn=nr=12:nf=-40,deesser=i=0.4,lowpass=f=11000" $B/out_$v/$(basename $f); done
done
python3 -c "import json,glob; json.dump(sorted(glob.glob('$B/out_*/*.wav')),open('$B/outw.json','w'))"
xtts/bin/python pipe/score_sim.py $B/outw.json $B/sim_out.json > /dev/null 2>&1
python3 -c "
import json,collections; s=json.load(open('$B/sim_out.json')); a=collections.defaultdict(list)
for f,v in s.items(): a[f.split('/')[-2]].append(v)
print({k:round(sum(v)/len(v),3) for k,v in a.items()})
for v in ('ft2','ft3'):
  c=json.load(open('$B/choix_'+v+'.json')); print(v,'mots faux >15%:',sum(x['wer']>0.15 for x in c.values()),'/',len(c))"
echo N3FINI
