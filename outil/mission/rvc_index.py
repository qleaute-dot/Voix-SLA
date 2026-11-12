import os, sys
os.chdir("/root/applio"); sys.path.insert(0, "/root/applio")
import core
print(core.run_index_script("papa", "Auto"))
