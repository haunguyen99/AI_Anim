"""Mecha Pup skin by rules (run inside Frolvy: exec(open(...).read()); run(api, A)). Shell map (A.survey):
0 lower body + 4 legs, 1 head+ears, 2 face/visor, 3 front leg tops, 4 backpack, 5/7/8/9 antenna+dish, 6 tail."""
import math, re

SMOOTH_ITERS = 2
SMOOTH_K = 0.5

def run(api, A, only=None):
    R = A.R
    api.set_frame(0); R.zero_controls(api)
    for j in api.ls("Joint"):
        pass
    mesh = "Pet_Mecha_Pup"
    api.select([mesh]); 
    if only is None:
        api.bind_skin(R.influences(api))
    side = lambda x: "_R" if x < 0 else "_L"
    D = lambda n, s: "DEF_%s%s" % (n, s)
    ANT = ["DEF_Ant1_M", "DEF_Ant2_M", "DEF_Dish_M", "DEF_Muzzle_M"]
    TAIL = ["DEF_Tail1_M", "DEF_Tail2_M", "DEF_TailEnd_M"]

    def seg_owner(p, cands, blend=0.25):
        best = None
        for a, b, pa, bias in cands:
            d, t = A._seg(p, A._jp(api, a), A._jp(api, b))
            if best is None or d + bias < best[0]:
                best = (d + bias, a, b, pa, t)
        _, a, b, pa, t = best
        w = {a: 1.0}
        if t > 1 - blend and b and 'End' not in b:
            f = 0.5 * A.ramp(t, 1 - blend, 1.0); w = {a: 1 - f, b: f}
        elif t < blend and pa:
            f = 0.5 * A.ramp(t, blend, 0.0); w = {a: 1 - f, pa: f}
        return w

    def body_w(p):
        s = side(p[0]); x, z = abs(p[0]), p[2]
        mid = A.ramp(x, 0.03, 0.14)
        fh = A.ramp(-z, 0.04, 0.16) * mid           # hind leg share
        ff = A.ramp(z, 0.05, 0.14) * mid            # front leg share
        ft = max(0.0, 1.0 - fh - ff)
        if fh + ff > 1.0:
            t = fh + ff; fh, ff = fh / t, ff / t
        out = {}
        def add(w, k):
            for j, v in w.items(): out[j] = out.get(j, 0.0) + v * k
        if ft > 0:
            add(seg_owner(p, [("DEF_Root_M", "DEF_Spine1_M", None, 0.0), ("DEF_Spine1_M", "DEF_Chest_M", "DEF_Root_M", 0.0),
                              ("DEF_Chest_M", "DEF_Neck_M", "DEF_Spine1_M", 0.0)]), ft)
        if fh > 0:
            add(seg_owner(p, [(D("Hip", s), D("Knee", s), "DEF_Root_M", 0.0), (D("Knee", s), D("Ankle", s), D("Hip", s), 0.0),
                              (D("Ankle", s), D("Toes", s), D("Knee", s), 0.0), (D("Toes", s), D("ToesEnd", s), D("Ankle", s), 0.0)]), fh)
        if ff > 0:
            add(seg_owner(p, [(D("Shoulder", s), D("Elbow", s), D("Chest", "_M"), 0.0), (D("Elbow", s), D("Wrist", s), D("Shoulder", s), 0.0),
                              (D("Wrist", s), D("FToes", s), D("Elbow", s), 0.0), (D("FToes", s), D("FToesEnd", s), D("Wrist", s), 0.0)]), ff)
        return out

    def fn(i, p, sh):
        s = side(p[0])
        if sh == 0 or sh == 3:
            return body_w(p)
        if sh in (1, 2):
            # ears: top of the head, outboard
            ear = [D("Ear1", s), D("Ear2", s), D("EarEnd", s)]
            if sh == 1 and abs(p[0]) > 0.17 and p[1] > 0.76:
                e = A.chain_w(api, p, ear, parent="DEF_Head_M", top=1.0)
                de = min(A._seg(p, A._jp(api, ear[k]), A._jp(api, ear[k + 1]))[0] for k in range(2))
                f = 1.0 - A.ramp(de, 0.05, 0.22)
                return {k: v * f for k, v in e.items()} | {"DEF_Head_M": 1 - f}
            return {"DEF_Head_M": 1.0}
        if sh == 4:
            return {"DEF_Backpack_M": 1.0}
        if sh == 6:
            return A.chain_w(api, p, TAIL, parent="DEF_Root_M", top=0.35)
        return A.chain_w(api, p, ANT, parent="DEF_Backpack_M", top=0.5)

    m = R.Mesh(api, mesh)
    shell_of = {}
    for si, sh in enumerate(m.shells):
        for i in sh: shell_of[i] = si
    W = {i: fn(i, m.p(i), shell_of[i]) for i in range(m.n)}
    nb = {}
    for e in m.edges:
        a, b = e[0], e[1]
        if shell_of[a] == shell_of[b]:
            nb.setdefault(a, []).append(b); nb.setdefault(b, []).append(a)
    for _ in range(SMOOTH_ITERS):
        N = {}
        for i, w in W.items():
            if shell_of[i] in (0, 3) and nb.get(i):
                acc = {j: v * (1 - SMOOTH_K) for j, v in w.items()}
                for k in nb[i]:
                    for j, v in W[k].items():
                        acc[j] = acc.get(j, 0.0) + v * SMOOTH_K / len(nb[i])
                N[i] = acc
            else:
                N[i] = w
        W = N
    print("weights written:", A.write_skin(api, mesh, lambda i, p, sh: W[i]))
    return R.skin_report(api, mesh) if hasattr(R, "skin_report") else None
