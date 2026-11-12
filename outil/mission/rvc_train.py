import os, sys, time
os.chdir("/root/applio"); sys.path.insert(0, "/root/applio")
import core
E = int(sys.argv[1]) if len(sys.argv) > 1 else 300
t = time.time()
print(core.run_prerequisites_script(pretraineds_hifigan=True, models=True, exe=False), round(time.time()-t), flush=True)
print(core.run_preprocess_script("papa", "/root/voix/rvc_ds", 40000, 4, "Automatic", False, 3.0, 0.3, "none"), flush=True)
print(core.run_extract_script("papa", "rmvpe", 4, "-", 40000, "contentvec"), round(time.time()-t), flush=True)
print(core.run_train_script("papa", 25, False, True, E, 40000, 8, "-", True, False, "Auto"), round(time.time()-t), flush=True)
print("RVC FINI", flush=True)
