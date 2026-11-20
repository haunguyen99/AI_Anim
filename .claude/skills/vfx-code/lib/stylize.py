"""stylize: kỹ thuật toon / pixel rút từ minerva-studio/pixel-effect-generator (MIT), RetroImpacts,
Pixel FX Forge, deepnight HParticle (xem references/sources.md).

  field_bands   một trường quyết định cả viền lẫn bậc màu
  carve         nhám chỉ ăn vào trong
  puff_cluster  cụm metaball nổ / khói có nhiệt lồng trong viền
  id_edges      nét toon tự động (viền ngoài + nét giữa các khối chồng nhau)
  drag_travel   luật hãm chung cho vòng xung kích
  env_punch     đường năng lượng đòn đánh (fighting game)
  slash_arc     vệt chém theo toạ độ cực (đầu / đuôi / mũi thon)
  dissolve_mask bộ dissolve 1 tham số: bayer / block / scan / edge / circles
  keep_components dọn vụn: giữ khối gốc + N mảnh lớn nhất
"""
import math

import numpy as np

from fxlib import TAU, _hashf, cov_field, sat, smoothstep, voronoi


def field_bands(E, heat, n=4):
    """MỘT trường quyết định cả viền lẫn bậc màu (minerva fieldBodies): hình = E > 0,
    bậc = floor((1 - heat)·n). Viền và tông luôn đi cùng nhau, không cần mask riêng.
    Trả (độ phủ mép 1 px, chỉ số bậc 0..n-1; 0 = nóng nhất)."""
    band = np.clip(np.floor((1 - sat(heat)) * n), 0, n - 1).astype(int)
    return cov_field(-np.asarray(E)), band


def carve(E, grit, amount=0.3):
    """Nhám CHỈ ĂN VÀO TRONG (minerva): E' = E - amount·max(grit, 0). Noise không bao giờ làm phình viền."""
    return np.asarray(E) - amount * np.maximum(np.asarray(grit), 0)


def puff_cluster(X, Y, puffs, thr=0.25):
    """Cụm metaball nổ / khói (minerva renderPuffClusterBody).
    puffs: list (x, y, r, weight, temp). Mỗi puff cộng k = (1 - d²)²·w vào mật độ, k·temp vào nhiệt.
    Trả (E = mật độ - thr, heat 0..1 lồng trong viền: heat → 0 ở silhouette).
    Gợi ý động: travel = D·drag_travel(age); bay lên y -= b·age²; puff nhanh nguội trước;
    thr tăng muộn (0.25 → 0.6) → thủng chỗ mỏng trước, cụm tự thắt lại.
    Khói toon của dự án vẫn là thân + thuỳ bám sát (SKILL.md §0) — puff_cluster cho NỔ / quả cầu lửa."""
    den = np.zeros(np.shape(X))
    ht = np.zeros(np.shape(X))
    for x, y, r, w, tmp in puffs:
        d2 = ((X - x) ** 2 + (Y - y) ** 2) / (r * r)
        k = np.where(d2 < 1, (1 - d2) ** 2, 0) * w
        den += k
        ht += k * tmp
    interior = sat((den - thr) / 0.9)
    heat = np.where(den > 1e-6, ht / np.maximum(den, 1e-6), 0) * interior ** 0.55
    return den - thr, sat(heat)


def id_edges(ids, alpha=None):
    """Nét toon tự động (minerva renderVolumeBody): pixel giáp pixel trống hoặc giáp khối KHÁC id → nét.
    ids: mảng nhãn khối (số nguyên, -1 = trống). Trả mặt nạ 0/1."""
    ids = np.asarray(ids)
    e = np.zeros(ids.shape, bool)
    for ax, s in ((0, 1), (0, -1), (1, 1), (1, -1)):
        e |= (ids >= 0) & (np.roll(ids, s, ax) != ids)
    if alpha is not None:
        e &= np.asarray(alpha) > 0.5
    return e.astype(float)


def drag_travel(age, K=7.0):
    """Luật hãm chung (minerva shock plates): 0 → 1, bắn nhanh rồi phanh, đúng 1 ở age = 1.
    Dùng chung cho mép trước và mép sau của vòng → vòng ép dần thành viền 1 px khi tan."""
    a = np.asarray(age, dtype=np.float64)
    return (1 - np.exp(-K * a)) / (1 - math.exp(-K))


def env_punch(t, rise=0.23, decay=4.2, floor=0.1):
    """Năng lượng đòn đánh kiểu fighting game (RetroImpacts): lên tuyến tính tới `rise` (s), rồi tắt mũ."""
    t = np.asarray(t, dtype=np.float64)
    return np.where(t < rise, 0.45 + 0.55 * t / rise, (1 - floor) * np.exp(-decay * (t - rise)) + floor)


def slash_arc(X, Y, R, width, a0, a1, t, head_end=0.35, tail_start=0.3, taper=0.25, tilt=0.0):
    """Vệt chém theo toạ độ cực (minerva slash): đầu chạy out_cubic tới hết ở head_end,
    đuôi đuổi theo smoothstep từ tail_start, mũi thon theo độ dài cung. a0 → a1 (radian) = chiều chém.
    tilt: ép dẹt y/cos(tilt) cho mặt phẳng nghiêng.
    Trả (SDF âm bên trong, v 0..1 ngang dải [trong → ngoài], s 0..1 dọc cung [đuôi → đầu]).
    Dự án: vệt chém dùng mesh + UV; hàm này vẽ TEXTURE vệt, giữ bố cục UV gốc."""
    yy = Y / max(math.cos(tilt), 1e-3)
    rho = np.hypot(X, yy)
    ang = np.arctan2(yy, X)
    sgn = 1 if a1 >= a0 else -1
    span = abs(a1 - a0)
    along = np.mod((ang - a0) * sgn, TAU) / max(span, 1e-6)          # 0 ở a0 → 1 ở a1
    head = 1 - (1 - min(t / head_end, 1.0)) ** 3
    k = min(max((t - tail_start) / (1 - tail_start), 0.0), 1.0)
    tail = k * k * (3 - 2 * k)
    s = (along - tail) / max(head - tail, 1e-6)
    inside = (along >= tail) & (along <= head)
    arc_len = np.minimum(along - tail, head - along) * span * R
    w = width * smoothstep(0, taper * span * R, arc_len)
    d = np.where(inside, np.abs(rho - R) - w / 2, 1e3)
    return d, sat((rho - (R - width / 2)) / max(width, 1e-6)), sat(s)


_BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0 + 1 / 32


def dissolve_mask(kind, shape, amount, seed=0, cell=4, dist_edge=None, X=None, Y=None):
    """Mặt nạ GIỮ (0/1). amount 0 = nguyên, 1 = mất hết. shape = (H, W) pixel.
      bayer    dither có trật tự 4×4 (pixel / retro)
      block    khối cell×cell tắt theo hash (arcade)
      scan     quét chéo (x + y) có rung
      edge     ăn từ mép vào (cần dist_edge 0..1: khoảng cách tới mép đã chuẩn hoá)
      circles  lỗ tròn mở dần theo ô voronoi (cần X, Y; cell = cỡ ô)"""
    H, W = shape
    yy, xx = np.mgrid[0:H, 0:W]
    if kind == "bayer":
        return (_BAYER4[yy % 4, xx % 4] >= amount).astype(float)
    if kind == "block":
        return (_hashf(xx // cell, yy // cell, seed) >= amount).astype(float)
    if kind == "scan":
        f = (xx + yy) / float(W + H) + (_hashf(xx // 2, yy // 2, seed) - 0.5) * 0.08
        return (f >= amount * 1.1 - 0.05).astype(float)
    if kind == "edge":
        j = _hashf(xx // 2, yy // 2, seed)
        return ((np.asarray(dist_edge) + j * amount * 0.5) > amount).astype(float)
    if kind == "circles":
        f1, _, cid = voronoi(np.asarray(X) / cell, np.asarray(Y) / cell, seed)
        rad = np.clip((amount - cid * 0.6) / 0.4, 0, 1) * 0.75
        return (f1 > rad).astype(float)
    raise ValueError(kind)


def keep_components(mask, n_keep=3, root_row=None):
    """Dọn vụn (minerva erodeFlameEdge): giữ khối nối với hàng gốc (root_row, vd đáy lửa = -1)
    + n_keep mảnh lớn nhất; bỏ mọi chấm lẻ. Không cần scipy (gán nhãn 2 lượt + union-find)."""
    m = np.asarray(mask) > 0.5
    H, W = m.shape
    lab = np.zeros((H, W), int)
    parent = [0]

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    nxt = 1
    for y in range(H):
        row = m[y]
        for x in np.nonzero(row)[0]:
            l = lab[y, x - 1] if x and row[x - 1] else 0
            u = lab[y - 1, x] if y and m[y - 1, x] else 0
            if l and u:
                a, b = find(l), find(u)
                lab[y, x] = min(a, b)
                parent[max(a, b)] = min(a, b)
            elif l or u:
                lab[y, x] = l or u
            else:
                parent.append(nxt)
                lab[y, x] = nxt
                nxt += 1
    roots = np.array([find(i) for i in range(nxt)])
    lab = roots[lab]
    if not (lab > 0).any():
        return np.zeros((H, W))
    ids, cnt = np.unique(lab[lab > 0], return_counts=True)
    keep = set(ids[np.argsort(-cnt)][:n_keep].tolist())
    if root_row is not None:
        r = lab[root_row]
        keep |= set(np.unique(r[r > 0]).tolist())
    return np.isin(lab, list(keep)).astype(float)
