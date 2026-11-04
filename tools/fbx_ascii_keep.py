"""Keep only part of an ASCII FBX (Frolvy export): the joint tree under given root Models plus
every Mesh Model. Everything else (rig controls, DEF/fit joints, groups) is dropped with its
NodeAttribute, AnimationCurveNode/AnimationCurve and connections; Definitions counts are fixed.

Frolvy exports the whole scene and has no "export selected", and deleting nodes before export
does not stop them being written (2026-11-02), so G-LumberCity clips are cleaned here.

usage: py tools/fbx_ascii_keep.py in.fbx out.fbx [--root root] [--root other] [--no-meshes]
"""
import argparse
import collections
import re
import sys

HEAD = re.compile(r'^\t(\w+): (\d+), "([^"]*)", "([^"]*)" \{')
CONN = re.compile(r'^\tC: "(\w+)",(\d+),(\d+)')


def parse(text):
    lines = text.split("\n")
    o0 = next(i for i, l in enumerate(lines) if l.startswith("Objects:"))
    objs, i = [], o0 + 1
    while not lines[i].startswith("}"):
        m = HEAD.match(lines[i])
        if not m:
            i += 1
            continue
        depth, j = 0, i
        while True:
            depth += lines[j].count("{") - lines[j].count("}")
            if depth == 0:
                break
            j += 1
        objs.append({"type": m.group(1), "id": int(m.group(2)), "name": m.group(3),
                     "sub": m.group(4), "span": (i, j)})
        i = j + 1
    c0 = next(i for i, l in enumerate(lines) if l.startswith("Connections:"))
    conns = []
    for k in range(c0 + 1, len(lines)):
        if lines[k].startswith("}"):
            break
        m = CONN.match(lines[k])
        if m:
            conns.append((k, m.group(1), int(m.group(2)), int(m.group(3))))
    return lines, objs, conns


def keep_part(text, roots=("root",), meshes=True):
    lines, objs, conns = parse(text)
    by_id = {o["id"]: o for o in objs}
    kids = collections.defaultdict(list)
    for _, kind, a, b in conns:
        if kind == "OO":
            kids[b].append(a)
    models = [o for o in objs if o["type"] == "Model"]
    keep = set()
    todo = [o["id"] for o in models if o["name"].split("::")[-1] in roots]
    if len(todo) != len(roots):
        raise SystemExit("root Model not found: %s" % (roots,))
    while todo:
        n = todo.pop()
        if n in keep:
            continue
        keep.add(n)
        todo += [k for k in kids[n] if by_id.get(k, {}).get("type") == "Model"]
    if meshes:
        keep |= {o["id"] for o in models if o["sub"] == "Mesh"}
    drop = {o["id"] for o in models if o["id"] not in keep}
    if not meshes:
        # anim-only FBX (user 2026-11-03 "fbx chỉ giữ joint với anim thôi ko cần mesh"): the meshes' Geometry
        # and their skin Deformers (Skin + Cluster) go too, so nothing is left pointing at a dropped mesh
        drop |= {o["id"] for o in objs if o["type"] in ("Geometry", "Deformer")}
    # dependants of dropped models: their attribute, curve nodes, then those curves
    for _ in range(3):
        for _, kind, a, b in conns:
            t = by_id.get(a, {}).get("type")
            if b in drop and t in ("NodeAttribute", "AnimationCurveNode", "AnimationCurve"):
                drop.add(a)
            if a in drop and by_id.get(b, {}).get("type") == "NodeAttribute":
                drop.add(b)
    clusters_on_dropped = [by_id[a]["name"] for _, kind, a, b in conns
                           if a in drop and by_id.get(a, {}).get("type") == "Model"
                           and by_id.get(b, {}).get("type") == "Deformer"]
    if clusters_on_dropped:
        raise SystemExit("skin clusters use dropped joints: %s" % clusters_on_dropped[:10])
    cut = set()
    for o in objs:
        if o["id"] in drop:
            cut.update(range(o["span"][0], o["span"][1] + 1))
    for k, kind, a, b in conns:
        if a in drop or b in drop:
            cut.add(k)
            if k > 0 and lines[k - 1].lstrip().startswith(";"):
                cut.add(k - 1)
    out = [l for i, l in enumerate(lines) if i not in cut]
    in_objects = {o["type"] for o in objs}  # GlobalSettings lives outside Objects: keep its count
    left = collections.Counter(o["type"] for o in objs if o["id"] not in drop)
    text = "\n".join(out)

    def type_count(mm):
        kind, old = mm.group(2), mm.group(3)
        return mm.group(1) + (str(left[kind]) if kind in in_objects else old)

    def fix_counts(m):
        block = re.sub(r'(ObjectType: "(\w+)" \{\s*\n\s*Count: )(\d+)', type_count, m.group(0))
        total = sum(int(c) for c in re.findall(r'ObjectType: "\w+" \{\s*\n\s*Count: (\d+)', block))
        return re.sub(r'(\n\tCount: )\d+', lambda mm: mm.group(1) + str(total), block, count=1)

    text = re.sub(r'Definitions:  \{.*?\n\}', fix_counts, text, count=1, flags=re.S)
    kept = sorted(by_id[i]["name"].split("::")[-1] for i in keep)
    return text, kept, len([d for d in drop if by_id[d]["type"] == "Model"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--root", action="append")
    ap.add_argument("--no-meshes", action="store_true")
    a = ap.parse_args()
    text = open(a.src, encoding="utf-8").read()
    out, kept, n_drop = keep_part(text, tuple(a.root or ["root"]), not a.no_meshes)
    open(a.dst, "w", encoding="utf-8", newline="\n").write(out)
    print("kept %d models, dropped %d -> %s" % (len(kept), n_drop, a.dst))


if __name__ == "__main__":
    sys.exit(main())
