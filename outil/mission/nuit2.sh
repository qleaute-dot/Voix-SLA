# Nuit : après la comparaison ft2/ft3 -> Applio réentraîné avec les extraits vidéo confirmés (papa2),
# conversion des meilleures prises ft3 avec papa2, puis F5 entraîné sur toutes ses phrases jusqu'au matin.
cd /root/voix; B=/root/voix/n3
while pgrep -f nuit_ft3.sh >/dev/null; do sleep 60; done
[ -f ft3/papa_epoque05.pth ] && xtts/bin/python pipe/demi.py ft3/papa_epoque05.pth
# --- Applio papa2 ---
mkdir -p rvc_ds2; cp rvc_ds/papa.wav rvc_ds2/papa.wav
python3 -c "
import json,glob
ok={f.split('/')[-1][4:-5] for f in glob.glob('avis_vid/avis/vid-*.json') if (lambda d:d.get('data',d))(json.load(open(f))).get('note')=='bon'}
open('/root/voix/rvc_ds2/liste.txt','w').write(''.join(f\"file '/root/voix/ds/wavs24/{n}.wav'\n\" for n in sorted(ok)))"
ffmpeg -loglevel error -y -f concat -safe 0 -i rvc_ds2/liste.txt -ar 40000 -ac 1 rvc_ds2/video.wav && rm rvc_ds2/liste.txt
( while pgrep -f nuit2.sh >/dev/null; do cd /root/applio/logs/papa2 2>/dev/null && ls -t G_*.pth D_*.pth 2>/dev/null | tail -n +3 | xargs -r rm -f; sleep 60; done ) &
rvc/bin/python - <<'PY'
import os, sys, time
os.chdir("/root/applio"); sys.path.insert(0, "/root/applio"); import core
t = time.time()
print(core.run_preprocess_script("papa2", "/root/voix/rvc_ds2", 40000, 4, "Automatic", False, 3.0, 0.3, "none"), flush=True)
print(core.run_extract_script("papa2", "rmvpe", 4, "-", 40000, "contentvec"), round(time.time()-t), flush=True)
print(core.run_train_script("papa2", 10, True, True, 20, 40000, 4, "-", True, False, "Auto"), round(time.time()-t), flush=True)
print(core.run_index_script("papa2", "Auto"), round(time.time()-t), flush=True)
PY
rm -f /root/applio/logs/papa2/G_*.pth /root/applio/logs/papa2/D_*.pth
P2=$(ls /root/applio/logs/papa2/papa2_20e_*.pth 2>/dev/null | head -1)
if [ -n "$P2" ]; then
  sed "s#papa.index#papa2.index#; s#logs/papa/#logs/papa2/#" pipe/rvc_conv2.py > pipe/rvc_conv3.py
  rvc/bin/python pipe/rvc_conv3.py $P2 $B/best_ft3 $B/rvc_ft3b 0 0.3 0.5 off 0 2>&1 | grep -c "^conv"
  mkdir -p $B/out_ft3b; for f in $B/rvc_ft3b/*.wav; do ffmpeg -loglevel error -y -i $f -af "highpass=f=60,afftdn=nr=12:nf=-40,deesser=i=0.4,lowpass=f=11000" $B/out_ft3b/$(basename $f); done
  python3 -c "import json,glob; json.dump(sorted(glob.glob('$B/out_*/*.wav')),open('$B/outw.json','w'))"
  xtts/bin/python pipe/score_sim.py $B/outw.json $B/sim_out.json > /dev/null 2>&1
  python3 -c "
import json,collections; s=json.load(open('$B/sim_out.json')); a=collections.defaultdict(list)
for f,v in s.items(): a[f.split('/')[-2]].append(v)
print('timbre', {k:round(sum(v)/len(v),3) for k,v in a.items()})"
fi
echo APPLIO2FINI
# --- F5 sur toutes ses phrases confirmées, jusqu'à 04:30 UTC ---
python3 - <<'PY'
import json, glob
d = json.load(open('/root/voix/ds/dataset.json'))
ok = {f.split('/')[-1][4:-5] for f in glob.glob('/root/voix/avis_vid/avis/vid-*.json') if (lambda d: d.get('data', d))(json.load(open(f))).get('note') == 'bon'}
S = {o['fichier'][:-4]: o['texte'] for o in json.load(open('/root/voix/video/ds_strict.json'))}
with open('/root/voix/f5t/metadata2.csv', 'w') as f:
    f.write('audio_file|text\n')
    for x in d['train']:
        if x['fichier'] != 'c000.wav': f.write(f"/root/voix/ds/wavs24/{x['fichier']}|{x['texte']}\n")
    for n in sorted(ok): f.write(f"/root/voix/ds/wavs24/{n}.wav|{S[n]}\n")
PY
D=f5/lib/python3.11/data/papa_custom; f5/bin/python f5/lib/python3.11/site-packages/f5_tts/train/datasets/prepare_csv_wavs.py f5t/metadata2.csv $D --pretrain --workers 2 2>&1 | tail -2
cp /root/.cache/huggingface/hub/models--RASPIAUDIO--F5-French-MixedSpeakers-reduced/snapshots/*/vocab.txt $D/vocab.txt
rm -f f5/lib/python3.11/ckpts/papa/model_last.pt
bash pipe/ft_f5.sh > f5t/ft2.log 2>&1 &
while [ $(date -u +%H%M) -lt 0430 ] || [ $(date -u +%H) -ge 12 ]; do sleep 120; pgrep -f f5-tts_finetune >/dev/null || break; done
pkill -f ft_f5.sh; pkill -f f5-tts_finetune; sleep 5
if [ -f f5/lib/python3.11/ckpts/papa/model_last.pt ]; then
  python3 -c "
import json; it=json.load(open('pipe/n3_items.json')); R=json.load(open('f5t/items.json'))[0]['refs']; Q=[r for x in json.load(open('f5t/items.json')) if '?' in x['texte'] for r in x['refs']][2]
for x in it: x['refs']=[Q if '?' in x['texte'] else R[0], R[1]]
json.dump(it,open('$B/f5_items.json','w'),ensure_ascii=False)"
  f5/bin/python pipe/gen_f5b.py $B/f5_items.json $B/raw_f5 f5/lib/python3.11/ckpts/papa/model_last.pt /root/voix/f5/lib/python3.11/data/papa_custom/vocab.txt 2>&1 | grep --line-buffered "^gen"
  echo F5GENFINI
fi
echo NUIT2FINI
