# Après F5 : choix de la meilleure prise (mots + timbre), Applio doux + débruitage, version actuelle en face
set -e
cd /root/voix; B=/root/voix/f5t
while pgrep -f gen_f5b.py >/dev/null; do sleep 20; done
python3 -c "
import json,glob; P={x['id']:x['texte'] for x in json.load(open('$B/items.json'))}
fs=sorted(glob.glob('$B/raw/*.wav')); json.dump(fs,open('$B/wavs.json','w'))
json.dump([[f,P[f.split('/')[-1].rsplit('_',1)[0]]] for f in fs],open('$B/asr_in.json','w'),ensure_ascii=False)"
asr/bin/python asr_check.py $B/asr_in.json $B/asr.json > /dev/null 2>&1
xtts/bin/python pipe/score_sim.py $B/wavs.json $B/sim.json > /dev/null 2>&1
python3 pipe/choisir.py $B/items.json $B/raw $B/asr.json $B/sim.json $B/choix.json
mkdir -p $B/best $B/act_in; python3 -c "
import json,shutil
for k,x in json.load(open('$B/choix.json')).items(): shutil.copy(x['fichier'], '$B/best/%s_0.wav'%k)"
for c in c001 c024 c038 c054; do cp var/best/v_ep5/${c}_0.wav $B/act_in/; done
for p in p01 p02 p05 p06 p10 p22 p03 p04 p35 p37; do cp p60/raw/${p}_0.wav $B/act_in/${p}_0.wav; done
for s in best act_in; do
  rvc/bin/python pipe/rvc_conv2.py /root/applio/logs/papa/papa_20e_1180s.pth $B/$s $B/rvc_$s 0 0.3 0.5 off 0 2>&1 | grep -c "^conv"
  mkdir -p $B/out_$s; for f in $B/rvc_$s/*.wav; do ffmpeg -loglevel error -y -i $f -af "highpass=f=60,afftdn=nr=12:nf=-40,deesser=i=0.4,lowpass=f=11000" $B/out_$s/$(basename $f); done
done
python3 -c "import json,glob; json.dump(sorted(glob.glob('$B/out_*/*.wav')),open('$B/outw.json','w'))"
xtts/bin/python pipe/score_sim.py $B/outw.json $B/sim_out.json 2>&1 | tail -1
echo F5POSTFINI
