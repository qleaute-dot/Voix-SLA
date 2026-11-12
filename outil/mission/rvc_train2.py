import os, sys, time
os.chdir("/root/applio"); sys.path.insert(0, "/root/applio")
import core
E = int(sys.argv[1]); B = int(sys.argv[2])
t = time.time()
print(core.run_train_script("papa", 25, False, True, E, 40000, B, "-", True, False, "Auto"), round(time.time()-t), flush=True)
print("RVC FINI", flush=True)
