"""Tự kiểm một pose Ninja trên mesh đã skin (lấy từ Studio): xuyên mesh, giãn da, chạm sàn.

Lấy mesh đã pose: trong trang Studio (lớp Anim) chạy đoạn JS ghi `window.__posed` rồi PUT vào
/api/store/ninja_studio_tmp/posed/<tên> (xem lịch sử phiên 2026-10-29); file ở work/store/ninja_studio_tmp/posed/<tên>.json.
    .venv/Scripts/python.exe -I -X utf8 work/infinite_defense/ninja_idle/pose_check.py k10_v5
Trục three (cm): x trái nhân vật, y lên, z trước.
"""
import collections, json, os, sys
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
name = sys.argv[1] if len(sys.argv) > 1 else "k10_v5"
P = json.load(open(os.path.join(ROOT, "work", "store", "ninja_studio_tmp", "posed", name + ".json")))
B = {m["name"]: m for m in json.load(open(os.path.join(ROOT, "work", "store", "ninja_mesh_lab", "mesh", "edit.json")))["meshes"]}
body = np.array(P["body_ninja"]["pos"]).reshape(-1, 3); T = np.array(P["body_ninja"]["idx"]).reshape(-1, 3)
kun = np.array(P["weapon"]["pos"]).reshape(-1, 3)
bb = np.array(B["body_ninja"]["verts"]).reshape(-1, 3)        # bind (cùng thứ tự đỉnh)
NV = len(body)

par = list(range(NV))
def f(a):
    while par[a] != a: par[a] = par[par[a]]; a = par[a]
    return a
for a, b, c in T:
    for u, v in ((a, b), (b, c)): par[f(u)] = f(v)
cnt = collections.Counter(f(i) for i in range(NV)); mr = cnt.most_common(1)[0][0]
main = np.array([f(i) == mr for i in range(NV)])


def inside(pts, tris_idx):
    """Đếm số lần tia +X cắt tam giác (lẻ = ở trong). Möller–Trumbore."""
    A, Bv, C = body[tris_idx[:, 0]], body[tris_idx[:, 1]], body[tris_idx[:, 2]]
    e1, e2 = Bv - A, C - A; d = np.array([1.0, 0, 0])
    h = np.cross(d, e2); a = (e1 * h).sum(1); ok = np.abs(a) > 1e-9; inv = np.where(ok, 1 / np.where(ok, a, 1), 0)
    res = []
    for p in pts:
        s = p - A; uu = inv * (s * h).sum(1); q = np.cross(s, e1); vv = inv * (q @ d); t = inv * (q * e2).sum(1)
        hit = ok & (uu >= 0) & (vv >= 0) & (uu + vv <= 1) & (t > 1e-6)
        res.append(hit.sum() % 2 == 1)
    return np.array(res)


tri_main = T[main[T[:, 0]]]
# vùng theo tư thế bind
arm_R = (bb[:, 0] < -18) & (bb[:, 1] > 100); arm_L = (bb[:, 0] > 18) & (bb[:, 1] > 100)
hand_R = main & (bb[:, 0] < -60); hand_L = main & (bb[:, 0] > 60); fore_L = main & (bb[:, 0] > 40)
tri_noarm = tri_main[~(arm_R[tri_main].any(1) | arm_L[tri_main].any(1))]
report = []
k_in = inside(kun, tri_main); report.append(("kunai trong thân", int(k_in.sum()), len(kun)))
r_in = inside(body[hand_R], tri_noarm); report.append(("bàn tay phải trong thân/hông", int(r_in.sum()), int(hand_R.sum())))
l_in = inside(body[fore_L], tri_noarm); report.append(("cẳng tay + bàn tay trái trong thân", int(l_in.sum()), int(fore_L.sum())))
sc = ~main
s_in = inside(body[sc], tri_noarm); report.append(("khăn (mảnh rời) trong thân/chân", int(s_in.sum()), int(sc.sum())))
for k, n, tot in report: print(f"{k:38s} {n:4d} / {tot}")
# kunai: khoảng cách gần nhất tới thân (không tính bàn tay trái)
others = body[main & ~fore_L]
dmin = min(np.min(np.linalg.norm(others - p, axis=1)) for p in kun)
print("kunai cách thân (trừ tay trái) gần nhất: %.1f cm" % dmin)
# sàn
print("thấp nhất thân: %.2f cm, kunai: %.2f cm, khăn: %.2f cm" % (body[main][:, 1].min(), kun[:, 1].min(), body[sc][:, 1].min()))
# giãn da (cạnh thân chính)
E = set()
for a, b, c in tri_main:
    for u, v in ((a, b), (b, c), (c, a)): E.add((min(u, v), max(u, v)))
E = np.array(sorted(E)); l0 = np.linalg.norm(bb[E[:, 0]] - bb[E[:, 1]], axis=1); l1 = np.linalg.norm(body[E[:, 0]] - body[E[:, 1]], axis=1)
m = l0 > 0.8; r = l1[m] / l0[m]; Em = E[m]
bad = (r > 1.25) | (r < 0.75)
print("cạnh giãn/co quá 25%%: %d / %d (%.1f%%), tệ nhất giãn %.0f%%, co %.0f%%" % (bad.sum(), len(r), 100 * bad.mean(), 100 * (r.max() - 1), 100 * (1 - r.min())))
# vùng của cạnh hỏng (theo vị trí bind)
def zone(p):
    x, y = p[0], p[1]
    if y < 14: return "bàn chân"
    if y < 45: return "gối/ống chân"
    if y < 70: return "hông/đùi"
    if abs(x) > 22 and y > 100: return "tay" + ("_L" if x > 0 else "_R")
    if y > 135: return "đầu/cổ"
    return "thân"
z = collections.Counter(zone((bb[a] + bb[b]) / 2) for a, b in Em[bad])
print("vùng có cạnh hỏng:", dict(z.most_common()))
