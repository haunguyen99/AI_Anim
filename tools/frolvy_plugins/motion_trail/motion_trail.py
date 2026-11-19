"""Maya-style motion trail for Frolvy (user 2026-11-17: built-in trail is a cloud of crosses, hard to read).

Built-in trail draws a 3D cross on every frame; this plugin draws, as ordinary scene curves under group `MotionTrails`:
  - the path: one smooth bright curve through every sampled frame (thick);
  - a key box (small wire cube, orange) on every KEYED frame;
  - a small tick on every other frame (white comb on one thin curve), so frame spacing (ease in / out) reads like Maya.
Samples come from api.motion_trail_points (world space, [frame, x, y, z, keyed, other_key]); the built-in trail is switched on
only for the read, then restored.

Plugins menu: Trail Selected (toggle on the selection) / Refresh Trails (after the anim changed) / Clear Trails.
The curves are real scene nodes: Clear Trails BEFORE saving a scene or exporting (they are not refreshed by themselves).
From the bridge:  exec(open('.../motion_trail.py').read()); trail(api, ['ns:CTL_Wrist_R'], before=12, after=12)
"""
import math

GROUP = "MotionTrails"
PATH_RGB = (0.15, 0.95, 1.00)    # cyan: stands out on the grey mesh and the dark floor
KEY_RGB = (1.00, 0.55, 0.10)     # orange key boxes
TICK_RGB = (0.95, 0.95, 0.95)    # white frame ticks
PATH_PX, KEY_PX, TICK_PX = 4.0, 2.0, 1.0
KEY_MAX, KEY_MIN = 0.8, 0.08    # key box half-size limits, cm (it scales with how far the node travels)
BOX_FRAC = 0.03                  # key box half-size = this x the path's bounding-box diagonal
STATE = {}                       # node -> (before, after)


def _sub(a, b): return [a[i] - b[i] for i in range(3)]
def _cross(a, b): return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
def _norm(a):
    n = math.sqrt(sum(x * x for x in a))
    return [x / n for x in a] if n > 1e-9 else [0.0, 0.0, 0.0]


def _group(api):
    if GROUP in api.ls():
        return GROUP
    g = api.create_group()
    api.rename(g, GROUP)
    return GROUP


def _short(node):
    return node.split(":")[-1]


def _samples(api, node):
    """[(frame, (x,y,z), keyed)] over the playback range, built-in trail restored afterwards."""
    pts = api.motion_trail_points(node)
    was_on = bool(pts)
    if not was_on:
        api.set_motion_trail(node, True)
        pts = api.motion_trail_points(node)
        api.set_motion_trail(node, False)
    return [(r[0], (r[1], r[2], r[3]), bool(r[4])) for r in pts]


def _flat(points):
    out = []
    for p in points:
        out.extend(p)
    return out


def _box(c, s):
    """Wire cube as one polyline (12 edges walked in a single stroke)."""
    x, y, z = c
    v = [(x + dx * s, y + dy * s, z + dz * s) for dx in (-1, 1) for dy in (-1, 1) for dz in (-1, 1)]
    # corners 0..7 indexed by (dx,dy,dz) bits; a path that covers all 12 edges (with a few retraced)
    order = [0, 1, 3, 2, 0, 4, 5, 1, 5, 7, 3, 7, 6, 2, 6, 4]
    return [v[i] for i in order]


def _draw(api, node, before, after):
    s = _samples(api, node)
    if len(s) < 2:
        return 0
    cur = int(api.current_frame())
    lo, hi = cur - before, cur + after
    win = [r for r in s if lo <= r[0] <= hi or r[2]]   # keys always shown
    win = [r for r in win if lo <= r[0] <= hi]
    if len(win) < 2:
        return 0
    grp = _group(api)
    tag = "MT_" + _short(node)
    names = []
    pos = [r[1] for r in win]
    lo3 = [min(p[i] for p in pos) for i in range(3)]; hi3 = [max(p[i] for p in pos) for i in range(3)]
    diag = math.sqrt(sum((hi3[i] - lo3[i]) ** 2 for i in range(3)))
    box = min(KEY_MAX, max(KEY_MIN, BOX_FRAC * diag))
    tick = 2.0 * box
    # path: smooth curve through every sample
    pth = api.create_curve(_flat(pos), 3 if len(pos) > 3 else 1, True, False)
    api.rename(pth, tag + "_path"); pth = tag + "_path"
    api.set_curve_color(pth, *PATH_RGB); api.set_curve_width(pth, PATH_PX)
    names.append(pth)
    # frame ticks: a comb on one polyline (p -> p+d -> p -> next p)
    comb = []
    for i, (f, p, k) in enumerate(win):
        a = win[max(i - 1, 0)][1]; b = win[min(i + 1, len(win) - 1)][1]
        t = _norm(_sub(b, a))
        d = _norm(_cross(t, [0.0, 1.0, 0.0]))
        if d == [0.0, 0.0, 0.0]:
            d = _norm(_cross(t, [1.0, 0.0, 0.0]))
        q = [p[j] + d[j] * tick for j in range(3)]
        comb += [p, q, p]
    if comb:
        tk = api.create_curve(_flat(comb), 1, True, False)
        api.rename(tk, tag + "_ticks"); tk = tag + "_ticks"
        api.set_curve_color(tk, *TICK_RGB); api.set_curve_width(tk, TICK_PX)
        names.append(tk)
    # key boxes
    for f, p, k in win:
        if not k:
            continue
        kb = api.create_curve(_flat(_box(p, box)), 1, True, False)
        nm = "%s_key%d" % (tag, int(f))
        api.rename(kb, nm)
        api.set_curve_color(nm, *KEY_RGB); api.set_curve_width(nm, KEY_PX)
        names.append(nm)
    for n in names:
        api.parent(n, grp)
    return len(names)


def clear_node(api, node):
    tag = "MT_" + _short(node)
    n = 0
    for name in list(api.ls()):
        if name == tag + "_path" or name == tag + "_ticks" or name.startswith(tag + "_key"):
            api.delete_node(name); n += 1
    STATE.pop(node, None)
    return n


def clear(api):
    n = 0
    for name in list(api.ls()):
        short = _short(name)
        if short.startswith("MT_") and (short.endswith("_path") or short.endswith("_ticks") or "_key" in short):
            api.delete_node(name); n += 1
    if GROUP in api.ls():
        api.delete_node(GROUP)
    STATE.clear()
    return n


def trail(api, nodes=None, before=16, after=16):
    """Draw (or redraw) trails for nodes (default: selection). Returns the number of curves made."""
    sel = list(api.selection())
    nodes = list(nodes) if nodes else [n for n in sel if not _short(n).startswith("MT_")]
    made = 0
    for n in nodes:
        clear_node(api, n)
        made += _draw(api, n, before, after)
        STATE[n] = (before, after)
    api.select(sel, False)
    return made


def toggle(api, before=16, after=16):
    sel = [n for n in api.selection() if not _short(n).startswith("MT_")]
    on = [n for n in sel if n in STATE]
    if on:
        for n in on:
            clear_node(api, n)
        api.log("Trail off: %s" % ", ".join(_short(n) for n in on))
        return
    made = trail(api, sel, before, after)
    api.log("Trail on: %d curves for %d node(s)" % (made, len(sel)))


def refresh(api):
    nodes = list(STATE.items())
    for n, (b, a) in nodes:
        trail(api, [n], b, a)
    api.log("Trails refreshed: %d" % len(nodes))


def register(api):
    api.command("Trail Selected (Maya style)", lambda: toggle(api))
    api.command("Refresh Trails", lambda: refresh(api))
    api.command("Clear Trails", lambda: api.log("Trails cleared: %d curves" % clear(api)))
