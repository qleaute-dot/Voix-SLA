# Garde seulement la dernière sauvegarde complète G/D d'Applio (≈ 1,3 Go chacune)
cd /root/applio/logs/papa
while true; do
  for k in G D; do ls -t ${k}_*.pth 2>/dev/null | tail -n +2 | xargs -r rm -f; done
  sleep 120
done
