"""Overlapper - overlapping action (follow-through / drag) for chains in Frolvy.

Select the chain controls ROOT -> TIP (click order), open Plugins > Overlapper, press Apply.
The first node is the DRIVER (body / base of the tail), never changed. Link i (1..n) drags behind it: its WORLD rotation
becomes the driver's rotation i * Lag frames earlier, so the tip trails the base. What a link already animates is kept
(own keys + the drag on top).
The result goes on a NEW override layer "Overlap" (weight = Amount %), Base keys are never edited: weight 0 or
delete the layer = back to the original.

Inside Frolvy (execute_code):
    exec(open(r'<repo>/tools/frolvy_plugins/overlapper/overlapper.py', encoding='utf-8').read())
    overlap(api, ['tail1', 'tail2', 'tail3'], lag=2.0, amount=1.0, loop=False)

Rules:
  - only rotation channels (rx ry rz) are lagged; translate / scale are left alone;
  - lag may be fractional (2.5 = lerp between frames); before the first frame the pose is held;
  - loop=True wraps around the range (idle / run / walk) so F-last flows into F-first;
  - originals are sampled BEFORE the layer is made, so nothing feeds back into itself.
"""
import math

ROT = ("rx", "ry", "rz")


def _range(api, first, last):
    a, b = api.frame_range()
    return (a if first is None else first), (b if not last else last)


def _sample(api, nodes, frames):
    """{frame: {node: (rx, ry, rz)}} of what the rig shows now (all layers)."""
    out = {}
    for f in frames:
        api.set_frame(f)
        out[f] = {n: tuple(api.get_attr(n + "." + c) for c in ROT) for n in nodes}
    return out


def _at(table, node, t, first, last, loop):
    """Value of node at float frame t from the sampled table."""
    span = last - first + 1
    def val(f):
        f = first + ((f - first) % span) if loop else min(max(f, first), last)
        return table[f][node]
    f0 = math.floor(t)
    k = t - f0
    a, b = val(f0), val(f0 + 1)
    return tuple(x + (y - x) * k for x, y in zip(a, b))


def overlap(api, nodes=None, lag=2.0, amount=1.0, loop=False, first=None, last=None, layer_name="Overlap", log=print):
    nodes = list(nodes or api.selection())
    if len(nodes) < 2:
        log("Overlapper: select the driver, then the chain links root -> tip (2+ nodes)")
        return False
    a, b = _range(api, first, last)
    keep_frame = api.current_frame()
    table = _sample(api, nodes, range(a, b + 1))
    keep_sel = list(api.selection())
    api.create_layer(layer_name, "override")
    li = api.active_layer()
    drv = nodes[0]
    links = nodes[1:]
    for f in range(a, b + 1):
        api.set_frame(f)
        for i, n in enumerate(links, 1):
            late = _at(table, drv, f - i * lag, a, b, loop)
            prev = _at(table, drv, f - (i - 1) * lag, a, b, loop)
            for c, own, x1, x0 in zip(ROT, table[f][n], late, prev):
                api.set_attr(n + "." + c, own + x1 - x0)
        api.select(links)
        api.set_key()
    api.set_layer_weight(li, amount)
    api.set_frame(keep_frame)
    api.select(keep_sel)
    log("Overlapper: %d links after the driver, lag %.1f F, frames %d-%d, layer '%s' weight %d%%" % (len(nodes) - 1, lag, a, b, layer_name, round(amount * 100)))
    return True


def register(api):
    p = api.panel("Overlapper")
    p.heading("Overlapper")
    p.text("hint", "Chon: khop dan (than) truoc, roi cac khop duoi/toc tu goc -> ngon, bam Apply. Ra layer 'Overlap' moi, Base khong bi sua.", tone="muted")
    p.int_field("lag", "Lag moi khop (x0.1 F)", 20, 0, 100, "20 = tre 2 frame sau khop truoc")
    p.int_field("amount", "Amount %", 100, 0, 100, "weight cua layer Overlap")
    p.int_field("first", "Frame dau (0 = dau scene)", 0, 0, 9999)
    p.int_field("last", "Frame cuoi (0 = het scene)", 0, 0, 9999)
    p.checkbox("loop", "Loop (idle / run / walk)", False)

    def go():
        overlap(api, lag=p.get("lag") / 10.0, amount=p.get("amount") / 100.0, loop=bool(p.get("loop")),
                first=p.get("first") or None, last=p.get("last") or None, log=api.log)

    p.button("apply", "Apply", go)
    api.command("Overlapper", p.open)
