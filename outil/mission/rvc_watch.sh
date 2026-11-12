cd /root/voix
for E in 10 20 30 40 50 60 70 80 90 100 110 120; do
  until ls /root/applio/logs/papa/papa_${E}e_*.pth >/dev/null 2>&1; do grep -q "^EXIT" pipe/rvc3.log && exit 0; sleep 60; done
  bash pipe/rvc_test.sh $E >> pipe/rvc_watch.log 2>&1
done
