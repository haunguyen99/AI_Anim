"""Anim Ops - one-call scene operations for Frolvy: scene overview, key table, clear keys, back to the default pose.

Why (user 2026-11-11, "sao lau the" -> "toi uu cach lam viec de nhanh nhat"): clearing the scarf keys of the Ninja took ~12
tool calls of probing around a few seconds of real Frolvy work. Each request below is ONE command, and the summary line it
prints is also the check, so no separate verify step is needed.

Inside Frolvy (execute_code of the `frolvy` MCP server):
    exec(open(r'<repo>\\tools\\frolvy_plugins\\anim_ops\\anim_ops.py', encoding='utf-8').read())
    report(api)                      # frames, nodes, layers, ref clips, selection, keyed nodes
    keys(api, 'Scarf')               # key table of every node whose name contains 'Scarf' ("," or "|" = several patterns)
    clear_keys(api, 'Scarf')         # delete ALL keys on those nodes, then their controls back to the default pose
    clear_keys(api, 'Scarf', reset=False)    # keys only;   dry=True: only count what would go
    reset_default(api, 'Scarf')      # default pose, keys untouched
From outside Frolvy: python tools/frolvy_port.py [port] scene | keys <pat> | clear <pat> [--keep-pose] [--dry] | reset <pat>

Rules baked in:
  - api.list_keys / api.delete_key work on the ACTIVE layer only, so a reset runs only while Base is active
    (set_transform on an additive layer writes the combined value, see frolvy_layers.py);
  - default pose = translate 0, rotate 0, scale 1 (Rig Builder controls, same as rig_pose_tools); locked channels are
    unlocked for the reset and locked again; FK/IK switches and the fit skeleton are never touched;
  - a pattern must be given and matches by name substring, so "all keys" has to be asked for on purpose (e.g. 'CTL_').
"""
import time

TR = ("tx", "ty", "tz", "rx", "ry", "rz")
SC = ("sx", "sy", "sz")


def _match(api, pattern):
    pats = [p.strip().lower() for p in pattern.replace("|", ",").split(",") if p.strip()]
    if not pats:
        raise ValueError("give a name pattern, e.g. 'Scarf'")
    return [n for n in api.ls() if any(p in n.lower() for p in pats)]


def _keyed(api, nodes):
    """{node: {channel: [frames]}} for every channel that holds keys on the active layer."""
    out = {}
    for n in nodes:
        for c in TR + SC:
            try:
                k = api.list_keys(n + "." + c)
            except Exception:
                continue
            if k:
                out.setdefault(n, {})[c] = [float(f) for f in k]
    return out


def _count(table):
    return sum(len(v) for d in table.values() for v in d.values())


def _frames(frames, cap=14):
    fr = sorted({int(round(f)) for f in frames})
    if len(fr) <= cap:
        return " ".join(str(f) for f in fr) or "-"
    return "%s .. %s (%d frames)" % (" ".join(str(f) for f in fr[:6]), " ".join(str(f) for f in fr[-4:]), len(fr))


def _layer(api):
    lay = list(api.layers())
    i = api.active_layer()
    return (lay[i] if 0 <= i < len(lay) else "?"), i == 0


def _controls(api, nodes):
    return [n for n in nodes if api.node_type(n) == "Curve" and n != "FitSkeleton"
            and not n.endswith(("_grp", "_follow")) and "Switch" not in n]


def _reset(api, controls):
    """Default pose. Returns how many controls had to move."""
    moved = 0
    for c in controls:
        t = api.transform(c)
        if not t or (all(abs(v) < 1e-6 for v in t[:6]) and all(abs(v - 1) < 1e-6 for v in t[6:9])):
            continue
        lk = api.locked_channels(c)
        if lk:
            api.lock_channels(c, " ".join(lk), False)
        s = [1.0 if ("s" + ax) not in lk else t[6 + i] for i, ax in enumerate("xyz")]
        api.set_transform(c, [0, 0, 0], [0, 0, 0], s)
        if lk:
            api.lock_channels(c, " ".join(lk), True)
        moved += 1
    return moved


def _offset(api, controls):
    """Largest translate / rotate value left on these controls (0 = default pose)."""
    m = 0.0
    for c in controls:
        t = api.transform(c)
        if t:
            m = max(m, max(abs(v) for v in t[:6]))
    return m


def report(api, log=print):
    a, b = api.frame_range()
    up = api.up_axis()
    log("frames %d-%d, now %d, up %s/%s" % (a, b, api.current_frame(), up[0], up[1]))
    kinds = {t: api.ls(t) for t in ("Object", "Joint", "Curve", "Group")}
    log("nodes: " + ", ".join("%s %d" % (t, len(v)) for t, v in kinds.items()))
    if kinds["Object"]:
        log("objects: " + ", ".join(kinds["Object"][:12]))
    log("layers: %s | active: %s" % (", ".join(api.layers()), _layer(api)[0]))
    for c in api.ref_clips():
        try:
            m = api.ref_marks(c)
        except Exception:
            m = []
        log("ref clip %s: %d marks, frames %s" % (c, len(m), _frames(m)))
    pk = api.pickers()
    if pk:
        log("pickers: " + ", ".join(pk))
    sel = api.selection()
    log("selection: " + (", ".join(sel[:10]) if sel else "-"))
    table = _keyed(api, api.ls())
    if not table:
        log("keys: none")
        return
    fr = [f for d in table.values() for v in d.values() for f in v]
    top = sorted(((sum(len(v) for v in d.values()), n) for n, d in table.items()), reverse=True)
    log("keys: %d on %d nodes, frames %s" % (_count(table), len(table), _frames(fr, 20)))
    log("  most: " + ", ".join("%s %d" % (n, k) for k, n in top[:8]))


def keys(api, pattern, log=print):
    nodes = _match(api, pattern)
    table = _keyed(api, nodes)
    log("%d nodes match '%s', %d keyed, %d keys (layer %s)" % (len(nodes), pattern, len(table), _count(table), _layer(api)[0]))
    for n, d in table.items():
        fr = [f for v in d.values() for f in v]
        log("  %s: %d keys on %s, frames %s" % (n, sum(len(v) for v in d.values()), " ".join(d), _frames(fr)))


def clear_keys(api, pattern, reset=True, dry=False, log=print):
    t0 = time.time()
    nodes = _match(api, pattern)
    table = _keyed(api, nodes)
    layer, base = _layer(api)
    if dry:
        log("dry run: %d keys on %d of %d nodes matching '%s' (layer %s); nothing changed"
            % (_count(table), len(table), len(nodes), pattern, layer))
        return
    failed = []
    for n, d in table.items():
        for c, frames in d.items():
            for f in frames:
                if not api.delete_key(n + "." + c, int(round(f))):
                    failed.append("%s.%s@%s" % (n, c, f))
    total = _count(table)
    left = _count(_keyed(api, list(table)))
    tail = ""
    if reset and not base:
        tail = "; pose NOT reset: active layer is %s, not Base" % layer
    elif reset:
        ctl = _controls(api, nodes)
        moved = _reset(api, ctl)
        tail = "; %d of %d controls moved to the default pose, max offset left %.5f" % (moved, len(ctl), _offset(api, ctl))
    log("cleared %d keys on %d nodes matching '%s' (layer %s): %d left, %d failed%s | %.1fs"
        % (total - left, len(table), pattern, layer, left, len(failed), tail, time.time() - t0))
    if failed:
        log("  failed: " + ", ".join(failed[:8]))


def reset_default(api, pattern, log=print):
    nodes = _match(api, pattern)
    layer, base = _layer(api)
    if not base:
        log("not reset: active layer is %s, not Base" % layer)
        return
    ctl = _controls(api, nodes)
    moved = _reset(api, ctl)
    log("%d of %d controls matching '%s' moved to the default pose, max offset left %.5f"
        % (moved, len(ctl), pattern, _offset(api, ctl)))


def cli(api, cmd, args=()):
    args = list(args)
    flags = [a for a in args if a.startswith("--")]
    pos = [a for a in args if not a.startswith("--")]
    pat = pos[0] if pos else ""
    if cmd == "scene":
        report(api)
    elif cmd == "keys":
        keys(api, pat)
    elif cmd == "clear":
        clear_keys(api, pat, reset="--keep-pose" not in flags, dry="--dry" in flags)
    elif cmd == "reset":
        reset_default(api, pat)
    else:
        raise ValueError("unknown command %r (scene | keys | clear | reset)" % cmd)


def register(api):
    api.command("Anim Ops: Scene Report", lambda: report(api, log=api.log))
