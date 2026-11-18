# Kitsune Nine-Mist bind + weights. Chạy SAU rig_build.py. Bind khi MỌI control = 0.
exec(open(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\kitsune_nine_mist\kit_common.py").read())
for _c in api.ls("Curve"):
    if _c.startswith("CTL_") and _c != "CTL_Main": api.rotate(_c, 0, 0, 0); api.move(_c, 0, 0, 0)
try: api.set_attr("CTL_TailFan.fan", 0.0)
except Exception as e: print("fan", e)
api.set_frame(3); api.set_frame(0)
DEF = [j for j in api.ls("Joint") if j.startswith("DEF_") and "Muzzle" not in j]
def ramp(v, a, b): t = (v - a) / (b - a); return max(0.0, min(1.0, t))
def sm(t): return t * t * (3 - 2 * t)
api.select([MESH])
try: api.unbind_skin()
except Exception: pass
api.select([MESH]); api.bind_skin(DEF)
W = {}
def body_row(i):
    x, y, z = V[i]; ax = abs(x); s = "L" if x > 0 else "R"
    # chân: y thấp; trái/phải và trước/sau chuyển mềm quanh x=0 và z~0.17 (các chân dính nhau ở bụng)
    leg = 1 - sm(ramp(y, 0.17, 0.27)); wl = sm(ramp(x, -0.03, 0.03)); fz = sm(ramp(z, 0.12, 0.22))
    l2 = sm(ramp(0.19 - y, 0.0, 0.09)); l3 = sm(ramp(0.10 - y, 0.0, 0.07))
    hw = sm(ramp(y, 0.33, 0.42)); sp = (1 - hw) * sm(ramp(y, 0.18, 0.36)); rt = 1 - hw - sp
    ew = sm(ramp(y, 0.56, 0.64)) * sm(ramp(ax, 0.04, 0.10)); f2 = sm(ramp(y, 0.66, 0.76))
    r = {}
    base = {"DEF_Root_M": rt, "DEF_Spine1_M": sp, "DEF_Head_M": hw}
    for k, v in base.items(): r[k] = r.get(k, 0) + v * (1 - leg) * (1 - ew)
    for pre, fp in (("FLeg", fz), ("BLeg", 1 - fz)):
        for sd, sp_ in (("L", wl), ("R", 1 - wl)):
            q = leg * fp * sp_ * (1 - ew)
            if q > 0.004: r["DEF_%s1_%s" % (pre, sd)] = q * (1 - l2); r["DEF_%s2_%s" % (pre, sd)] = q * l2 * (1 - l3); r["DEF_%s3_%s" % (pre, sd)] = q * l2 * l3
    r["DEF_Ear1_" + s] = ew * (1 - f2); r["DEF_Ear2_" + s] = ew * f2
    return r
def mask_row(i):
    x, y, z = V[i]; ax = abs(x); s = "L" if x > 0 else "R"
    ew = sm(ramp(y, 0.60, 0.66)) * sm(ramp(ax, 0.04, 0.10)); f2 = sm(ramp(y, 0.66, 0.76))
    return {"DEF_Head_M": 1 - ew, "DEF_Ear1_" + s: ew * (1 - f2), "DEF_Ear2_" + s: ew * f2}
def tail_row(t, i):
    T = t['T'][i]; ts = (0.0, 0.2, 0.4, 0.6, 0.8); r = {}
    if T >= ts[4]: r[tail_name(t, 5)] = 1.0
    else:
        for n in range(4):
            if ts[n] <= T < ts[n + 1]:
                u = sm((T - ts[n]) / 0.2); r[tail_name(t, n + 1)] = 1 - u; r[tail_name(t, n + 2)] = u
    return r
for i in BODY: W[i] = body_row(i)
for m in MASK:
    for i in m: W[i] = mask_row(i)
for t in TAILS:
    for i in t['verts']: W[i] = tail_row(t, i)
# làm mượt trọng số: 2 lượt trộn 50% với trung bình hàng xóm CÙNG mảnh (đuôi/thân/mặt nạ riêng nhau) để vùng chuyển không bị kéo thành cạnh dài
_part = {}
for pi, grp in enumerate([BODY] + MASK + [t['verts'] for t in TAILS]):
    for i in grp: _part[i] = pi
for _ in range(2):
    new = {}
    for i in range(len(IDX)):
        nb = [n for n in NB[i] if _part[n] == _part[i]]
        acc = {}
        for j, v in W[i].items(): acc[j] = acc.get(j, 0) + 0.5 * v
        for n in nb:
            for j, v in W[n].items(): acc[j] = acc.get(j, 0) + 0.5 * v / len(nb)
        new[i] = acc
    W = new
def fin(w):
    r = [(j, v) for j, v in w.items() if v > 0.01]; r.sort(key=lambda a: -a[1]); r = r[:4]; tot = sum(v for _, v in r); return [(j, v / tot) for j, v in r]
missing = [i for i in range(len(IDX)) if i not in W]
print("vertices without row:", len(missing))
api.select([MESH]); api.set_skin_weights([IDX[i] for i in range(len(IDX))], [fin(W[i]) for i in range(len(IDX))])
print("skinned", len(IDX))
