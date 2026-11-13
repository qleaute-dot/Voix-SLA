# Stocke une sauvegarde XTTS en demi-précision (2 Go -> 1 Go) ; rechargée en float32 à l'inférence
import sys, torch
f = sys.argv[1]; ck = torch.load(f, map_location="cpu", weights_only=False)
sd = ck["model"] if "model" in ck else ck
for k, v in sd.items():
    if torch.is_tensor(v) and v.is_floating_point(): sd[k] = v.half()
torch.save(ck, f + ".tmp"); import os; os.replace(f + ".tmp", f); print("ok", os.path.getsize(f) // 2**20, "Mo")
