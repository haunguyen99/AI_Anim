"""Spine Live: sửa curve (graph editor) và lưới mesh (kiểu Spine) trên skeleton JSON 4.2.

Gọi từ spine_live.handle_post:
  POST /api/spine/timeline   {json, anim, bone, channel: rotate|translate|scale, keys:[...]}  thay toàn bộ key của một kênh
  POST /api/spine/mesh/trace {json, slot, attachment, detail, maxEdge, spacing}  -> {hull, inner, w, h} (px ảnh, chưa ghi)
  POST /api/spine/mesh/tri   {hull, inner, w, h}                                   -> {triangles} (xem trước)
  POST /api/spine/mesh/apply {json, slot, attachment, hull, inner}                 ghi lưới mới (region -> mesh được)
Toạ độ lưới: px trong ảnh của attachment (x phải, y xuống), gốc ở góc trên trái.
Weight khi đổi lưới: nội suy từ lưới cũ (tam giác chứa điểm, barycentric), ngoài lưới cũ lấy đỉnh cũ gần nhất;
region -> mesh: không weight, gắn vào xương của slot.
"""
import json, math, os

import numpy as np

KINDS = {"rotate": ["value"], "translate": ["x", "y"], "scale": ["x", "y"], "shear": ["x", "y"]}

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



# ---------------- curve ----------------
def _clean_keys(keys, fields):
    clean, last = [], -1
    for k in keys:
        t = ktime(k.get("time", 0))
        if t <= last:
            raise ValueError("thời gian key phải tăng dần")
        last = t
        o = {"time": t}
        for f in fields:
            o[f] = round(float(k.get(f, 0)), 4)
        c = k.get("curve")
        if c == "stepped":
            o["curve"] = "stepped"
        elif isinstance(c, list) and len(c) == 4 * len(fields):
            o["curve"] = [round(float(v), 4) for v in c]
        clean.append(o)
    if clean:
        clean[-1].pop("curve", None)
    return clean


def reduce_anim(b, safe, backup, save):
    """Graph > Giảm key (2026-11-05, người dùng: "đang như mocap, quá nhiều key ... chỉ để những key chính mà vẫn giữ được
    chuyển động y nguyên"): {json, anim, bones?: [tên] (bỏ trống = mọi xương), tol?: hệ số ngưỡng (1 = xoay 0.15°,
    dời 0.3 px, scale 0.003)} -> lấy mẫu từng frame của mỗi kênh rồi dựng lại ít key nhất (tools/spine/key_reduce.py).
    Chỉ sửa anim được gửi (góp ý anim chỉ áp cho anim đang mở). Bỏ qua kênh có key stepped hoặc dưới 3 key."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "spine"))
    import key_reduce as KR
    js = safe(b.get("json", ""))
    if not js or not os.path.isfile(js):
        raise ValueError("không thấy file")
    data = json.load(open(js, encoding="utf8"))
    anim = b.get("anim")
    an = (data.get("animations") or {}).get(anim)
    if an is None:
        raise ValueError("không có anim " + str(anim))
    fps = (data.get("skeleton") or {}).get("fps") or 30
    k = max(0.2, float(b.get("tol") or 1.0))
    want = set(b.get("bones") or [])
    before = after = 0
    done = []
    for bone, tls in (an.get("bones") or {}).items():
        if want and bone not in want:
            continue
        for ch, keys in list(tls.items()):
            if ch not in KINDS or len(keys) < 3 or KR.has_stepped(keys):
                continue
            fl = KINDS[ch]
            f0 = round(keys[0].get("time", 0) * fps)
            n = round(keys[-1].get("time", 0) * fps)
            if n - f0 < 2:
                continue
            dflt = {"x": 1.0, "y": 1.0} if ch == "scale" else None
            V = KR.sample_timeline(keys, fl, n, fps=fps, defaults=dflt)
            V = [v[f0:] for v in V]
            nk = KR.reduce_keys(V, fl, KR.TOL[ch] * k, fps=fps)
            if len(nk) >= len(keys):
                continue
            if f0:   # kênh bắt đầu sau F0: dời thời gian về đúng chỗ
                t0 = f0 / fps
                for q in nk:
                    q["time"] = ktime(q.get("time", 0) + t0, fps)
                    if isinstance(q.get("curve"), list):
                        q["curve"] = [round(x + t0, 6) if i % 2 == 0 else x for i, x in enumerate(q["curve"])]
            before += len(keys); after += len(nk)
            tls[ch] = nk
            done.append(bone + "." + ch)
    if not done:
        return {"channels": 0, "before": 0, "after": 0}
    backup(js)
    save(js, data)
    return {"channels": len(done), "before": before, "after": after}


def set_timelines(b, safe, backup, save):
    """ghi nhiều kênh một lần (tool Physics): {json, anim, items: [{bone, channel, keys}], what} -> một bản sao lưu."""
    js = safe(b.get("json", ""))
    if not js or not os.path.isfile(js):
        raise ValueError("không thấy file")
    anim, items = b.get("anim"), b.get("items") or []
    if not anim or not items:
        raise ValueError("thiếu anim / kênh")
    data = json.load(open(js, encoding="utf8"))
    names = {x["name"] for x in data.get("bones", [])}
    bt = data.setdefault("animations", {}).setdefault(anim, {}).setdefault("bones", {})
    for it in items:
        bone, ch = it.get("bone"), it.get("channel")
        if bone not in names or ch not in KINDS:
            raise ValueError("kênh không hợp lệ: %s.%s" % (bone, ch))
        clean = _clean_keys(it.get("keys") or [], KINDS[ch])
        tl = bt.setdefault(bone, {})
        if clean:
            tl[ch] = clean
        else:
            tl.pop(ch, None)
    ph = b.get("physics")   # {bone: {offs, src} | None}: lưu trong file để lần chạy sau trừ ra (không cộng dồn), Hoàn tác khớp
    if isinstance(ph, dict):
        store = data.setdefault("spineLive", {}).setdefault("physics", {}).setdefault(anim, {})
        for bone, offs in ph.items():
            if offs is None:
                store.pop(bone, None)
            else:   # offs: {offs: [...], src: key gốc trước lần nướng đầu (giữ bản đầu tiên)}
                old = store.get(bone) or {}
                store[bone] = {"fps": (data.get("skeleton") or {}).get("fps") or 30,
                               "offs": [round(float(v), 3) for v in offs["offs"]], "src": old.get("src") or offs.get("src")}
    backup(js, b.get("what") or "Physics")
    save(js, data)
    return {"channels": len(items)}


def set_timeline(b, safe, backup, save):
    js = safe(b.get("json", ""))
    if not js or not os.path.isfile(js):
        raise ValueError("không thấy file")
    anim, bone, ch, keys = b.get("anim"), b.get("bone"), b.get("channel"), b.get("keys")
    if ch not in KINDS or not anim or not bone or not isinstance(keys, list):
        raise ValueError("thiếu anim / xương / kênh / key")
    fields = KINDS[ch]
    clean, last = [], -1
    for k in keys:
        t = ktime(k.get("time", 0))
        if t <= last:
            raise ValueError("thời gian key phải tăng dần")
        last = t
        o = {"time": t}
        for f in fields:
            o[f] = round(float(k.get(f, 0)), 4)
        c = k.get("curve")
        if c == "stepped":
            o["curve"] = "stepped"
        elif isinstance(c, list) and len(c) == 4 * len(fields):
            o["curve"] = [round(float(v), 4) for v in c]
        clean.append(o)
    if clean:
        clean[-1].pop("curve", None)
    data = json.load(open(js, encoding="utf8"))
    if bone not in {x["name"] for x in data.get("bones", [])}:
        raise ValueError("không có xương " + bone)
    bt = data.setdefault("animations", {}).setdefault(anim, {}).setdefault("bones", {})
    tl = bt.setdefault(bone, {})
    if clean:
        tl[ch] = clean
    else:
        tl.pop(ch, None)
        if not tl:
            bt.pop(bone, None)
    backup(js)
    save(js, data)
    return {"keys": len(clean)}


# ---------------- weight: bind tự động + lưu weight sơn tay ----------------
def _mesh_world(data, slot_name, att_name):
    slot = next((s for s in data.get("slots", []) if s["name"] == slot_name), None)
    if not slot:
        raise ValueError("không có slot " + slot_name)
    skin, a = find_attachment(data, slot_name, att_name)
    if a.get("type") != "mesh":
        raise ValueError("chỉ bind / sơn weight được trên mesh: mở Lưới… và Áp dụng để đổi region thành mesh trước")
    W = setup_world(data)
    names = [x["name"] for x in data["bones"]]
    px, world, weights, tris = old_mesh(a, slot["bone"], W, names)
    return slot, skin, a, W, names, world


def _anchor_zero(per, world, W, keep):
    """xương "đã bind nhưng 0 %" (2026-11-18, người dùng: bind thêm xương thì chỉ thêm xương đó để tự sơn weight ở Fix
    Weight): mesh weighted chỉ lưu xương có trong từng đỉnh, nên xương 0 % ở mọi đỉnh sẽ mất khỏi danh sách bind.
    Giữ nó bằng một mục weight 0 ở đỉnh gần gốc xương nhất còn chỗ (< 4 xương). Trả lại per (đã sửa tại chỗ)."""
    for n in keep:
        if n not in W or any(wd.get(n, 0) > 0 for wd in per):
            continue
        x0, y0 = W[n][4], W[n][5]
        order = sorted(range(len(world)), key=lambda i: (world[i][0] - x0) ** 2 + (world[i][1] - y0) ** 2)
        i = next((i for i in order if len([k for k, v in per[i].items() if v > 0 or k in keep]) < 4), None)
        if i is not None:
            per[i] = dict(per[i]); per[i][n] = 0.0
    return per


def _write_weights(a, W, names, world, per_vertex):
    """per_vertex: [{tên xương: w}] -> vertices JSON (weighted), toạ độ local tính lại từ vị trí thế giới ở setup.
    Mục weight đúng 0.0 (đặt bởi _anchor_zero) được giữ để xương 0 % vẫn nằm trong danh sách bind."""
    bidx = {n: i for i, n in enumerate(names)}
    verts = []
    for (wx, wy), wd in zip(world, per_vertex):
        wd = {k: float(v) for k, v in wd.items() if k in bidx and (float(v) >= 0.005 or (v == 0.0 and isinstance(v, float)))}
        if not wd:
            raise ValueError("có đỉnh không còn weight nào")
        tot = sum(wd.values())
        verts.append(len(wd))
        for name, w in sorted(wd.items(), key=lambda kv: -kv[1]):
            lx, ly = apply_m(inv_m(W[name]), wx, wy)
            verts += [bidx[name], round(lx, 3), round(ly, 3), round(w / tot, 4)]
    a["vertices"] = verts


def _seg_dist(p, b, W, L):
    a, bb, c, d, x, y = W
    if L <= 0:
        return math.hypot(p[0] - x, p[1] - y)
    ex, ey = x + a * L, y + c * L
    dx, dy = ex - x, ey - y
    u = max(0, min(1, ((p[0] - x) * dx + (p[1] - y) * dy) / (dx * dx + dy * dy)))
    return math.hypot(x + dx * u - p[0], y + dy * u - p[1])


def bind_auto(b, safe, backup, save):
    """Bind như Spine: weight tự động theo khoảng cách tới đoạn xương (nghịch đảo bình phương, giữ 4 xương gần nhất)."""
    js = safe(b.get("json", ""))
    data = json.load(open(js, encoding="utf8"))
    bones = [n for n in (b.get("bones") or [])]
    slot, skin, a, W, names, world = _mesh_world(data, b["slot"], b["attachment"])
    # "add" (2026-11-05, người dùng: "chọn 1 xương và nhấn Bind thì sẽ là bind thêm chứ không phải chỉ bind 1 xương đấy"):
    # mesh đã có weight -> giữ weight đang có (kể cả chỗ sửa tay), chỉ chia phần cho xương mới ở vùng gần nó.
    add = [n for n in (b.get("add") or []) if n in W]
    old_w = None
    if add and len(a["vertices"]) != len(a["uvs"]):
        old_w = old_mesh(a, slot["bone"], W, names)[2]
        add = [n for n in add if not any(n in wd for wd in old_w)]
        if not add:
            raise ValueError("các xương chọn đã bind sẵn")
        bones = list(dict.fromkeys([n for wd in old_w for n in wd] + add))
        # 2026-11-18 (người dùng: "bind thêm sau khi đã bind thì chỉ thêm xương đó, để có thể tự chỉnh add thêm những vùng
        # thủ công bên fix weight"): mặc định chỉ thêm xương (0 %), weight cũ giữ nguyên y hệt; "mix": true = cách cũ
        # (xương mới tự nhận phần ở vùng gần nó). Tính lại toàn bộ = nút Auto weight (bind không có "add").
        if not b.get("mix"):
            per = _anchor_zero([dict(wd) for wd in old_w], world, W, add)
            _write_weights(a, W, names, world, per)
            backup(js)
            save(js, data)
            return {"vertices": len(world), "bones": bones, "added": add, "parent": slot["bone"], "reparented": False,
                    "zero": True}
    bset = [n for n in bones if n in W]
    if not bset:
        raise ValueError("chọn ít nhất một xương để bind")
    L = {x["name"]: x.get("length", 0) for x in data["bones"]}
    size = max(1.0, max(max(p[0] for p in world) - min(p[0] for p in world), max(p[1] for p in world) - min(p[1] for p in world)))
    # 2026-10-31 (người dùng: "1 point mesh có thể được bind bởi nhiều xương để smooth chuyển động giữa các xương"):
    # độ mềm lớn hơn (điểm gần khớp chia cho nhiều xương) + làm mượt weight theo đỉnh kề trên lưới, giữ tối đa 4 xương.
    # weight giảm theo hàm mũ của CHÊNH khoảng cách so với xương gần nhất: điểm nghiêng hẳn về một xương ~100%, vùng khớp
    # (hai xương gần bằng nhau) ~50/50; "soft" = bề rộng vùng chuyển (tỉ lệ cỡ mesh). Nghịch đảo khoảng cách trộn quá đều ở mesh rộng.
    soft = max(1e-3, float(b.get("soft", 0.05)) * size)
    per = []
    for p in world:
        ds = {n: _seg_dist(p, n, W[n], L[n]) for n in bset}
        d0 = min(ds.values())
        ws = {n: math.exp(-(d - d0) / soft) for n, d in ds.items()}
        tot = sum(ws.values())
        per.append({n: w / tot for n, w in ws.items()})
    nb = [set() for _ in world]
    tri = a.get("triangles") or []
    for i in range(0, len(tri) - 2, 3):
        x, y, z = tri[i], tri[i + 1], tri[i + 2]
        nb[x] |= {y, z}; nb[y] |= {x, z}; nb[z] |= {x, y}
    for _ in range(int(b.get("smooth", 1))):
        nxt = []
        for i, wd in enumerate(per):
            if not nb[i]:
                nxt.append(wd); continue
            avg = {n: sum(per[j].get(n, 0) for j in nb[i]) / len(nb[i]) for n in bset}
            nxt.append({n: 0.5 * wd.get(n, 0) + 0.5 * avg[n] for n in bset})
        per = nxt
    if old_w is not None:   # bind thêm: phần của xương mới lấy theo tính tự động, phần còn lại chia theo weight cũ
        mixed = []
        for wd, ow in zip(per, old_w):
            s_new = sum(wd.get(n, 0) for n in add)
            tot = sum(ow.values()) or 1
            d = {k: v / tot * (1 - s_new) for k, v in ow.items()}
            for n in add:
                d[n] = d.get(n, 0) + wd.get(n, 0)
            mixed.append(d)
        per = mixed
    out = []
    for wd in per:
        top = sorted(((n, w) for n, w in wd.items() if w >= 0.01), key=lambda kv: -kv[1])[:4]
        tot = sum(w for _, w in top) or 1
        out.append({n: w / tot for n, w in top})
    per = out
    _write_weights(a, W, names, world, per)
    backup(js)
    save(js, data)
    tot = {n: sum(wd.get(n, 0) for wd in per) for n in bset}
    main = max(tot, key=tot.get)
    moved = None
    if slot["bone"] != main:   # đổi cha, các ảnh khác trong slot giữ nguyên chỗ (set_parent); mesh có weight không dời
        moved = set_parent({"json": b.get("json"), "slot": slot["name"], "bone": main}, safe, lambda js: None, save)
    return {"vertices": len(world), "bones": bset, "added": add if old_w is not None else [], "parent": main, "reparented": bool(moved)}


def set_weights(b, safe, backup, save):
    js = safe(b.get("json", ""))
    data = json.load(open(js, encoding="utf8"))
    slot, skin, a, W, names, world = _mesh_world(data, b["slot"], b["attachment"])
    per = b.get("weights") or []
    if len(per) != len(world):
        raise ValueError(f"số đỉnh không khớp ({len(per)} / {len(world)}): file vừa đổi? nạp lại rồi sơn lại")
    if len(a["vertices"]) != len(a["uvs"]):     # giữ xương đang bind mà vẫn 0 % (bind thêm chưa sơn) trong danh sách
        had = {n for wd in old_mesh(a, slot["bone"], W, names)[2] for n in wd}
        per = _anchor_zero([dict(wd) for wd in per], world, W, sorted(had))
    _write_weights(a, W, names, world, per)
    backup(js)
    save(js, data)
    return {"vertices": len(world)}


# ---------------- đổi xương cha (parent) của slot, ảnh đứng yên ----------------
def _mul(m, n):
    a, b, c, d, x, y = m
    A, B, C, D, X, Y = n
    return (a * A + b * C, a * B + b * D, c * A + d * C, c * B + d * D, a * X + b * Y + x, c * X + d * Y + y)


def set_parent(b, safe, backup, save):
    js = safe(b.get("json", ""))
    if not js or not os.path.isfile(js):
        raise ValueError("không thấy file")
    data = json.load(open(js, encoding="utf8"))
    slot = next((s for s in data.get("slots", []) if s["name"] == b.get("slot")), None)
    if not slot:
        raise ValueError("không có slot " + str(b.get("slot")))
    nb = b.get("bone")
    W = setup_world(data)
    if nb not in W:
        raise ValueError("không có xương " + str(nb))
    ob = slot["bone"]
    if ob == nb:
        return {"slot": slot["name"], "bone": nb, "changed": 0}
    rel = _mul(inv_m(W[nb]), W[ob])   # toạ độ xương cũ -> xương mới
    changed = 0
    for skin in data.get("skins", []):
        for name, a in ((skin.get("attachments") or {}).get(slot["name"]) or {}).items():
            t = a.get("type", "region")
            if t == "region":
                r = math.radians(a.get("rotation", 0)); sx, sy = a.get("scaleX", 1), a.get("scaleY", 1)
                loc = (math.cos(r) * sx, -math.sin(r) * sy, math.sin(r) * sx, math.cos(r) * sy, a.get("x", 0), a.get("y", 0))
                A, B, C, D, X, Y = _mul(rel, loc)
                nsx = math.hypot(A, C); rot = math.degrees(math.atan2(C, A)); nsy = (A * D - B * C) / (nsx or 1)
                for k, v, dflt in (("x", X, 0), ("y", Y, 0), ("rotation", rot, 0), ("scaleX", nsx, 1), ("scaleY", nsy, 1)):
                    if abs(v - dflt) < 1e-5:
                        a.pop(k, None)
                    else:
                        a[k] = round(v, 4)
                changed += 1
            elif "vertices" in a and "uvs" in a and len(a["vertices"]) == len(a["uvs"]) or (t in ("clipping", "boundingbox", "path") and "vertices" in a
                                                                                          and len(a["vertices"]) == 2 * a.get("vertexCount", 0)):
                v = a["vertices"]
                for i in range(0, len(v), 2):
                    v[i], v[i + 1] = (round(q, 3) for q in apply_m(rel, v[i], v[i + 1]))
                changed += 1
            elif t == "point":
                a["x"], a["y"] = (round(q, 3) for q in apply_m(rel, a.get("x", 0), a.get("y", 0)))
                changed += 1
            # mesh có weight: đỉnh tính theo các xương bind, đổi xương của slot không làm ảnh dời
    slot["bone"] = nb
    backup(js)
    save(js, data)
    return {"slot": slot["name"], "from": ob, "bone": nb, "changed": changed}


# ---------------- tab Setup: lưu tư thế gốc ----------------
def set_setup(b, safe, backup, save):
    """bones: {tên: {rotate, x, y, sx?, sy?}} giá trị local tuyệt đối -> ghi vào bones[] (setup). Key anim tương đối nên dời theo."""
    js = safe(b.get("json", ""))
    if not js or not os.path.isfile(js):
        raise ValueError("không thấy file")
    data = json.load(open(js, encoding="utf8"))
    B = {x["name"]: x for x in data.get("bones", [])}
    n = 0
    for name, v in (b.get("bones") or {}).items():
        x = B.get(name)
        if not x:
            continue
        for k, f, dflt in (("rotation", "rotate", 0), ("x", "x", 0), ("y", "y", 0), ("scaleX", "sx", 1), ("scaleY", "sy", 1),
                           ("shearX", "shx", 0), ("shearY", "shy", 0)):
            if f in v:
                val = round(float(v[f]), 4)
                if abs(val - dflt) < 1e-6:
                    x.pop(k, None)
                else:
                    x[k] = val
        n += 1
    if not n:
        raise ValueError("không có xương nào để lưu")
    backup(js)
    save(js, data)
    return {"bones": n}


# ---------------- xương ở setup pose ----------------
def setup_world(data):
    """name -> (a, b, c, d, x, y) ma trận thế giới ở setup (bỏ qua shear / inherit đặc biệt)."""
    W = {}
    for bn in data.get("bones", []):
        r = math.radians(bn.get("rotation", 0))
        sx, sy = bn.get("scaleX", 1), bn.get("scaleY", 1)
        la, lb, lc, ld = math.cos(r) * sx, -math.sin(r) * sy, math.sin(r) * sx, math.cos(r) * sy
        x, y = bn.get("x", 0), bn.get("y", 0)
        p = W.get(bn.get("parent"))
        if p:
            pa, pb, pc, pd, px, py = p
            W[bn["name"]] = (pa * la + pb * lc, pa * lb + pb * ld, pc * la + pd * lc, pc * lb + pd * ld,
                             pa * x + pb * y + px, pc * x + pd * y + py)
        else:
            W[bn["name"]] = (la, lb, lc, ld, x, y)
    return W


def apply_m(m, x, y):
    a, b, c, d, tx, ty = m
    return a * x + b * y + tx, c * x + d * y + ty


def inv_m(m):
    a, b, c, d, tx, ty = m
    det = a * d - b * c
    ia, ib, ic, id_ = d / det, -b / det, -c / det, a / det
    return ia, ib, ic, id_, -(ia * tx + ib * ty), -(ic * tx + id_ * ty)


def find_attachment(data, slot, att):
    for skin in data.get("skins", []):
        a = (skin.get("attachments") or {}).get(slot, {}).get(att)
        if a is not None:
            return skin, a
    raise ValueError(f"không thấy attachment {att} ở slot {slot}")


def old_mesh(a, slot_bone, W, bone_names):
    """đỉnh lưới cũ: px ảnh, vị trí thế giới (setup), weight {xương: w}, và tam giác."""
    w, h = a["width"], a["height"]
    uv = a["uvs"]
    n = len(uv) // 2
    px = [(uv[2 * i] * w, uv[2 * i + 1] * h) for i in range(n)]
    v = a["vertices"]
    world, weights = [], []
    if len(v) == len(uv):   # không weight: toạ độ trong xương của slot
        m = W[slot_bone]
        for i in range(n):
            world.append(apply_m(m, v[2 * i], v[2 * i + 1]))
            weights.append({slot_bone: 1.0})
    else:
        i = 0
        while i < len(v):
            cnt = int(v[i]); i += 1
            sx = sy = 0.0; wd = {}
            for _ in range(cnt):
                bi, bx, by, ww = int(v[i]), v[i + 1], v[i + 2], v[i + 3]; i += 4
                name = bone_names[bi]
                x, y = apply_m(W[name], bx, by)
                sx += x * ww; sy += y * ww; wd[name] = wd.get(name, 0) + ww
            world.append((sx, sy)); weights.append(wd)
    tris = [a["triangles"][k:k + 3] for k in range(0, len(a["triangles"]), 3)]
    return px, world, weights, tris


def region_px_to_world(a, slot_bone, W):
    """region: px ảnh -> thế giới (setup) theo x, y, rotation, scale của region."""
    w, h = a.get("width", 0), a.get("height", 0)
    r = math.radians(a.get("rotation", 0))
    sx, sy = a.get("scaleX", 1), a.get("scaleY", 1)
    cr, sr = math.cos(r), math.sin(r)
    m = W[slot_bone]

    def f(x, y):
        lx, ly = (x - w / 2) * sx, (h / 2 - y) * sy
        return apply_m(m, a.get("x", 0) + lx * cr - ly * sr, a.get("y", 0) + lx * sr + ly * cr)
    return f


def affine_fit(src, dst):
    """world = A * px + t (bình phương nhỏ nhất)."""
    S = np.array([[x, y, 1] for x, y in src], float)
    D = np.array(dst, float)
    M, *_ = np.linalg.lstsq(S, D, rcond=None)
    return lambda x, y: tuple(np.array([x, y, 1.0]) @ M)


def interp_weights(p, opx, oweights, otris):
    """weight tại p (px) nội suy trong tam giác cũ chứa nó; ngoài lưới cũ: đỉnh cũ gần nhất."""
    x, y = p
    for t in otris:
        (x1, y1), (x2, y2), (x3, y3) = (opx[t[0]], opx[t[1]], opx[t[2]])
        det = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
        if abs(det) < 1e-9:
            continue
        l1 = ((y2 - y3) * (x - x3) + (x3 - x2) * (y - y3)) / det
        l2 = ((y3 - y1) * (x - x3) + (x1 - x3) * (y - y3)) / det
        l3 = 1 - l1 - l2
        if min(l1, l2, l3) >= -1e-4:
            out = {}
            for lam, vi in zip((l1, l2, l3), t):
                for k, w in oweights[vi].items():
                    out[k] = out.get(k, 0) + lam * w
            return out
    j = min(range(len(opx)), key=lambda i: (opx[i][0] - x) ** 2 + (opx[i][1] - y) ** 2)
    return dict(oweights[j])


# ---------------- trace + chia tam giác ----------------
def image_path(js, data, att_name, a):
    from spine_live import images_dir   # cùng thư mục tools/home
    d = images_dir(js)
    if not d:
        raise ValueError("skeleton không có thư mục images/ (sửa lưới chỉ làm trên file build có ảnh rời)")
    p = os.path.join(d, (a.get("path") or att_name) + ".png")
    if not os.path.isfile(p):
        raise ValueError("không thấy ảnh " + os.path.relpath(p))
    return p


def trace(b, safe):
    import cv2
    from PIL import Image
    js = safe(b.get("json", ""))
    data = json.load(open(js, encoding="utf8"))
    _, a = find_attachment(data, b["slot"], b["attachment"])
    img = np.array(Image.open(image_path(js, data, b["attachment"], a)).convert("RGBA"))
    alpha = img[:, :, 3]
    h, w = alpha.shape
    if b.get("points"):   # 2026-10-31: chỉ một số "Số điểm", bám sát ảnh mà không cắt vào ảnh (như Trace của Spine)
        return _trace_points(alpha, int(b["points"]))
    detail = float(b.get("detail", 3))          # độ bám viền (px, nhỏ = sát hơn, nhiều điểm hơn)
    max_edge = float(b.get("maxEdge", 120))     # cạnh viền dài nhất
    spacing = float(b.get("spacing", 0))        # khoảng cách điểm trong (0 = không thêm)
    pad = 4
    mask = (alpha > 8).astype(np.uint8)
    m2 = cv2.dilate(np.pad(mask, pad), np.ones((5, 5), np.uint8))
    cs, _ = cv2.findContours(m2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not cs:
        raise ValueError("ảnh trong suốt hoàn toàn")
    c = max(cs, key=cv2.contourArea)
    poly = cv2.approxPolyDP(c, max(0.5, detail), True)[:, 0, :].astype(float) - pad
    poly[:, 0] = poly[:, 0].clip(0, w); poly[:, 1] = poly[:, 1].clip(0, h)
    hull = []
    for i in range(len(poly)):
        p, q = poly[i], poly[(i + 1) % len(poly)]
        k = max(1, int(math.ceil(np.hypot(*(q - p)) / max(10, max_edge))))
        hull += [(float(p[0] + (q[0] - p[0]) * j / k), float(p[1] + (q[1] - p[1]) * j / k)) for j in range(k)]
    inner = []
    if spacing > 0:
        hp = np.array(hull, np.float32)
        for y in np.arange(spacing / 2, h, spacing):
            for x in np.arange(spacing / 2, w, spacing):
                if cv2.pointPolygonTest(hp, (float(x), float(y)), True) >= spacing * 0.45:
                    inner.append((float(x), float(y)))
    return {"hull": [list(map(lambda v: round(v, 2), p)) for p in hull], "inner": [[round(x, 2), round(y, 2)] for x, y in inner],
            "w": w, "h": h}


def _dp_outward(C, eps, out_tol, outside_sign):
    """Douglas-Peucker trên đường bao kín C (N x 2) nhưng không cho cắt vào trong: chia đoạn khi điểm bao lệch > eps
    (bất kỳ phía) hoặc lệch RA NGOÀI đoạn > out_tol (đoạn đó cắt vào ảnh). Trả chỉ số đỉnh giữ lại."""
    N = len(C)
    far = int(np.argmax(np.hypot(C[:, 0] - C[0, 0], C[:, 1] - C[0, 1])))
    keep = {0, far}
    stack = [(0, far), (far, N)]
    while stack:
        i, j = stack.pop()
        if j - i < 2:
            continue
        a, b = C[i], C[j % N]
        idx = np.arange(i + 1, j)
        P = C[idx % N]
        d = b - a
        L = math.hypot(*d) or 1.0
        sd = ((P[:, 0] - a[0]) * d[1] - (P[:, 1] - a[1]) * d[0]) / L * outside_sign   # > 0: điểm bao nằm ngoài đoạn
        k_abs = int(np.argmax(np.abs(sd)))
        k_out = int(np.argmax(sd))
        if sd[k_out] > out_tol:
            k = k_out
        elif abs(sd[k_abs]) > eps:
            k = k_abs
        else:
            continue
        m = int(idx[k])
        keep.add(m % N)
        stack += [(i, m), (m, j)]
    return sorted(keep)


def _dp_idx(C, eps):
    """Douglas-Peucker thường trên đường bao kín C -> chỉ số đỉnh giữ lại."""
    N = len(C)
    far = int(np.argmax(np.hypot(C[:, 0] - C[0, 0], C[:, 1] - C[0, 1])))
    keep, stack = {0, far}, [(0, far), (far, N)]
    while stack:
        i, j = stack.pop()
        if j - i < 2:
            continue
        a, b = C[i], C[j % N]
        idx = np.arange(i + 1, j)
        P = C[idx % N]
        d = b - a
        L = math.hypot(*d) or 1.0
        dist = np.abs((P[:, 0] - a[0]) * d[1] - (P[:, 1] - a[1]) * d[0]) / L
        k = int(np.argmax(dist))
        if dist[k] > eps:
            m = int(idx[k])
            keep.add(m % N)
            stack += [(i, m), (m, j)]
    return sorted(keep)


def _clip_rect(P, w, h):
    """Sutherland-Hodgman: cắt đa giác theo khung ảnh [0,w] x [0,h]."""
    def clip(P, inside, cut):
        out = []
        for i in range(len(P)):
            a, b = P[i - 1], P[i]
            ia, ib = inside(a), inside(b)
            if ib:
                if not ia:
                    out.append(cut(a, b))
                out.append(b)
            elif ia:
                out.append(cut(a, b))
        return out
    lerp = lambda a, b, t: (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
    for inside, cut in (
            (lambda p: p[0] >= 0, lambda a, b: lerp(a, b, (0 - a[0]) / (b[0] - a[0]))),
            (lambda p: p[0] <= w, lambda a, b: lerp(a, b, (w - a[0]) / (b[0] - a[0]))),
            (lambda p: p[1] >= 0, lambda a, b: lerp(a, b, (0 - a[1]) / (b[1] - a[1]))),
            (lambda p: p[1] <= h, lambda a, b: lerp(a, b, (h - a[1]) / (b[1] - a[1])))):
        P = clip(P, inside, cut)
        if not P:
            break
    out = []
    for p in P:   # bỏ điểm trùng
        if not out or math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) > 0.5:
            out.append(p)
    if len(out) > 2 and math.hypot(out[0][0] - out[-1][0], out[0][1] - out[-1][1]) <= 0.5:
        out.pop()
    return out


def _outward_hull(C, K, sign, extra, w, h):
    """đường bao kín C (N x 2), giữ đỉnh K: mỗi cạnh K[t] -> K[t+1] đẩy ra ngoài vừa đủ bao trọn đoạn C nó thay (+ extra px),
    đỉnh mới = giao hai cạnh kề (góc quá nhọn thì vát 2 điểm), cắt theo khung ảnh. Dùng chung cho Auto trace và Remesh."""
    N = len(C)
    lines = []   # mỗi cạnh: điểm gốc + hướng, đã đẩy ra ngoài
    for t in range(len(K)):
        i, j = K[t], K[(t + 1) % len(K)]
        a, b = C[i], C[j]
        d = b - a
        L = math.hypot(*d) or 1.0
        u = d / L
        nrm = np.array([u[1], -u[0]]) * sign   # pháp tuyến ra ngoài
        seg = C[np.arange(i, j if j > i else j + N) % N]
        off = max(0.0, float(np.max((seg - a) @ nrm))) + extra
        lines.append((a + nrm * off, u, nrm, off))
    P = []
    for t in range(len(lines)):
        (p1, u1, n1, o1), (p2, u2, n2, o2) = lines[t - 1], lines[t]
        den = u1[0] * u2[1] - u1[1] * u2[0]
        v = C[K[t]]
        if abs(den) < 0.08:   # hai cạnh gần thẳng hàng: dời đỉnh theo pháp tuyến trung bình
            nn = n1 + n2; nn = nn / (math.hypot(*nn) or 1)
            P.append(tuple(v + nn * max(o1, o2)))
            continue
        s1 = ((p2[0] - p1[0]) * u2[1] - (p2[1] - p1[1]) * u2[0]) / den
        q = p1 + u1 * s1
        lim = 6 * max(o1, o2, 1.0) + 4   # góc quá nhọn: không cho nhọn vô hạn, cắt vát bằng 2 điểm
        if math.hypot(*(q - v)) > lim:
            P.append(tuple(v + n1 * o1)); P.append(tuple(v + n2 * o2))
        else:
            P.append(tuple(q))
    return _clip_rect(P, w, h)


def remesh(b, safe):
    """Remesh (2026-11-03, người dùng: "auto giảm lại số lượng point và lưới theo setting mà vẫn ưu tiên giữ được hình"):
    giảm điểm trên CHÍNH lưới đang có (giữ chỗ người dùng sửa tay), không trace lại từ ảnh.
    Viền: DP trên viền hiện tại (lấy mẫu 1 px) với sai số nhỏ nhất cho đủ số điểm -> giữ góc / chỗ cong nhất, rồi đẩy cạnh
    ra ngoài vừa đủ bao viền cũ (viền mới luôn chứa viền cũ, không cắt vào ảnh nếu viền cũ không cắt).
    Điểm trong: chọn lại trong các điểm trong cũ bằng farthest point sampling (rải đều, xa viền trước), không sinh điểm mới.
    b: {json, slot, attachment, hull, inner, points (tổng điểm mong muốn), innerPct (% điểm trong, mặc định như lưới cũ)}"""
    import cv2
    from PIL import Image
    hull0 = np.array(b.get("hull") or [], float)
    inner0 = np.array(b.get("inner") or [], float).reshape(-1, 2)
    if len(hull0) < 3:
        raise ValueError("lưới cần ít nhất 3 điểm viền")
    js = safe(b.get("json", ""))
    data = json.load(open(js, encoding="utf8"))
    _, a = find_attachment(data, b["slot"], b["attachment"])
    alpha = np.array(Image.open(image_path(js, data, b["attachment"], a)).convert("RGBA"))[:, :, 3]
    h, w = alpha.shape
    total0 = len(hull0) + len(inner0)
    n = max(4, min(total0, int(b.get("points") or total0)))
    pct = b.get("innerPct")
    pct = (len(inner0) / total0 * 100) if pct is None else max(0.0, min(80.0, float(pct)))
    n_in = min(len(inner0), int(round(n * pct / 100)))
    n_hull = max(3, min(len(hull0), n - n_in))
    # viền: lấy mẫu dày (<= 1 px) trên viền cũ, đỉnh cũ nằm trong mẫu
    C, vid = [], []
    for i in range(len(hull0)):
        p, q = hull0[i], hull0[(i + 1) % len(hull0)]
        k = max(1, int(math.ceil(math.hypot(*(q - p)))))
        vid.append(len(C))
        C += [p + (q - p) * j / k for j in range(k)]
    C = np.array(C)
    area2 = float(np.sum(C[:, 0] * np.roll(C[:, 1], -1) - np.roll(C[:, 0], -1) * C[:, 1]))
    sign = 1.0 if area2 > 0 else -1.0
    if n_hull >= len(hull0):
        hull = [tuple(p) for p in hull0]
    else:
        lo, hi, K = 0.05, float(max(w, h)), None
        for _ in range(30):   # sai số nhỏ nhất mà số điểm viền <= n_hull
            mid = (lo + hi) / 2
            k = _dp_idx(C, mid)
            if len(k) <= n_hull:
                K, hi = k, mid
            else:
                lo = mid
        K = K or _dp_idx(C, hi)
        hull = _outward_hull(C, K, sign, 0.3, w, h)
    # điểm trong: farthest point sampling trong các điểm cũ, bỏ điểm quá sát viền mới
    inner = []
    if n_in > 0 and len(inner0):
        hp = np.array(hull, np.float32)
        dist_h = np.array([cv2.pointPolygonTest(hp, (float(x), float(y)), True) for x, y in inner0])
        cand = np.where(dist_h > 2)[0]
        if len(cand):
            P = inner0[cand]
            d = dist_h[cand].copy()          # khoảng cách tới viền / điểm đã chọn gần nhất
            for _ in range(min(n_in, len(P))):
                k = int(np.argmax(d))
                if d[k] <= 0:
                    break
                inner.append(tuple(P[k]))
                d = np.minimum(d, np.hypot(P[:, 0] - P[k, 0], P[:, 1] - P[k, 1]))
    # kiểm: điểm ảnh đục nằm ngoài viền mới, độ phình (diện tích lưới thêm so với cũ)
    fill = np.zeros((h, w), np.uint8)
    cv2.fillPoly(fill, [np.round(np.array(hull) * 4).astype(np.int32)], 1, shift=2)
    old = np.zeros((h, w), np.uint8)
    cv2.fillPoly(old, [np.round(hull0 * 4).astype(np.int32)], 1, shift=2)
    cut = int(((alpha > 8) & (fill == 0)).sum())
    # 2026-11-20: .sum() của mảng uint8 trả số KHÔNG DẤU (uint64 trên Linux / numpy 2): hiệu âm (lưới mới nhỏ hơn cũ) tràn thành
    # ~1e19 -> trang hiện "lưới phình 2e+17%". Ép int64 trước khi trừ; âm = lưới co lại.
    n_new, n_old = int(fill.sum(dtype=np.int64)), int(old.sum(dtype=np.int64))
    grow = float((n_new - n_old) / max(1, n_old) * 100)
    old_cut = int(((alpha > 8) & (old == 0)).sum())
    hull = [tuple(p) for p in hull]
    for _ in range(6):   # Delaunay sót cạnh viền ở chỗ lõm hẹp: chèn điểm giữa cạnh sót rồi chia lại (bài học GiftBox)
        tris, miss = triangulate(hull, inner, w, h)
        if not miss:
            break
        for i in sorted(miss, reverse=True):
            p, q = hull[i], hull[(i + 1) % len(hull)]
            hull.insert(i + 1, ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2))
    return {"hull": [[round(x, 2), round(y, 2)] for x, y in hull], "inner": [[round(x, 2), round(y, 2)] for x, y in inner],
            "w": w, "h": h, "cut_px": cut, "old_cut_px": old_cut, "grow_pct": round(grow, 2), "before": {"points": total0, "hull": len(hull0),
            "inner": len(inner0)}, "triangles": len(tris), "missing": miss}


def _trace_points(alpha, n):
    """Auto trace theo số điểm (người dùng 2026-10-31: "số point càng nhiều thì càng nhiều điểm cho mesh, autotrace như Spine
    ưu tiên bám sát layer nhất có thể mà không cắt khuyết layer"; "tăng nhiều điểm nhưng curve cong / góc chưa bám sát").
    1) Đơn giản hoá đường bao ảnh (nới 1 px) bằng DP thường: đủ số điểm viền, điểm đặt ở chỗ bám sát nhất.
    2) Đẩy từng cạnh ra ngoài vừa đủ bao trọn đoạn đường bao nó thay (+0.3 px); đỉnh mới = giao hai cạnh kề -> giữ góc nhọn,
       không cắt vào ảnh. 3) Cắt theo khung ảnh. Điểm còn lại rải đều bên trong (n >= 12, khoảng 25%)."""
    import cv2
    h, w = alpha.shape
    n = max(4, min(400, n))
    n_hull = n if n < 12 else max(8, round(n * 0.75))
    mask = (alpha > 8).astype(np.uint8)
    if not mask.any():
        raise ValueError("ảnh trong suốt hoàn toàn")
    m = cv2.dilate(np.pad(mask, 2), np.ones((3, 3), np.uint8))[2:-2, 2:-2]
    m = np.pad(m, 1)
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    C = max(cs, key=cv2.contourArea)[:, 0, :].astype(float) - 1 + 0.5
    C[:, 0] = C[:, 0].clip(0, w); C[:, 1] = C[:, 1].clip(0, h)
    C[C[:, 0] <= 0.5, 0] = 0; C[C[:, 0] >= w - 0.5, 0] = w
    C[C[:, 1] <= 0.5, 1] = 0; C[C[:, 1] >= h - 0.5, 1] = h
    N = len(C)
    area2 = float(np.sum(C[:, 0] * np.roll(C[:, 1], -1) - np.roll(C[:, 0], -1) * C[:, 1]))
    sign = 1.0 if area2 > 0 else -1.0

    lo, hi, K = 0.2, max(w, h), None
    for _ in range(30):   # sai số nhỏ nhất mà số điểm viền <= n_hull (bám sát nhất)
        mid = (lo + hi) / 2
        k = _dp_idx(C, mid)
        if len(k) <= n_hull:
            K, hi = k, mid
        else:
            lo = mid
    K = K or _dp_idx(C, hi)

    def build(extra):
        return _outward_hull(C, K, sign, extra, w, h)

    hull = None
    for extra in (0.3, 0.8, 1.5, 3.0, 6.0):   # kiểm: không điểm ảnh đục nào ngoài viền
        hull = build(extra)
        fill = np.zeros((h, w), np.uint8)
        cv2.fillPoly(fill, [np.round(np.array(hull) * 4).astype(np.int32)], 1, shift=2)
        cut = int(((mask > 0) & (fill == 0)).sum())
        if cut == 0:
            break
    inner = []
    rest = n - len(hull)
    if rest > 0 and n >= 12:
        hp = np.array(hull, np.float32)
        grid = lambda sp: [(float(x), float(y)) for y in np.arange(sp / 2, h, sp) for x in np.arange(sp / 2, w, sp)
                           if cv2.pointPolygonTest(hp, (float(x), float(y)), True) >= sp * 0.4]
        a, b, pick = 4.0, float(max(w, h)), []
        for _ in range(16):
            sp = (a + b) / 2
            pts = grid(sp)
            if not pick or abs(len(pts) - rest) < abs(len(pick) - rest):
                pick = pts
            if len(pts) > rest:
                a = sp
            else:
                b = sp
        inner = pick
    return {"hull": [[round(x, 2), round(y, 2)] for x, y in hull], "inner": [[round(x, 2), round(y, 2)] for x, y in inner],
            "w": w, "h": h, "cut_px": cut}


def triangulate(hull, inner, w, h):
    import cv2
    pts = [tuple(map(float, p)) for p in hull] + [tuple(map(float, p)) for p in inner]
    if len(hull) < 3:
        raise ValueError("viền cần ít nhất 3 điểm")
    hp = np.array(hull, np.float32)
    lo = np.min(np.array(pts), 0) - 20
    hi = np.max(np.array(pts), 0) + 20
    sub = cv2.Subdiv2D((int(lo[0]), int(lo[1]), int(hi[0] - lo[0]) + 2, int(hi[1] - lo[1]) + 2))
    for p in pts:
        sub.insert(p)
    tris = []
    for t in sub.getTriangleList():
        v = [min(range(len(pts)), key=lambda i: (pts[i][0] - t[j]) ** 2 + (pts[i][1] - t[j + 1]) ** 2) for j in (0, 2, 4)]
        if len(set(v)) < 3:
            continue
        P = [pts[j] for j in v]
        tests = [((P[0][0] + P[1][0] + P[2][0]) / 3, (P[0][1] + P[1][1] + P[2][1]) / 3)]
        tests += [((P[i][0] + P[(i + 1) % 3][0]) / 2, (P[i][1] + P[(i + 1) % 3][1]) / 2) for i in range(3)]
        if all(cv2.pointPolygonTest(hp, (float(x), float(y)), True) >= -0.5 for x, y in tests):
            tris.append(v)
    E = {tuple(sorted((t[i], t[(i + 1) % 3]))) for t in tris for i in range(3)}
    miss = [i for i in range(len(hull)) if tuple(sorted((i, (i + 1) % len(hull)))) not in E]
    return tris, miss


def tri_preview(b):
    tris, miss = triangulate(b.get("hull") or [], b.get("inner") or [], b.get("w", 0), b.get("h", 0))
    return {"triangles": tris, "missing": miss}


def apply_mesh(b, safe, backup, save):
    js = safe(b.get("json", ""))
    if not js or not os.path.isfile(js):
        raise ValueError("không thấy file")
    data = json.load(open(js, encoding="utf8"))
    slot_name, att_name = b["slot"], b["attachment"]
    slot = next((s for s in data.get("slots", []) if s["name"] == slot_name), None)
    if not slot:
        raise ValueError("không có slot " + slot_name)
    skin, a = find_attachment(data, slot_name, att_name)
    hull = [tuple(map(float, p)) for p in b.get("hull") or []]
    inner = [tuple(map(float, p)) for p in b.get("inner") or []]
    tris, miss = triangulate(hull, inner, 0, 0)
    if not tris:
        raise ValueError("không chia được tam giác (viền tự cắt nhau?)")
    W = setup_world(data)
    bone_names = [x["name"] for x in data["bones"]]
    bidx = {n: i for i, n in enumerate(bone_names)}
    sb = slot["bone"]
    pts = hull + inner
    if a.get("type") == "mesh":
        w, h = a["width"], a["height"]
        opx, oworld, owt, otris = old_mesh(a, sb, W, bone_names)
        to_world = affine_fit(opx, oworld)
        weighted = len(a["vertices"]) != len(a["uvs"])
    elif a.get("type", "region") == "region":
        from spine_live import images_dir
        w, h = a.get("width"), a.get("height")
        if not w or not h:
            from PIL import Image
            w, h = Image.open(image_path(js, data, att_name, a)).size
        to_world = region_px_to_world(dict(a, width=w, height=h), sb, W)
        weighted, opx, owt, otris = False, None, None, None
    else:
        raise ValueError("chỉ sửa được region / mesh, không phải " + a.get("type"))
    uvs, verts = [], []
    per = None
    if weighted:   # 2026-11-18: giữ xương đang bind mà 0 % (bind thêm chưa sơn) khi đổi lưới, trước đây rơi khỏi danh sách
        per = [{k: v for k, v in interp_weights(p, opx, owt, otris).items() if v >= 0.01} for p in pts]
        had = sorted({n for wd in owt for n in wd})
        per = _anchor_zero(per, [to_world(*p) for p in pts], W, had)
    for pi_, p in enumerate(pts):
        uvs += [round(p[0] / w, 6), round(p[1] / h, 6)]
        wx, wy = to_world(*p)
        if weighted:
            wd = per[pi_]
            tot = sum(wd.values()) or 1
            verts.append(len(wd))
            for name, ww in sorted(wd.items(), key=lambda kv: -kv[1]):
                lx, ly = apply_m(inv_m(W[name]), wx, wy)
                verts += [bidx[name], round(lx, 3), round(ly, 3), round(ww / tot, 4)]
        else:
            lx, ly = apply_m(inv_m(W[sb]), wx, wy)
            verts += [round(lx, 3), round(ly, 3)]
    edges = []
    for i in range(len(hull)):
        edges += [i * 2, ((i + 1) % len(hull)) * 2]
    new = {"type": "mesh", "uvs": uvs, "triangles": [i for t in tris for i in t], "vertices": verts,
           "hull": len(hull), "edges": edges, "width": w, "height": h}
    for k in ("path", "color"):
        if k in a:
            new[k] = a[k]
    skin["attachments"][slot_name][att_name] = new
    # deform timeline của attachment này không còn khớp số đỉnh: bỏ
    dropped = 0
    for an in (data.get("animations") or {}).values():
        for sk_name, slots in list((an.get("attachments") or {}).items()):
            atts = (slots.get(slot_name) or {})
            if att_name in atts and "deform" in atts[att_name]:
                atts[att_name].pop("deform"); dropped += 1
        dfm = an.get("deform") or {}
        for sk_name, slots in dfm.items():
            if att_name in (slots.get(slot_name) or {}):
                slots[slot_name].pop(att_name); dropped += 1
    backup(js)
    save(js, data)
    return {"vertices": len(pts), "triangles": len(tris), "hull": len(hull), "weighted": weighted,
            "missingHullEdges": miss, "droppedDeform": dropped}
