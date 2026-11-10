"""Giảm key (2026-11-05, người dùng: "đang như mocap, quá nhiều key không cần thiết ... chỉ để những key chính mà vẫn
giữ được chuyển động y nguyên"): mẫu theo frame -> ít key Spine nhất, đường cong bezier liền mượt, lệch <= tol ở MỌI frame.

Cách làm:
  1. key bắt đầu: F đầu, F cuối, các đỉnh rõ (cực trị cao hơn hẳn hai bên) + frame bắt buộc (keep, vd keypose người dùng);
  2. độ dốc tại mỗi key DÙNG CHUNG cho đoạn trước và sau (đường liền, không gãy), tính bằng bình phương tối thiểu trên
     mọi frame -> mỗi đoạn là Hermite = bezier Spine có tay cầm ở 1/3 và 2/3 đoạn;
  3. còn frame lệch > tol thì thêm key đúng frame lệch nhất, lặp lại.
Loop (periodic): độ dốc F cuối = F đầu -> nối vòng không gãy.

Dùng: reduce_keys(chans, fields, tol, periodic=False, keep=(), fps=30) -> list key Spine (time giây, curve bezier).
  chans: mỗi kênh một list giá trị frame 0..N (vd [[rot...]] hoặc [[x...], [y...]]), cùng key cho mọi kênh.
Ngưỡng hay dùng: xoay 0.15°, dời 0.3 px (chân IK / chậu 0.2), scale 0.003.
"""
import math
import numpy as np

def ktime(t, fps=30):
    """thời gian key an toàn (2026-11-10, rà soát Spine Live): key nằm đúng frame -> ghi SỚM hơn mốc frame 0.00001 s,
    không bao giờ muộn (round(2/30, 4) = 0.0667 > 0.066667 làm key stepped / đổi ảnh hiện trễ 1 frame khi lấy mẫu f/fps;
    float32 của 0.1 cũng > 0.1). Key không nằm đúng frame: làm tròn 5 chữ số."""
    t = float(t)
    if t <= 0:
        return 0.0
    f = t * fps; r = round(f)
    if abs(f - r) < 0.02:
        return math.floor(r / fps * 1e5 - 0.5) / 1e5
    return round(t, 5)


TOL = {"rotate": 0.15, "translate": 0.3, "scale": 0.003, "shear": 0.15}


def _extrema(v, tol):
    n = len(v) - 1
    out = set()
    for x in range(1, n):
        lo, hi = max(0, x - 3), min(n, x + 3)
        win = v[lo:hi + 1]
        if (v[x] >= max(win) or v[x] <= min(win)) and max(abs(v[x] - v[lo]), abs(v[x] - v[hi])) > 3 * tol:
            if not any(abs(x - o) <= 1 for o in out):
                out.add(x)
    return out


def _fit(V, ks, periodic):
    """V: (C, N+1). Độ dốc chung mỗi key (giá trị / frame) theo bình phương tối thiểu -> (slopes (C, K), fit (C, N+1))."""
    C, N1 = V.shape
    n = N1 - 1
    K = len(ks)
    col = list(range(K))
    if periodic:
        col[-1] = 0                     # độ dốc F cuối = F đầu
    ncol = max(col) + 1
    rows, rhs_rows = [], []
    seg = []
    for j in range(K - 1):
        a, b = ks[j], ks[j + 1]
        h = b - a
        for x in range(a + 1, b):
            t = (x - a) / h
            h00 = 2 * t ** 3 - 3 * t ** 2 + 1; h10 = t ** 3 - 2 * t ** 2 + t
            h01 = -2 * t ** 3 + 3 * t ** 2;    h11 = t ** 3 - t ** 2
            r = np.zeros(ncol); r[col[j]] += h10 * h; r[col[j + 1]] += h11 * h
            rows.append(r); seg.append((x, a, b, h00, h01))
    # neo nhẹ về độ dốc sai phân (đoạn ngắn không có frame giữa vẫn xác định được)
    lam = 0.05
    fd = np.gradient(V, axis=1) if N1 > 1 else np.zeros_like(V)
    if periodic and N1 > 2:
        fd[:, 0] = fd[:, -1] = (V[:, 1] - V[:, -2]) / 2
    reg = []
    for j in range(K):
        r = np.zeros(ncol); r[col[j]] = lam; reg.append((r, ks[j]))
    A = np.array(rows + [r for r, _ in reg]) if rows else np.array([r for r, _ in reg])
    S = np.zeros((C, K))
    fit = V.copy()
    for c in range(C):
        b = [V[c, x] - h00 * V[c, a] - h01 * V[c, bb] for (x, a, bb, h00, h01) in seg] + [lam * fd[c, k] for _, k in reg]
        m, *_ = np.linalg.lstsq(A, np.array(b), rcond=None)
        S[c] = [m[col[j]] for j in range(K)]
        for (x, a, bb, h00, h01), r in zip(seg, rows):
            fit[c, x] = h00 * V[c, a] + h01 * V[c, bb] + r @ m
    return S, fit


def reduce_keys(chans, fields, tol, periodic=False, keep=(), fps=30, rnd=4):
    V = np.array(chans, dtype=float)
    if V.ndim == 1:
        V = V[None, :]
    n = V.shape[1] - 1
    if n <= 0 or float(np.max(V.max(axis=1) - V.min(axis=1))) < 1e-9:
        return [{fld: round(float(V[c, 0]), rnd) for c, fld in enumerate(fields)}]
    periodic = periodic and float(np.max(np.abs(V[:, 0] - V[:, -1]))) < max(tol, 1e-6)
    ks = {0, n} | {int(k) for k in keep if 0 <= int(k) <= n}
    for c in range(V.shape[0]):
        ks |= _extrema(list(V[c]), tol)
    while True:
        k = sorted(ks)
        S, fit = _fit(V, k, periodic)
        err = np.max(np.abs(fit - V), axis=0)
        worst = int(np.argmax(err))
        if err[worst] <= tol or worst in ks or len(ks) >= n + 1:
            break
        ks.add(worst)
    k = sorted(ks)
    out = []
    for j, f in enumerate(k):
        key = {} if f == 0 else {"time": ktime(f / fps, fps)}
        for c, fld in enumerate(fields):
            key[fld] = round(float(V[c, f]), rnd)
        if j + 1 < len(k):
            f1 = k[j + 1]; h = (f1 - f) / 3; cv = []
            for c in range(V.shape[0]):
                cv += [round((f + h) / fps, 6), round(float(V[c, f] + S[c, j] * h), rnd),
                       round((f1 - h) / fps, 6), round(float(V[c, f1] - S[c, j + 1] * h), rnd)]
            key["curve"] = cv
        out.append(key)
    return out


# ---------------------------------------------------------------- đọc timeline Spine -> mẫu theo frame
def _bez(p0, c1, c2, p3, x):
    lo, hi = 0.0, 1.0
    for _ in range(50):
        t = (lo + hi) / 2
        xt = (1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * c1[0] + 3 * (1 - t) * t * t * c2[0] + t ** 3 * p3[0]
        if xt < x:
            lo = t
        else:
            hi = t
    t = (lo + hi) / 2
    return (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * c1[1] + 3 * (1 - t) * t * t * c2[1] + t ** 3 * p3[1]


def sample_timeline(keys, fields, n, fps=30, defaults=None):
    """key Spine 4.2 (curve bezier [cx1, cy1, cx2, cy2] mỗi kênh / "stepped" / thẳng) -> mẫu mỗi frame 0..n theo kênh."""
    defaults = defaults or {}
    out = [[] for _ in fields]
    for f in range(n + 1):
        t = f / fps
        for c, fld in enumerate(fields):
            dv = defaults.get(fld, 0.0)
            if not keys:
                out[c].append(dv); continue
            if t <= keys[0].get("time", 0):
                out[c].append(keys[0].get(fld, dv)); continue
            v = keys[-1].get(fld, dv)
            for a, b in zip(keys, keys[1:]):
                ta, tb = a.get("time", 0), b.get("time", 0)
                if ta <= t <= tb and tb > ta:
                    va, vb = a.get(fld, dv), b.get(fld, dv)
                    cv = a.get("curve")
                    if cv == "stepped":
                        v = va if t < tb else vb
                    elif isinstance(cv, list) and len(cv) >= 4 * (c + 1):
                        q = cv[4 * c:4 * c + 4]
                        v = _bez((ta, va), (q[0], q[1]), (q[2], q[3]), (tb, vb), t)
                    else:
                        v = va + (vb - va) * (t - ta) / (tb - ta)
                    break
            out[c].append(v)
    return out


def has_stepped(keys):
    return any(k.get("curve") == "stepped" for k in keys)
