cd /root/voix; B=/root/voix/n4
f5/bin/python pipe/gen_vox.py $B/items8.json $B/raw_vx 2>&1 | grep --line-buffered "^gen"
python3 -c "
import json,glob; P={x['id']:x['texte'] for x in json.load(open('$B/items8.json'))}
fs=sorted(glob.glob('$B/raw_vx/*.wav')); json.dump(fs,open('$B/wavs_vx.json','w'))
json.dump([[f,P[f.split('/')[-1].rsplit('_',1)[0]]] for f in fs],open('$B/asr_in_vx.json','w'),ensure_ascii=False)"
asr/bin/python asr_check.py $B/asr_in_vx.json $B/asr_vx.json > /dev/null 2>&1
xtts/bin/python pipe/score_sim.py $B/wavs_vx.json $B/sim_vx.json > /dev/null 2>&1
python3 - <<'PY'
import json,os,collections,subprocess
B='/root/voix/n4'; asr={x['fichier']:x for x in json.load(open(B+'/asr_vx.json'))}; sim=json.load(open(B+'/sim_vx.json'))
g=collections.defaultdict(list)
for f in asr: g[os.path.basename(f).rsplit('_',1)[0]].append(f)
os.makedirs(B+'/out_vx',exist_ok=True); choix={}
for q,fs in sorted(g.items()):
  fs.sort(key=lambda f:(round(asr[f]['wer'],2)>0.15, -sim.get(f,0)))
  for r,f in enumerate(fs[:2]):
    subprocess.run(['ffmpeg','-loglevel','error','-y','-i',f,'-ar','24000',f'{B}/out_vx/{q}r{r}_0.wav'])
    choix[f'{q}r{r}']={'src':f,'wer':asr[f]['wer'],'sim':sim.get(f),'entendu':asr[f]['entendu']}
json.dump(choix,open(B+'/choix_vx.json','w'),indent=1,ensure_ascii=False)
for k,v in choix.items(): print(k,v)
PY
echo VOXFINI
