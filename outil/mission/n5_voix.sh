# Phrases « Position et gêne » avec la Version 3 : ft3, 3 prises, meilleure prise (mots puis timbre), Applio papa2, débruitage
cd /root/voix; B=/root/voix/n5; I=${1:-$B/items.json}
SEEDOFF=0 REFS=/root/voix/refs_gardees.json xtts/bin/python pipe/gen_ft.py ft3/papa_epoque05.pth $I $B/raw 3 0.65 2>&1 | grep --line-buffered "^gen"
python3 -c "
import json,glob; P={x['id']:x['texte'] for x in json.load(open('$I'))}
fs=sorted(f for f in glob.glob('$B/raw/*.wav') if f.split('/')[-1].rsplit('_',1)[0] in P); json.dump(fs,open('$B/wavs.json','w'))
json.dump([[f,P[f.split('/')[-1].rsplit('_',1)[0]]] for f in fs],open('$B/asr_in.json','w'),ensure_ascii=False)"
asr/bin/python asr_check.py $B/asr_in.json $B/asr.json > /dev/null 2>&1
xtts/bin/python pipe/score_sim.py $B/wavs.json $B/sim.json > /dev/null 2>&1
python3 pipe/choisir.py $I $B/raw $B/asr.json $B/sim.json $B/choix.json > /dev/null
mkdir -p $B/best; python3 -c "
import json,shutil
for k,x in json.load(open('$B/choix.json')).items(): shutil.copy(x['fichier'], '$B/best/%s_0.wav'%k)"
rvc/bin/python pipe/rvc_conv3.py /root/applio/logs/papa2/papa2_20e_1440s.pth $B/best $B/rvc 0 0.3 0.5 off 0 2>&1 | grep -c "^conv"
mkdir -p $B/out; for f in $B/rvc/*.wav; do o=$B/out/$(basename $f .wav).mp3; [ -f $o ] || ffmpeg -loglevel error -y -i $f -af "highpass=f=60,afftdn=nr=12:nf=-40,deesser=i=0.4,lowpass=f=11000" -ac 1 -b:a 128k $o; done
python3 -c "
import json; c=json.load(open('$B/choix.json')); print('mots faux >15%:',sum(x['wer']>0.15 for x in c.values()),'/',len(c))"
echo N5FINI
