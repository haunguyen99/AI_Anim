"""In cây xương + khoảng frame của một FBX (Mixamo hay team), để lập bảng nối xương.
    .venv/Scripts/python.exe -I tools/retarget/inspect_skel.py <file.fbx> [...]"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, ".."))
import numpy as np
import fbx_fast, fbxanim
fbxanim.fbxread.read = fbx_fast.read


def main():
    for p in sys.argv[1:]:
        m, par = fbxanim.load(p)
        kt = fbxanim.key_times(m)
        print("==", os.path.basename(p), "| models", len(m), "| có anim", sum(1 for v in m.values() if "anim" in v),
              "| frame (30fps)", (kt[0], kt[-1], len(kt)) if kt else None)

        def depth(k):
            d = 0
            while k in par:
                k = par[k]; d += 1
            return d
        for k, v in m.items():
            t = v["type"].split("\x00")[0]
            if t in ("LimbNode", "Null", "Root"):
                pre = v["props"].get("PreRotation")
                print("  " * depth(k) + v["name"], t, "ro", fbxanim.rot_order(v),
                      "pre", None if pre is None else np.round(pre[:3], 1),
                      "T", np.round(v["props"].get("Lcl Translation", [0, 0, 0])[:3], 2),
                      "anim", sorted(v.get("anim", {}).keys()))


if __name__ == "__main__":
    main()
