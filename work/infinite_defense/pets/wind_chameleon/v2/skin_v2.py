"""Skin v2 cho mesh moi Pet_Wind_Chameleon (741 dinh: than 562 + luoi 89 + 2 mat 45). Chay ngoai Frolvy (python3 -I, khong numpy).
Dau vao: /tmp/wc_new.json (mesh_data cua mesh moi, xoay 180 + freeze), /tmp/wc_old.json (trong so cu de so sanh).
Dau ra: /tmp/wc_weights_v2.json {idx, rows} -> apply_skin_v2.py ap vao Frolvy.
Logic = rig/skin.py cu (vung + lam muc theo canh), chinh theo hinh khoi moi: mieng la ONG TRON nho (r .038) o (0,.322,z .406-.489), mat = 2 mang roi, luoi z .316-.735."""
import json, math, heapq, re, sys
def ramp(v, a, b):
    t = (v - a) / (b - a); return max(0.0, min(1.0, t))
def sm(t): return t*t*(3-2*t)
def dist(a, b): return math.sqrt(sum((a[i]-b[i])**2 for i in range(3)))
TAIL = [(0, .21, -.30), (0, .27, -.43), (0, .41, -.46), (0, .55, -.41), (0, .66, -.33), (0, .70, -.17), (0, .62, -.04), (0, .51, -.06), (0, .48, -.16), (0, .56, -.21)]
SPINE = [("DEF_Root_M", (0, .20, -.12)), ("DEF_Spine1_M", (0, .26, -.02)), ("DEF_Chest_M", (0, .33, .08)), ("DEF_Neck_M", (0, .40, .15)), ("DEF_Head_M", (0, .45, .22))]
TCH = [("DEF_Root_M", (0, .20, -.12))] + [("DEF_Tail%d_M" % (i+1), p) for i, p in enumerate(TAIL)]
EYE_C = (0.19, 0.465, 0.285)   # tam vom mat trang tren dau (|x|)
MOUTH = (0.0, 0.322, 0.447)     # tam ong mieng (moi)
JAW_Y = 0.300                   # duong cat ham: duoi ong mieng (day ong y .306)
def proj(p, chain):
    best = None
    for i in range(len(chain)-1):
        a = chain[i][1]; b = chain[i+1][1]; ab = [b[k]-a[k] for k in range(3)]; L2 = sum(c*c for c in ab)
        t = max(0.0, min(1.0, sum((p[k]-a[k])*ab[k] for k in range(3)) / L2)); q = [a[k]+ab[k]*t for k in range(3)]
        d = dist(p, q)
        if best is None or d < best[0]: best = (d, i, t)
    d, i, t = best; t = sm(t)
    return d, {chain[i][0]: 1-t, chain[i+1][0]: t}
def norm(w):
    r = sorted([(j, v) for j, v in w.items() if v > 0.01], key=lambda t: -t[1])[:4]; t = sum(v for _, v in r); return [(j, v/t) for j, v in r]
SJ = [0.0]
for i in range(1, len(TCH)): SJ.append(SJ[-1] + dist(TCH[i-1][1], TCH[i][1]))
def hat(s):
    if s <= SJ[1]: return {TCH[1][0]: 1.0}
    if s >= SJ[-1]: return {TCH[-1][0]: 1.0}
    for i in range(1, len(SJ) - 1):
        if SJ[i] <= s <= SJ[i+1]:
            u = sm((s - SJ[i]) / (SJ[i+1] - SJ[i])); return {TCH[i][0]: 1 - u, TCH[i+1][0]: u}
def body_row(p, tail_flag, arcs=None):
    x, y, z = p; ax = abs(x); s = "L" if x > 0 else "R"
    dB, wB = proj(p, SPINE); dT, wT = proj(p, TCH)
    if tail_flag and arcs is not None: base = dict(hat(arcs))
    elif tail_flag: base = dict(wT if (y >= 0.45 or z <= -0.26) else proj(p, TCH[:3])[1])
    else: base = dict(wB)
    def over(wt, jn):
        if wt <= 0: return
        for k in base: base[k] *= (1 - wt)
        base[jn] = base.get(jn, 0) + wt
    if not tail_flag:
        c = sm(ramp(y, 0.54, 0.66)) * ramp(0.30, z, 0.22) * ramp(z, -0.02, 0.06)
        over(c * 0.85, "DEF_Crest_M")
        em = math.sqrt((ax / 0.065) ** 2 + ((y - MOUTH[1]) / 0.065) ** 2)           # ong mieng + vanh quanh no
        over((1 - sm(ramp(em, 0.9, 1.5))) * sm(ramp(z, 0.30, 0.38)), "DEF_Mouth_M")
        jw = sm(ramp(JAW_Y - y, 0.0, 0.07)) * sm(ramp(y, 0.15, 0.20)) * sm(ramp(z, 0.20, 0.31)) * ramp(0.19, ax, 0.12)
        over(jw, "DEF_Jaw_M")
        de = dist(p, (EYE_C[0] if x > 0 else -EYE_C[0], EYE_C[1], EYE_C[2])); over(1 - sm(ramp(de, 0.08, 0.115)), "DEF_Eye_" + s)   # mat = vom trang tren dau (texture), cau xanh o ma la MA
    x0 = 0.05 + 0.05 * sm(ramp(y, 0.06, 0.16))        # ban chan thap: mep trong lan can than cung theo chan (mesh moi co de phang)
    lw = sm(ramp(0.23 - y, 0.0, 0.08)) * sm(ramp(ax, x0, x0 + 0.05))
    if lw > 0 and not (tail_flag and z < -0.3):
        fr = sm(ramp(z, -0.01, 0.04)); pre = "F" if fr > 0.5 else "R"
        hip, ank, toe = "DEF_%sHip_%s" % (pre, s), "DEF_%sAnkle_%s" % (pre, s), "DEF_%sToes_%s" % (pre, s)
        tz = 0.24 if pre == "F" else -0.10; az = 0.15 if pre == "F" else -0.17
        wa = sm(ramp(0.17 - y, 0.0, 0.08)); wt = sm(ramp(abs(z - az), 0.02, 0.08)) * (1 if ((z - az) * (tz - az)) > 0 else 0) * ramp(0.10, y, 0.05)
        over(lw, hip)
        if wa > 0:
            moved = base[hip] * wa; base[hip] -= moved; base[ank] = moved
            if wt > 0: m2 = base[ank] * wt; base[ank] -= m2; base[toe] = m2
    return norm(base)
def build(new, old=None, out="/tmp/wc_weights_v2.json"):
    idx = new["idx"]; P3 = new["P"]; n = len(idx)
    P = [P3[i*3:i*3+3] for i in range(n)]
    nb = [set() for _ in range(n)]; c = 0; par = list(range(n))
    def f(a):
        while par[a] != a: par[a] = par[par[a]]; a = par[a]
        return a
    for s in new["fs"]:
        cs = new["fc"][c:c+s]; c += s
        for a in range(s):
            nb[cs[a]].add(cs[(a+1) % s]); nb[cs[(a+1) % s]].add(cs[a]); par[f(cs[a])] = f(cs[0])
    comps = {}
    for i in range(n): comps.setdefault(f(i), []).append(i)
    comps = sorted(comps.values(), key=lambda v: -len(v))
    body = comps[0]; rest = comps[1:]
    tongue = [v for v in rest if len(v) == 89 or max(P[i][2] for i in v) > 0.6][0]
    eyes = [v for v in rest if v is not tongue]
    for i in tongue: P[i] = [P[i][0], P[i][1], P[i][2] + TONGUE_SHIFT]
    rows = [None] * n
    bset = set(body)
    # ---- than ----
    lab = {}
    for i in body:
        p = P[i]; x, y, z = p; dB = proj(p, SPINE)[0]; dT = proj(p, TCH)[0]
        if (z < -0.12 and dT < dB) or (y > 0.55 and z < -0.02 and dT < dB): lab[i] = True
        elif z > -0.02 or dB < 0.12 or (z < -0.12 and dT >= dB): lab[i] = False
        else: lab[i] = None
    front = [i for i in body if lab[i] is not None]
    while front:
        nxt = []
        for i in front:
            for m in nb[i]:
                if lab.get(m, 1) is None: lab[m] = lab[i]; nxt.append(m)
        front = nxt
    arc = {}; hp = []
    for i in body:
        p = P[i]
        if lab[i] and -0.34 <= p[2] <= -0.26 and p[1] < 0.32: arc[i] = SJ[1]; hp.append((SJ[1], i))
    heapq.heapify(hp)
    while hp:
        d, i = heapq.heappop(hp)
        if d > arc[i] + 1e-9: continue
        for m in nb[i]:
            if m not in bset or not lab[m]: continue
            nd = d + dist(P[i], P[m])
            if m not in arc or nd < arc[m] - 1e-9: arc[m] = nd; heapq.heappush(hp, (nd, m))
    def sproj(p):
        best = None
        for i in range(len(TCH) - 1):
            a = TCH[i][1]; b = TCH[i+1][1]; ab = [b[k] - a[k] for k in range(3)]; L2 = sum(cc * cc for cc in ab)
            u = max(0.0, min(1.0, sum((p[k] - a[k]) * ab[k] for k in range(3)) / L2)); q = [a[k] + ab[k] * u for k in range(3)]
            d = dist(p, q)
            if best is None or d < best[0]: best = (d, SJ[i] + u * (SJ[i+1] - SJ[i]))
        return best[1]
    for i in body:
        if i in arc and lab[i] and P[i][2] > -0.40 and P[i][1] < 0.35: arc[i] = min(arc[i], sproj(P[i]))
    print("than", len(body), "duoi", sum(1 for i in body if lab[i]), "co cung", len(arc), "khong cung (duoi)", sum(1 for i in body if lab[i] and i not in arc))
    R = {i: dict(body_row(P[i], lab[i], arc[i] if (lab[i] and i in arc and (P[i][2] < -0.26 or P[i][1] >= 0.45)) else None)) for i in body}
    EYE = {"DEF_Eye_L", "DEF_Eye_R"}
    for _ in range(3):
        new_r = {}
        for i in body:
            r = R[i]
            nbb = [m for m in nb[i] if m in bset]
            if not nbb: new_r[i] = r; continue
            acc = {}
            for j, v in r.items(): acc[j] = acc.get(j, 0) + 0.5 * v
            for m in nbb:
                for j, v in R[m].items(): acc[j] = acc.get(j, 0) + 0.5 * v / len(nbb)
            new_r[i] = dict(norm(acc))
        R = new_r
    def _tn(j):
        m = re.match(r"DEF_Tail(\d+)_M", j); return int(m.group(1)) if m else 0
    for i in body:
        r = R[i]; z = P[i][2]; y = P[i][1]
        if z > -0.26 and y < 0.45: r = {j: v for j, v in r.items() if _tn(j) < 2} or r
        if z < -0.34: r = {j: v for j, v in r.items() if j not in ("DEF_Root_M", "DEF_Spine1_M", "DEF_Chest_M")} or r
        R[i] = dict(norm(r))
    for i in body: rows[i] = list(R[i].items())
    # ---- 2 qua cau roi = ma (Cheek) 100% ----
    for sh in eyes:
        cx = sum(P[i][0] for i in sh) / len(sh)
        for i in sh: rows[i] = [("DEF_Cheek_L" if cx > 0 else "DEF_Cheek_R", 1.0)]   # qua cau xanh 2 ben = MA phong (xac nhan bang texture)
    # ---- luoi: theo z ----
    TJ = [("DEF_Tongue1_M", TZ[0]), ("DEF_Tongue2_M", TZ[1]), ("DEF_Tongue3_M", TZ[2]), ("DEF_Tongue4_M", TZ[3])]
    for i in tongue:
        z = P[i][2]
        if z <= TJ[0][1]: rows[i] = [(TJ[0][0], 1.0)]
        elif z >= TJ[-1][1]: rows[i] = [(TJ[-1][0], 1.0)]
        else:
            for k in range(3):
                if TJ[k][1] <= z <= TJ[k+1][1]:
                    t = sm((z - TJ[k][1]) / (TJ[k+1][1] - TJ[k][1])); rows[i] = [(TJ[k][0], 1-t), (TJ[k+1][0], t)]
    json.dump(dict(idx=idx, rows=rows, tongue=sorted(tongue), tongue_pos=[P[i] for i in sorted(tongue)]), open(out, "w"))
    print("xong", sum(1 for r in rows if r is None), "dinh chua co hang")
    return rows, P, body, tongue, eyes, nb
TZ = (.24, .38, .50, .59)   # z cac khop luoi (giu nhu rig cu)
TONGUE_SHIFT = -0.099        # luoi mesh moi nam truoc luoi cu 0.099 (z .316-.735 so voi .216-.636): lui ve de Idle thut hang vao mieng nhu ban chot
if __name__ == "__main__":
    new = json.load(open("/tmp/wc_new.json"))
    rows, P, body, tongue, eyes, nb = build(new)
    # so sanh voi trong so cu (dinh gan nhat cua mesh cu)
    old = json.load(open("/tmp/wc_old.json"))["chameleon"]; OP = old["pos"]; OW = old["w"]
    OPp = [OP[i*3:i*3+3] for i in range(len(OP)//3)]
    from collections import Counter
    diff = Counter(); bad = []
    for i in body:
        j = min(range(len(OPp)), key=lambda k: dist(OPp[k], P[i]))
        ow = max(OW[j], key=lambda t: t[1])[0]; nw = max(rows[i], key=lambda t: t[1])[0]
        if ow != nw: diff[(ow, nw)] += 1; bad.append((i, ow, nw, [round(c, 2) for c in P[i]]))
    print("khac chu dao so voi mesh cu:", len(bad), "/", len(body))
    for k, v in diff.most_common(25): print(k, v)
