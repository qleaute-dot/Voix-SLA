cd /root/voix
for E in 25 50 75 100 125 150 175 200 225 250 275 300; do
  until ls /root/applio/logs/papa/papa_${E}e_*.pth >/dev/null 2>&1; do grep -q "^EXIT" pipe/rvc2.log && exit 0; sleep 60; done
  bash pipe/rvc_test.sh $E >> pipe/rvc_watch.log 2>&1
done
