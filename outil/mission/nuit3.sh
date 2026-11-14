# Après nuit2 : Version 4 (F5 ~3000 étapes) post-traitée, puis F5 prolongé -> Version 5.
cd /root/voix; B=/root/voix/n3; C=f5/lib/python3.11/ckpts/papa
while ! grep -q NUIT2FINI nuit2.log; do sleep 60; done
post() {  # $1 = suffixe (f5 / f5b)
  v=$1
  python3 -c "
import json,glob; P={x['id']:x['texte'] for x in json.load(open('pipe/n3_items.json'))}
fs=sorted(glob.glob('$B/raw_$v/*.wav')); json.dump(fs,open('$B/wavs_$v.json','w'))
json.dump([[f,P[f.split('/')[-1].rsplit('_',1)[0]]] for f in fs],open('$B/asr_in_$v.json','w'),ensure_ascii=False)"
  asr/bin/python asr_check.py $B/asr_in_$v.json $B/asr_$v.json > /dev/null 2>&1
  xtts/bin/python pipe/score_sim.py $B/wavs_$v.json $B/sim_$v.json > /dev/null 2>&1
  python3 pipe/choisir.py pipe/n3_items.json $B/raw_$v $B/asr_$v.json $B/sim_$v.json $B/choix_$v.json > /dev/null
  rm -rf $B/best_$v; mkdir -p $B/best_$v; python3 -c "
import json,shutil
for k,x in json.load(open('$B/choix_$v.json')).items(): shutil.copy(x['fichier'], '$B/best_$v/%s_0.wav'%k)"
  rvc/bin/python pipe/rvc_conv2.py /root/applio/logs/papa/papa_20e_1180s.pth $B/best_$v $B/rvc_$v 0 0.3 0.5 off 0 2>&1 | grep -c "^conv"
  mkdir -p $B/out_$v; for f in $B/rvc_$v/*.wav; do ffmpeg -loglevel error -y -i $f -af "highpass=f=60,afftdn=nr=12:nf=-40,deesser=i=0.4,lowpass=f=11000" $B/out_$v/$(basename $f); done
  python3 -c "import json,glob; json.dump(sorted(glob.glob('$B/out_$v/*.wav')),open('$B/outw_$v.json','w'))"
  xtts/bin/python pipe/score_sim.py $B/outw_$v.json $B/sim_out_$v.json > /dev/null 2>&1
  python3 -c "
import json; s=json.load(open('$B/sim_out_$v.json')); c=json.load(open('$B/choix_$v.json'))
print('$v timbre', round(sum(s.values())/len(s),3), 'mots faux >15%:', sum(x['wer']>0.15 for x in c.values()), '/', len(c))"
}
[ -f $C/model_last.pt ] || { echo "PAS DE MODELE F5"; echo NUIT3FINI; exit 1; }
post f5; echo V4PRET
# copie allégée du modèle de la Version 4, puis préparation de la reprise (poids seuls, sans compteur)
f5/bin/python - <<PY
import torch, os
c = torch.load("$C/model_last.pt", map_location="cpu", weights_only=True)
print("modele V4 a l'etape", c.get("update"))
torch.save({"ema_model_state_dict": {k: (v.half() if v.is_floating_point() else v) for k, v in c["ema_model_state_dict"].items()}, "update": c.get("update")}, "/root/voix/f5snap/f5_v4_half.pt")
os.remove("$C/model_last.pt")
sd = {k: v for k, v in c["ema_model_state_dict"].items()}; sd.setdefault("initted", torch.tensor(True)); sd.setdefault("step", torch.tensor(0)); torch.save({"ema_model_state_dict": sd}, "$C/model_last.pt")
PY
bash pipe/ft_f5.sh > f5t/ft3.log 2>&1 &
while [ $(date -u +%H%M) -lt 0630 ] || [ $(date -u +%H) -ge 12 ]; do sleep 60; pgrep -f f5-tts_finetune >/dev/null || break; done
pkill -f ft_f5.sh; pkill -f f5-tts_finetune; sleep 5
tr '\r' '\n' < f5t/ft3.log | grep -oE "update=[0-9]+" | tail -1
f5/bin/python pipe/gen_f5b.py $B/f5_items.json $B/raw_f5b $C/model_last.pt /root/voix/f5/lib/python3.11/data/papa_custom/vocab.txt 2>&1 | grep --line-buffered "^gen" | tail -1
post f5b; echo V5PRET
echo NUIT3FINI
