"""Stack look_<frame>.png images for several frames into one sheet (for quick eye review).
python tools/lookgrid.py WORK 6,11,16,21 [--out look/grid.png]"""
import os, sys
import cv2, numpy as np
work, frames = sys.argv[1], [int(x) for x in sys.argv[2].split(",")]
out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "look/grid.png"
ims = [cv2.imread(os.path.join(work, "look", f"look_{f:05d}.png")) for f in frames]
w = max(i.shape[1] for i in ims)
cv2.imwrite(os.path.join(work, out), np.vstack([np.pad(i, ((0, 0), (0, w - i.shape[1]), (0, 0))) for i in ims]))
print(os.path.join(work, out))
