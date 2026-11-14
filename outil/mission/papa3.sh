# Applio papa3 : même jeu que papa2 (enregistrement + extraits vidéo confirmés), 60 époques au lieu de 20
cd /root/voix
until grep -q REPRISEFINI n5/log2.txt; do sleep 30; done
( while pgrep -f papa3.sh >/dev/null; do cd /root/applio/logs/papa3 2>/dev/null && ls -t G_*.pth D_*.pth 2>/dev/null | tail -n +3 | xargs -r rm -f; sleep 60; done ) &
rvc/bin/python - <<'PY'
import os, sys, time
os.chdir("/root/applio"); sys.path.insert(0, "/root/applio"); import core
t = time.time()
print(core.run_preprocess_script("papa3", "/root/voix/rvc_ds2", 40000, 4, "Automatic", False, 3.0, 0.3, "none"), flush=True)
print(core.run_extract_script("papa3", "rmvpe", 4, "-", 40000, "contentvec"), round(time.time()-t), flush=True)
print(core.run_train_script("papa3", 20, True, True, 60, 40000, 4, "-", True, False, "Auto"), round(time.time()-t), flush=True)
print(core.run_index_script("papa3", "Auto"), round(time.time()-t), flush=True)
PY
rm -f /root/applio/logs/papa3/G_*.pth /root/applio/logs/papa3/D_*.pth
ls /root/applio/logs/papa3/*.pth; echo PAPA3FINI
