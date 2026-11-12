# Entraînement de la partie GPT de XTTS-v2 sur les phrases de papa (CPU).
# usage: train_xtts.py epochs lr outdir
import os, sys, glob
os.environ["COQUI_TOS_AGREED"] = "1"
import torch
torch.set_num_threads(4)
from trainer import Trainer, TrainerArgs
from TTS.config.shared_configs import BaseDatasetConfig
from TTS.tts.configs.xtts_config import XttsAudioConfig
from TTS.tts.datasets import load_tts_samples
from TTS.tts.layers.xtts.trainer.gpt_trainer import GPTArgs, GPTTrainer, GPTTrainerConfig

epochs, lr, out = int(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
X = glob.glob("/root/.cache/huggingface/hub/models--tts-hub--XTTS-v2/snapshots/*/")[0]
DVAE = glob.glob("/root/.cache/huggingface/hub/models--coqui--XTTS-v2/snapshots/*/dvae.pth")[0]
ds = BaseDatasetConfig(formatter="coqui", dataset_name="papa", path="/root/voix/ds",
                       meta_file_train="/root/voix/ds/train.csv", meta_file_val="/root/voix/ds/eval.csv", language="fr")
args = GPTArgs(max_conditioning_length=132300, min_conditioning_length=66150, debug_loading_failures=False,
               max_wav_length=255995, max_text_length=250, mel_norm_file=X + "mel_stats.pth", dvae_checkpoint=DVAE,
               xtts_checkpoint=X + "model.pth", tokenizer_file=X + "vocab.json", gpt_num_audio_tokens=1026,
               gpt_start_audio_token=1024, gpt_stop_audio_token=1025, gpt_use_masking_gt_prompt_approach=True,
               gpt_use_perceiver_resampler=True)
config = GPTTrainerConfig(
    epochs=epochs, output_path=out, model_args=args, run_name="papa", project_name="papa",
    datasets=[ds], dashboard_logger="tensorboard", audio=XttsAudioConfig(sample_rate=22050, dvae_sample_rate=22050, output_sample_rate=24000),
    batch_size=2, batch_group_size=0, eval_batch_size=2, num_loader_workers=0, num_eval_loader_workers=0,
    eval_split_max_size=256, print_step=5, plot_step=1000, log_model_step=1000, save_step=100000, save_n_checkpoints=1,
    save_checkpoints=True, save_best_after=100000, print_eval=True, mixed_precision=False,
    optimizer="AdamW", optimizer_wd_only_on_weights=True,
    optimizer_params={"betas": [0.9, 0.96], "eps": 1e-8, "weight_decay": 1e-2},
    lr=lr, lr_scheduler="MultiStepLR", lr_scheduler_params={"milestones": [10**9], "gamma": 0.5, "last_epoch": -1},
    test_sentences=[])
model = GPTTrainer.init_from_config(config)
train, ev = load_tts_samples(config, eval_split=True, eval_split_max_size=256)
t = Trainer(TrainerArgs(restore_path=None, skip_train_epoch=False, start_with_eval=False, grad_accum_steps=2),
            config, output_path=out, model=model, train_samples=train, eval_samples=ev)
t.fit()
print("ENTRAINEMENT FINI", t.output_path, flush=True)
