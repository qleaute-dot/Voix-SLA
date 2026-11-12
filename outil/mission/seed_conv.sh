# usage: seed_conv.sh in_dir out_dir steps
cd /root/seedvc; mkdir -p $2
for f in $1/*_0.wav; do
  b=$(basename $f); [ -f $2/$b ] && continue
  t=$(mktemp -d); /root/voix/svc/bin/python inference.py --source $f --target /root/voix/seed_ref.wav --output $t --diffusion-steps $3 --fp16 False > /dev/null 2>&1
  o=$(ls $t/*.wav 2>/dev/null | head -1); [ -n "$o" ] && mv "$o" $2/$b && echo "seed $b"; rm -rf $t
done
echo SEEDFINI
