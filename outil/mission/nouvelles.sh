set -e
cd /root/voix; B=/root/voix/nv; I=pipe/nouvelles.json
run() { REFS=$3 SPEED=$5 xtts/bin/python pipe/gen_ft.py ft2/papa_epoque0$2.pth $I $B/$1 2 $4 2>&1 | grep --line-buffered "^gen"; }
run nA 5 /root/voix/refs_gardees.json 0.65 1.0
run nE 5 /root/voix/refs_long.json 0.7 0.92
run nAE 5 /root/voix/refs_gardees.json 0.65 0.93
python3 -c "
import json,glob; P={x['id']:x['texte'] for x in json.load(open('$I'))}
fs=sorted(glob.glob('$B/n*/*.wav')); json.dump(fs,open('pipe/nv_wavs.json','w'))
json.dump([[f,P[f.split('/')[-1].rsplit('_',1)[0]]] for f in fs],open('pipe/nv_asr_in.json','w'),ensure_ascii=False)"
asr/bin/python asr_check.py pipe/nv_asr_in.json pipe/nv_asr.json > /dev/null 2>&1
xtts/bin/python pipe/score_sim.py pipe/nv_wavs.json pipe/nv_sim.json > /dev/null 2>&1
for v in nA nE nAE; do
  python3 pipe/choisir.py $I $B/$v pipe/nv_asr.json pipe/nv_sim.json pipe/nv_choix_$v.json > pipe/nv_choix_$v.log
  mkdir -p $B/best/$v; python3 -c "
import json,shutil
for k,x in json.load(open('pipe/nv_choix_$v.json')).items(): shutil.copy(x['fichier'], '$B/best/$v/%s_0.wav'%k)"
  rvc/bin/python pipe/rvc_conv.py /root/applio/logs/papa/papa_20e_1180s.pth $B/best/$v $B/rvc/$v 0 0.6 0.33 2>&1 | grep -c "^conv"
done
echo NVFINI
