# usage: rvc_test.sh EPOCH -> convertit toutes les sources disponibles avec le modèle Applio de cette époque
cd /root/voix; E=$1
P=$(ls /root/applio/logs/papa/papa_${E}e_*.pth | head -1)
O=/root/voix/rvcout/e$E
mkdir -p /root/voix/ft5sel && for i in $(python3 -c "import json;print(' '.join([x['id'] for x in json.load(open('pipe/test_items.json'))+json.load(open('pipe/qz_extra.json'))]))"); do [ -f cmp/ft5best/${i}_0.wav ] && cp -n cmp/ft5best/${i}_0.wav ft5sel/; done
rvc/bin/python pipe/rvc_conv.py $P /root/voix/fils/clips $O/fils -1 0.6 0.33 2>&1 | grep --line-buffered "^conv"
rvc/bin/python pipe/rvc_conv.py $P /root/voix/qz/c021 $O/qz -2 0.6 0.33 2>&1 | grep --line-buffered "^conv"
[ -d seedout/fils ] && rvc/bin/python pipe/rvc_conv.py $P /root/voix/seedout/fils $O/seedfils 0 0.6 0.33 2>&1 | grep --line-buffered "^conv"
[ -d seedout/qz ] && rvc/bin/python pipe/rvc_conv.py $P /root/voix/seedout/qz $O/seedqz 0 0.6 0.33 2>&1 | grep --line-buffered "^conv"
rvc/bin/python pipe/rvc_conv.py $P /root/voix/ft5sel $O/ft5 0 0.6 0.33 2>&1 | grep --line-buffered "^conv"
echo "TESTFINI $E"
