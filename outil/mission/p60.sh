set -e
cd /root/voix
REFS=/root/voix/refs_gardees.json SPEED=1.0 xtts/bin/python pipe/gen_ft.py ft2/papa_epoque05.pth pipe/p60_items.json p60/raw 3 0.7 2>&1 | grep --line-buffered "^gen"
# les 3 prises → Applio doux + débruitage
for k in 0 1 2; do mkdir -p p60/in$k; for f in p60/raw/*_$k.wav; do b=$(basename $f _$k.wav); cp $f p60/in$k/${b}_0.wav; done
  rvc/bin/python pipe/rvc_conv2.py /root/applio/logs/papa/papa_20e_1180s.pth p60/in$k p60/rvc$k 0 0.3 0.5 off 0 2>&1 | grep -c "^conv"
  mkdir -p p60/out$k; for f in p60/rvc$k/*.wav; do ffmpeg -loglevel error -y -i $f -af "highpass=f=60,afftdn=nr=12:nf=-40,deesser=i=0.4,lowpass=f=11000" p60/out$k/$(basename $f); done
done
echo P60FINI
