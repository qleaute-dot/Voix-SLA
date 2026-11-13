# Idempotent : relance l'entraînement Applio (reprend à la dernière sauvegarde) et le guetteur de conversions
cd /root/voix
(swapon --show | grep -q swapfile) || swapon /root/swapfile 2>/dev/null
if ! pgrep -f "rvc_train2.py" >/dev/null; then
  (rvc/bin/python pipe/rvc_train2.py 300 4 >> pipe/rvc3.log 2>&1; echo "EXIT $?" >> pipe/rvc3.log) &
  echo "relancé Applio $(date)"
fi
sed -i '/^EXIT/d' pipe/rvc3.log 2>/dev/null
if ! pgrep -f "rvc_watch.sh" >/dev/null; then (bash pipe/rvc_watch.sh > /dev/null 2>&1 &); echo "relancé guetteur"; fi
pgrep -f menage.sh >/dev/null || (nohup bash /root/voix/pipe/menage.sh > /dev/null 2>&1 &)
