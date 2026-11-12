until [ -f /root/voix/f5zs/c021/e4_0.wav ]; do sleep 10; done
pkill -f run_f5_zs.sh; pkill -f "gen_f5.py pipe/f5_items.json f5zs/c047"; echo C021FINI
