cd /root/voix
until grep -q SEEDFINI pipe/seed_fils.log; do sleep 30; done
bash pipe/seed_conv.sh /root/voix/qz/c021 /root/voix/seedout/qz 30 > pipe/seed_qz.log 2>&1
T=$(python3 -c "import json;print([r['texte'] for r in json.load(open('ds/dataset.json'))['train'] if r['fichier']=='c021.wav'][0])")
qwen/bin/python pipe/gen_qwen.py pipe/qz_extra.json qz/c021 1 ds/wavs24/c021.wav "$T" > pipe/qwen_extra.log 2>&1
bash pipe/seed_conv.sh /root/voix/qz/c021 /root/voix/seedout/qz 30 >> pipe/seed_qz.log 2>&1
echo QUEUEFINI >> pipe/seed_qz.log
