# Copie model_last.pt de l'entraînement F5 toutes les 300 mises à jour (garde les 2 dernières)
C=/root/voix/f5/lib/python3.11/ckpts/papa; S=/root/voix/f5snap; mkdir -p $S; last=""
while true; do
  if [ -f $C/model_last.pt ]; then
    m=$(stat -c %Y $C/model_last.pt)
    if [ "$m" != "$last" ]; then last=$m; sleep 30
      u=$(grep -oP "Saved last checkpoint at update \K\d+" /root/voix/f5t/ft.log | tail -1)
      if [ -n "$u" ] && [ $((u % 300)) -eq 0 ] && [ ! -f $S/u$u.pt ]; then
        cp $C/model_last.pt $S/u$u.pt; ls -t $S/u*.pt | tail -n +3 | xargs -r rm -f; echo "snap $u $(date +%H:%M)"
      fi
    fi
  fi
  pgrep -f f5-tts_finetune >/dev/null || { [ -f $C/model_last.pt ] && break; }
  sleep 60
done
