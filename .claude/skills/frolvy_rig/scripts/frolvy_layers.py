"""Anim layers in Frolvy for EDITS of an existing anim (user 2026-11-04: every requested edit goes on a layer,
never straight on the Base layer). Run INSIDE Frolvy through MCP execute_code:

    import sys; sys.path.insert(0, r"E:\\AI Animation\\.claude\\skills\\frolvy_rig\\scripts")
    import importlib, frolvy_layers as FL; importlib.reload(FL)
    L = FL.start_fix(api, "fix_r1_hand")                    # new additive layer on top, made active
    FL.key(api, L, {"CTL_Hand_R.rx": 25.0}, 30, hold=(24, 36))   # 25 = TOTAL value wanted on screen
    FL.offset(api, L, {"CTL_Hand_R.rx": 5.0}, 30)           # or: add +5 to what is there now
    FL.report(api)                                          # layers and which nodes/channels each one keys
    FL.bake_for_export(api, 0, 60)                          # ONLY on a copy right before export

Frolvy 0.9.36 bugs this works around (tested 2026-11-04, work/frolvy_feedback.md #14-#16):
- set_key on an additive layer stores the TOTAL on-screen value as the layer's own value (counted twice), and it
  keys EVERY channel of the selected nodes, even with select_channels. So key() records each channel's layer
  contribution first, then set_key, then move_key writes the right value back on every channel.
- flatten_layers, bake_keys and export_scene count an additive layer twice (and bake_keys of a node that has
  layered keys loses the Base). So bake_for_export() samples the on-screen totals, writes them on Base itself and
  deletes the layers before the normal export (bake team joints -> export_scene -> fbx_ascii_keep).
Fix layers stay at weight 1 and unmuted: contribution maths assumes that.
"""

CH = ("tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz")


def _node(path):
    return path.rsplit(".", 1)[0]


def _chans(api, node):
    out = list(CH)
    try:
        for a in api.list_attrs(node) or []:
            if a not in out and (api.attr_info(node + "." + a) or {}).get("keyable"):
                out.append(a)
    except Exception:
        pass
    return out


def _read(api, nodes, frame):
    api.set_frame(frame)
    return {n: {c: api.get_attr(n + "." + c) for c in _chans(api, n)} for n in nodes}


def start_fix(api, name, mode="additive"):
    """Add a fix layer on top and make it active. Name it fix_r<round>_<what>. Returns its index."""
    api.create_layer(name, mode)
    return api.active_layer()


def _contrib(api, layer, nodes, frame):
    tot = _read(api, nodes, frame)
    api.set_layer_mute(layer, True)
    wo = _read(api, nodes, frame)
    api.set_layer_mute(layer, False)
    return tot, wo


def key(api, layer, targets, frame, hold=None, interp="spline", tol=1e-3):
    """Key `targets` {"node.ch": TOTAL value} on `layer` at `frame`; every other channel of those nodes keeps what
    it shows now. hold=(a, b): first key the layer's current contribution at a and b (0 on a fresh layer) so the
    fix fades in and out there instead of shifting the whole clip. Returns the max error on screen after keying."""
    nodes = sorted({_node(p) for p in targets})
    for h in (hold or ()):
        if h != frame:
            _key_nodes(api, layer, nodes, {}, h, interp)
    return _key_nodes(api, layer, nodes, targets, frame, interp, tol)


def _key_nodes(api, layer, nodes, targets, frame, interp, tol=1e-3):
    tot, wo = _contrib(api, layer, nodes, frame)
    api.set_active_layer(layer)
    api.select(nodes)
    api.set_frame(frame)
    api.set_key()
    want = {}
    for n in nodes:
        for c, t in tot[n].items():
            p = n + "." + c
            if t is None or wo[n][c] is None:
                continue
            total = targets.get(p, t)
            want[p] = total
            api.move_key(p, frame, frame, total - wo[n][c])
            if interp:
                api.set_key_interp(p, frame, interp)
    got = _read(api, nodes, frame)
    return max([abs(got[_node(p)][p.rsplit(".", 1)[1]] - v) for p, v in want.items()] or [0.0])


def offset(api, layer, deltas, frame, hold=None, interp="spline"):
    """Like key() but with {"node.ch": +delta} on top of what the screen shows now."""
    nodes = sorted({_node(p) for p in deltas})
    now = _read(api, nodes, frame)
    tg = {p: now[_node(p)][p.rsplit(".", 1)[1]] + d for p, d in deltas.items()}
    return key(api, layer, tg, frame, hold=hold, interp=interp)


def layered(api, nodes=None):
    """{layer index: {node: [channels with keys]}} for every layer above Base."""
    nodes = nodes or api.ls()
    keep = api.active_layer()
    out = {}
    for i in range(1, len(api.layers())):
        api.set_active_layer(i)
        hit = {}
        for n in nodes:
            cs = [c for c in _chans(api, n) if api.list_keys(n + "." + c)]
            if cs:
                hit[n] = cs
        out[i] = hit
    api.set_active_layer(keep)
    return out


def report(api, nodes=None):
    names = api.layers()
    for i, hit in layered(api, nodes).items():
        print(i, names[i], {n: cs for n, cs in hit.items()})


def lag_mirror_translate(api, layer, src, dst, lag=5, gain=1.15, period=30, step=3,
                         signs={"tx": -1, "ty": 1, "tz": 1}):
    """Lech nhip hai tay cho idle loop: translate cua `dst` (tay trai) = chuyen dong translate cua `src` (tay phai),
    doi xung (tx doi dau), TRE `lag` frame, bien do x`gain` (chi 10-20%), quanh POSE GOC cua dst o F0 (F0/F30 giu
    nguyen, rotate khong doi). Translate cong tuyen tinh nen layer cong khong sai so (rotate Euler lon thi co:
    dung dat ca gia tri tong len layer, lech 5-8 do). Goi sau start_fix(). Tra max sai so."""
    rt = {f: _read(api, [src], f)[src] for f in range(period)}
    d0 = _read(api, [dst], 0)[dst]
    r0 = rt[(0 - lag) % period]
    err = 0.0
    for f in range(0, period + 1, step):
        r = rt[(f - lag) % period]
        tg = {dst + "." + c: d0[c] + gain * s * (r[c] - r0[c]) for c, s in signs.items()}
        err = max(err, key(api, layer, tg, f))
    return err


def bake_for_export(api, first, last, nodes=None, tol=1e-3):
    """Collapse the layers by hand: sample on-screen totals of every layered node, delete the layers, write the
    totals on Base every frame (linear). Run on a COPY saved before export, then reopen the layered scene.
    Returns the max difference between the screen before and after (should be ~0)."""
    hit = layered(api, nodes)
    todo = sorted({n for h in hit.values() for n in h})
    if not todo:
        return 0.0
    frames = list(range(first, last + 1))
    before = {f: _read(api, todo, f) for f in frames}
    while len(api.layers()) > 1:
        api.delete_layer(len(api.layers()) - 1)
    api.set_active_layer(0)
    api.select(todo)
    for f in frames:
        api.set_frame(f)
        api.set_key()
        for n in todo:
            for c, v in before[f][n].items():
                if v is not None:
                    api.move_key(n + "." + c, f, f, v)
                    api.set_key_interp(n + "." + c, f, "linear")
    err = 0.0
    for f in frames:
        got = _read(api, todo, f)
        for n in todo:
            for c, v in before[f][n].items():
                if v is not None and got[n][c] is not None:
                    err = max(err, abs(got[n][c] - v))
    return err
