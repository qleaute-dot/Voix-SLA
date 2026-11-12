# usage: rvc_conv.py model.pth in_dir out_dir [pitch] [index_rate] [protect]
import os, sys, glob
os.chdir("/root/applio"); sys.path.insert(0, "/root/applio")
import core
pth, ind, outd = sys.argv[1], sys.argv[2], sys.argv[3]
pitch = int(sys.argv[4]) if len(sys.argv) > 4 else 0
ir = float(sys.argv[5]) if len(sys.argv) > 5 else 0.6
prot = float(sys.argv[6]) if len(sys.argv) > 6 else 0.33
idx = (glob.glob("/root/applio/logs/papa/*.index") or [""])[0]
os.makedirs(outd, exist_ok=True)
for f in sorted(glob.glob(ind + "/*_0.wav")):
    o = os.path.join(outd, os.path.basename(f))
    if os.path.exists(o): continue
    core.run_infer_script(pitch, ir, 1.0, prot, "rmvpe", f, o, pth, idx, False, 1.0, False, 155.0, "WAV", "contentvec")
    print("conv", os.path.basename(f), flush=True)
