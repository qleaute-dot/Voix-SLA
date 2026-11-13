# Variantes de diction XTTS (entraîné) → meilleure de 2 prises → Applio époque 20
set -e
cd /root/voix
B=/root/voix/var
run() { # nom epoque refs temperature vitesse
  REFS=$3 SPEED=$5 xtts/bin/python pipe/gen_ft.py ft2/papa_epoque0$2.pth pipe/var_items.json $B/$1 2 $4 2>&1 | grep --line-buffered "^gen"
}
run v_ep5 5 /root/voix/refs_gardees.json 0.65 1.0
run v_ep3 3 /root/voix/refs_gardees.json 0.65 1.0
run v_long 5 /root/voix/refs_long.json 0.7 1.0
run v_expr 5 /root/voix/refs_long.json 0.85 1.0
run v_lent 5 /root/voix/refs_long.json 0.7 0.92
python3 -c "
import json,glob; P={x['id']:x['texte'] for x in json.load(open('pipe/var_items.json'))}
fs=sorted(glob.glob('$B/*/*.wav')); json.dump(fs,open('pipe/var_wavs.json','w'))
json.dump([[f,P[f.split('/')[-1].rsplit('_',1)[0]]] for f in fs],open('pipe/var_asr_in.json','w'),ensure_ascii=False)"
asr/bin/python asr_check.py pipe/var_asr_in.json pipe/var_asr.json > /dev/null 2>&1
xtts/bin/python pipe/score_sim.py pipe/var_wavs.json pipe/var_sim.json > /dev/null 2>&1
for v in v_ep5 v_ep3 v_long v_expr v_lent; do
  python3 pipe/choisir.py pipe/var_items.json $B/$v pipe/var_asr.json pipe/var_sim.json pipe/var_choix_$v.json > /dev/null
  mkdir -p $B/best/$v; python3 -c "
import json,shutil
for k,x in json.load(open('pipe/var_choix_$v.json')).items(): shutil.copy(x['fichier'], '$B/best/$v/%s_0.wav'%k)"
  rvc/bin/python pipe/rvc_conv.py /root/applio/logs/papa/papa_20e_1180s.pth $B/best/$v $B/rvc/$v 0 0.6 0.33 2>&1 | grep -c "^conv"
done
echo VARFINI
