set -e
cd /root/voix
rvc/bin/python - <<'PY'
import json,glob,subprocess,os
it={x['id']:x['texte'] for x in json.load(open('pipe/p60_items.json'))}
sel=[]
for f in sorted(glob.glob('avis_pr/prises/*.json')):
    d=json.load(open(f)); d=d.get('data',d); pid=f.split('/')[-1][:-5]; c=d.get('choix')
    if it[pid].strip().endswith('?'): continue
    sel.append((pid, c if (c is not None and c>=0) else 0))
os.makedirs('mel/in',exist_ok=True)
out=[]
for pid,k in sel:
    r=subprocess.run(['rvc/bin/python','pipe/melodie.py',f'p60/raw/{pid}_{k}.wav',f'mel/in/{pid}_0.wav',it[pid]],capture_output=True,text=True).stdout.strip()
    if r.startswith('corrig'): out.append({'id':pid,'k':k,'texte':it[pid],'exces':r})
    else: os.remove(f'mel/in/{pid}_0.wav')
json.dump(out,open('mel/sel.json','w'),ensure_ascii=False,indent=0); print(len(out),'phrases corrigées')
PY
rvc/bin/python pipe/rvc_conv2.py /root/applio/logs/papa/papa_20e_1180s.pth mel/in mel/rvc 0 0.3 0.5 off 0 2>&1 | grep -c "^conv"
mkdir -p mel/out; for f in mel/rvc/*.wav; do ffmpeg -loglevel error -y -i $f -af "highpass=f=60,afftdn=nr=12:nf=-40,deesser=i=0.4,lowpass=f=11000" mel/out/$(basename $f); done
echo MELFINI
