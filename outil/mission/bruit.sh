set -e
cd /root/voix; M=/root/applio/logs/papa/papa_20e_1180s.pth; S=nv/best/nA; O=/root/voix/bruit
rvc/bin/python pipe/rvc_conv2.py $M $S $O/b1 0 0.3 0.5 off 0 2>&1 | grep -c "^conv"
rvc/bin/python pipe/rvc_conv2.py $M $S $O/b2 0 0.3 0.5 light 12 2>&1 | grep -c "^conv"
mkdir -p $O/b3; for f in $O/b1/*.wav; do ffmpeg -loglevel error -y -i $f -af "highpass=f=60,afftdn=nr=12:nf=-40,deesser=i=0.4,lowpass=f=11000" $O/b3/$(basename $f); done
mkdir -p $O/b0; cp nv/rvc/nA/*.wav $O/b0/
echo BRUITFINI
