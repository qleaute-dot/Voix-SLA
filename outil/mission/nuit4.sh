# Reprise après redémarrage de la machine (01:12 UTC) : F5 repart de model_last (étape 1380),
# jusqu'à 04:30 UTC, puis génère la Version 4 ; ensuite nuit3.sh enchaîne (V4 post, prolongation, V5).
cd /root/voix; B=/root/voix/n3; C=f5/lib/python3.11/ckpts/papa
f5/bin/python - <<PY
import torch, os
c = torch.load("$C/model_last.pt", map_location="cpu", weights_only=True)
print("reprise", c.get("update"), len(c["ema_model_state_dict"]))
os.remove("$C/model_last.pt"); sd = {k: v for k, v in c["ema_model_state_dict"].items()}; sd.setdefault("initted", torch.tensor(True)); sd.setdefault("step", torch.tensor(0)); torch.save({"ema_model_state_dict": sd}, "$C/model_last.pt")
PY
bash pipe/ft_f5.sh > f5t/ft4.log 2>&1 &
sleep 120
while [ $(date -u +%H%M) -lt 0430 ] || [ $(date -u +%H) -ge 12 ]; do sleep 60; pgrep -f f5-tts_finetune >/dev/null || break; done
pkill -f ft_f5.sh; pkill -f f5-tts_finetune; sleep 5
tr '\r' '\n' < f5t/ft4.log | grep -oE "update=[0-9]+" | tail -1
python3 -c "
import json; it=json.load(open('pipe/n3_items.json')); R=json.load(open('f5t/items.json'))[0]['refs']; Q=[r for x in json.load(open('f5t/items.json')) if '?' in x['texte'] for r in x['refs']][2]
for x in it: x['refs']=[Q if '?' in x['texte'] else R[0], R[1]]
json.dump(it,open('$B/f5_items.json','w'),ensure_ascii=False)"
f5/bin/python pipe/gen_f5b.py $B/f5_items.json $B/raw_f5 $C/model_last.pt /root/voix/f5/lib/python3.11/data/papa_custom/vocab.txt 2>&1 | grep --line-buffered "^gen" | tail -1
echo F5GENFINI; echo NUIT2FINI | tee -a nuit2.log
