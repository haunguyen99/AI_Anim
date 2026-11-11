# Joint `root` (đầu cây xương team, theo CTL_Main) KHÔNG được có skin; hông là `Root_M`.
# Kiểm:  .venv/Scripts/python.exe -I tools/fbx_root_skin.py check a.fbx [b.fbx ...]   (thoát mã 1 nếu root còn đỉnh)
# Sửa:   .venv/Scripts/python.exe -I tools/fbx_root_skin.py fix in.fbx out.fbx [tên mesh]   (cộng weight root vào Root_M, cluster root rỗng; tổng weight giữ nguyên)
# Mọi thứ khác trong FBX giữ nguyên từng byte (dùng khung của fbx_replace_mesh). Rút ra từ London MC 2026-11-06 (root ăn 277/1199 đỉnh → méo thân).
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
import fbx_replace_mesh as R
import fbx_remove_mesh as F


def meshes(f):
    for i, (o, pr) in f.obj.items():
        if o[0] == "Model" and pr[2] == "Mesh":
            yield i, f.name(i), {b: c for c, b in f.clusters(f.geometry(i))}


def weights(f, cid):
    cn = f.obj[cid][0]; a, w = F.child(cn, "Indexes"), F.child(cn, "Weights")
    if a is None or w is None: return np.zeros(0, int), np.zeros(0)
    return np.array(F.props(a[2], a[1])[0], int), np.array(F.props(w[2], w[1])[0], float)


def check(paths):
    bad = 0
    for p in paths:
        f = R.Fbx(p)
        for _, name, cl in meshes(f):
            n = len(weights(f, cl["root"])[0]) if "root" in cl else 0
            print("%-4s %s | %s: root ăn %d đỉnh" % ("LỖI" if n else "ok", os.path.basename(p), name, n)); bad += bool(n)
    return bad


def fix(src, dst, only=None):
    f = R.Fbx(src)
    for i, name, cl in meshes(f):
        if only and name != only: continue
        if "root" not in cl or "Root_M" not in cl: continue
        ir, wr = weights(f, cl["root"])
        if not len(ir): continue
        im, wm = weights(f, cl["Root_M"])
        d = {int(k): float(v) for k, v in zip(im, wm)}
        for k, v in zip(ir, wr): d[int(k)] = d.get(int(k), 0.0) + float(v)
        ks = np.array(sorted(d), int)
        rm = f.obj[cl["Root_M"]][0]
        R.set_arr(rm, "Indexes", "i", ks); R.set_arr(rm, "Weights", "d", np.array([d[k] for k in ks]))
        c = f.obj[cl["root"]][0]; c[3] = [k for k in c[3] if k[0] not in ("Indexes", "Weights")]
        print("mesh %s: %d đỉnh root -> Root_M (Root_M %d -> %d đỉnh)" % (name, len(ir), len(im), len(ks)))
    f.save(dst); print("ghi", dst)


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) >= 2 and a[0] == "check": sys.exit(1 if check(a[1:]) else 0)
    elif len(a) >= 3 and a[0] == "fix": fix(a[1], a[2], a[3] if len(a) > 3 else None)
    else: print(__doc__)
