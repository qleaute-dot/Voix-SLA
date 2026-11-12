cd /root/voix
for c in c021 c047 c008; do
  T=$(python3 -c "import json;print([r['texte'] for r in json.load(open('ds/dataset.json'))['train'] if r['fichier']=='$c.wav'][0])")
  f5/bin/python pipe/gen_f5.py pipe/f5_items.json f5zs/$c 1 ds/wavs24/$c.wav "$T" 2>&1 | grep --line-buffered -E "^gen|Error|Traceback"
done
echo GENFINI
