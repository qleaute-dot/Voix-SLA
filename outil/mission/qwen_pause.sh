cd /root/voix
pkill -STOP -f "rvc/bin/python"
T=$(python3 -c "import json;print([r['texte'] for r in json.load(open('ds/dataset.json'))['train'] if r['fichier']=='c021.wav'][0])")
qwen/bin/python pipe/gen_qwen.py pipe/qz_extra.json qz/c021 1 ds/wavs24/c021.wav "$T" > pipe/qwen_extra.log 2>&1
pkill -CONT -f "rvc/bin/python"
echo "QWENFINI $(ls qz/c021 | wc -l)" >> pipe/qwen_extra.log
