"""Loop Seam - make a looping anim (idle / run / walk) join smoothly from its last frame to its first, in Frolvy.

A loop jumps at the seam for two reasons, and keying the last frame "equal" to the first fixes neither on its own:
  1. a curve DRIFTS: its last key does not hold the first key's value. RPG2 Hero Idle (2026-11-05): the additive layer
     `fix_r1_tay_xoay_it_dich_nhieu` held wrist rx 0 -> -1.3 deg and blade rz 0 -> -0.5 deg over the loop; a 40 cm blade
     turns that into a 16 mm/frame spike at the seam;
  2. the two end keys get one-sided automatic tangents, so the speed breaks at the seam.

smooth() fixes both, LAYER BY LAYER (api.layers(): Base first, then override / additive layers):
  - each layer is soloed so api.get_attr reads that layer's own value (the displayed value of an additive layer is
    Base + layer, and api.set_attr / api.set_key in a layer writes the COMBINED value into it - they compound, so they
    are never used here). Values are changed only with api.move_key(path, f, f, value);
  - a channel whose last key differs from its first is de-trended: every key loses gap * (t - first)/(last - first), so
    the last key equals the first and the closing is spread over the whole loop instead of snapping in the last 3 frames;
  - both end keys get the same tangent = (key after the first - key before the last) / (time between them across the
    seam), the cyclic Catmull-Rom slope. It reads KEY values only, so running it twice gives the same result;
  - infinity is set to cycle; solo and the active layer are put back;
  - seam_report() then checks the combined result in world space (acceleration at the seam / interior, speed spike).

Run it automatically at the end of every edit round on a looping clip (rule: memory frolvy-loop-seam-smooth):
    exec(open(r'D:\\Project\\AI_Anim\\tools\\frolvy_plugins\\loop_seam\\loop_seam.py', encoding='utf-8').read())
    smooth(api)            # prints one line per problem, 'seam OK' when clean; returns a report dict
Plugins menu: Smooth Loop Seam (same call).

Playback range (api.frame_range()) is the loop: first frame == last frame (F1 == F31 in 1-based counting).
Tangent units are per SECOND (api.set_key_tangent), so the per-frame slope is multiplied by fps.
Pure Python, no numpy.
"""
import math

CH = ("tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz")
ROT = ("rx", "ry", "rz")
# World points worth watching at the seam when they exist in the scene (name after the namespace).
PROBES = ("DEF_Wrist_R", "DEF_Wrist_L", "DEF_Elbow_R", "DEF_Elbow_L", "DEF_WeaponEnd_R", "DEF_WeaponEnd_L",
          "DEF_Head_M", "DEF_Chest_M", "DEF_Root_M", "DEF_Ankle_R", "DEF_Ankle_L")


def _fps(api):
    for name in ("fps", "get_fps"):
        f = getattr(api, name, None)
        if callable(f):
            try:
                v = float(f())
                if v > 0:
                    return v
            except Exception:
                pass
    return 30.0


def _animated(api, nodes=None):
    """{path: [key frames]} for every channel with 3+ keys IN THE ACTIVE LAYER."""
    out = {}
    for n in (nodes if nodes is not None else api.ls()):
        for c in CH:
            p = n + "." + c
            try:
                k = sorted(int(round(f)) for f in api.list_keys(p))
            except Exception:
                continue
            if len(k) > 2:
                out[p] = k
    return out


def _smooth_layer(api, li, a, b, fps, nodes, log):
    """Close and tangent one layer (already soloed + active). Returns (closed, tangents, skipped, still_open)."""
    chans = _animated(api, nodes)
    loop = {p: ks for p, ks in chans.items() if ks[0] == a and ks[-1] == b}
    skipped = sorted(set(chans) - set(loop))
    frames = sorted({f for ks in loop.values() for f in ks})
    val = {p: {} for p in loop}
    for f in frames:
        api.set_frame(f)
        for p, ks in loop.items():
            if f in ks:
                val[p][f] = api.get_attr(p)

    closed = []
    for p, ks in loop.items():
        v = val[p]
        gap = v[b] - v[a]
        tol = 1e-4 if p.rsplit(".", 1)[1] in ROT else 1e-5
        if abs(gap) <= tol:
            continue
        for k in ks[1:]:                               # de-trend: last key := first key, closing spread over the loop
            nv = v[k] - gap * (k - a) / float(b - a)
            api.move_key(p, k, k, nv)
            v[k] = nv
        closed.append((p.split(":")[-1], round(gap, 4)))

    tangents = 0
    for p, ks in loop.items():
        v = val[p]
        if max(v.values()) - min(v.values()) < 1e-6:
            continue                                   # constant channel, nothing to smooth
        kn, kp = ks[1], ks[-2]
        slope = (v[kn] - v[kp]) / float((kn - a) + (b - kp)) * fps      # per second
        api.set_key_tangent(p, a, slope, slope, False)
        api.set_key_tangent(p, b, slope, slope, False)
        api.set_infinity(p, "cycle", "cycle")
        tangents += 1

    # read back this layer's own values: first and last key must now agree
    still = []
    api.set_frame(a)
    first = {p: api.get_attr(p) for p in loop}
    api.set_frame(b)
    for p in loop:
        tol = 1e-3 if p.rsplit(".", 1)[1] in ROT else 1e-4
        if abs(api.get_attr(p) - first[p]) > tol:
            still.append(p.split(":")[-1])
    return closed, tangents, skipped, still


def smooth(api, nodes=None, log=print, probes=True):
    """Close the loop and give the seam one shared tangent, in every layer.
    Returns {'closed': {layer: [(channel, gap)]}, 'tangents', 'skipped', 'not_closed', 'report'}."""
    a, b = [int(x) for x in api.frame_range()]
    fps = _fps(api)
    cur = int(api.current_frame())
    sel = list(api.selection())
    active0 = int(api.active_layer())
    layers = list(api.layers())
    many = len(layers) > 1
    res = {"closed": {}, "tangents": 0, "skipped": [], "not_closed": []}
    try:
        for li, name in enumerate(layers):
            if many:
                api.set_layer_solo(li, True)
            api.set_active_layer(li)
            try:
                closed, tangents, skipped, still = _smooth_layer(api, li, a, b, fps, nodes, log)
            finally:
                if many:
                    api.set_layer_solo(li, False)
            res["closed"][name] = closed
            res["tangents"] += tangents
            res["skipped"] += ["%s:%s" % (name, s.split(":")[-1]) for s in skipped]
            res["not_closed"] += ["%s:%s" % (name, s) for s in still]
            for ch, gap in closed:
                log("layer %s: %s last key was off by %s -> de-trended" % (name, ch, gap))
    finally:
        api.set_active_layer(active0)
        api.set_frame(cur)
        if sel:
            api.select(sel)
    if res["not_closed"]:
        log("NOT closed: %s" % ", ".join(res["not_closed"]))
    n_closed = sum(len(v) for v in res["closed"].values())
    log("Loop Seam: %d channels closed, %d tangents set across %d layer(s)%s"
        % (n_closed, res["tangents"], len(layers),
           ("; %d channels skipped (keys do not span %d..%d)" % (len(res["skipped"]), a, b)) if res["skipped"] else ""))
    res["report"] = seam_report(api, log=log) if probes else {}
    return res


def seam_report(api, names=None, log=print, flag=2.0):
    """World-space check of the combined result at the seam. For each moving probe: acceleration at the seam / biggest
    interior acceleration, per axis, and the speed spike (fastest step within 2 frames of the seam / median step).
    A ratio above `flag` is printed as a problem. Points that move less than 2 mm over the loop are ignored.
    Returns {probe: {'accel': [x, y, z], 'spike': r}}."""
    a, b = [int(x) for x in api.frame_range()]
    n = b - a
    cur = int(api.current_frame())
    have = {}
    for full in api.ls():
        short = full.split(":")[-1]
        if short in (names or PROBES):
            have[short] = full
    pts = {s: [] for s in have}
    for f in range(a, b + 1):
        api.set_frame(f)
        for s, full in have.items():
            m = api.world_matrix(full)
            pts[s].append((m[12], m[13], m[14]))
    api.set_frame(cur)
    out, bad = {}, 0
    for s, p in pts.items():
        p = p[:n]
        if max(max(q[i] for q in p) - min(q[i] for q in p) for i in range(3)) < 2e-3:
            continue
        ratios = []
        for ax in range(3):
            v = [q[ax] for q in p]
            acc = [v[(i + 1) % n] - 2 * v[i] + v[(i - 1) % n] for i in range(n)]
            inner = max(abs(x) for x in acc[3:n - 3]) if n > 8 else 0.0
            seam = max(abs(acc[0]), abs(acc[1]), abs(acc[n - 1]))
            ratios.append(round(seam / inner, 2) if inner > 1e-6 else 0.0)
        sp = [math.dist(p[(i + 1) % n], p[i]) for i in range(n)]
        med = sorted(sp)[n // 2]
        spike = max(sp[n - 2], sp[n - 1], sp[0], sp[1]) / med if med > 1e-7 else 0.0
        out[s] = {"accel": ratios, "spike": round(spike, 2)}
        if max(ratios) > flag or spike > flag:
            bad += 1
            log("seam: %s accel %s speed spike x%.1f" % (s, ratios, spike))
    if not bad:
        log("seam OK (%d moving probes)" % len(out))
    return out


def register(api):
    api.command("Smooth Loop Seam", lambda: smooth(api, log=api.log))
