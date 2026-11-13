# Entraînement F5-TTS (français) sur les 66 extraits de papa, CPU. Attend la fin du test F5.
cd /root/voix
while pgrep -f "f5_post.sh|gen_f5b.py" >/dev/null; do sleep 30; done
export WANDB_MODE=disabled OMP_NUM_THREADS=4
f5/bin/f5-tts_finetune-cli --exp_name F5TTS_Base --dataset_name papa --finetune \
  --pretrain /root/.cache/huggingface/hub/models--RASPIAUDIO--F5-French-MixedSpeakers-reduced/snapshots/bcad6ae266c8406dc572b33d1d6ffced4db114fe/model_last_reduced.pt \
  --tokenizer custom --tokenizer_path /root/voix/f5/lib/python3.11/data/papa_custom/vocab.txt \
  --learning_rate 1e-5 --batch_size_per_gpu 3000 --batch_size_type frame --max_samples 16 \
  --epochs 200 --num_warmup_updates 50 --save_per_updates 1000000 --last_per_updates 60 \
  --keep_last_n_checkpoints 0
echo FTF5FINI
