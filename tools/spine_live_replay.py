"""Dựng lại một skeleton Spine theo từng bước trên Spine Live để người dùng xem quá trình (chế độ Theo Claude).

  python tools/spine_live_replay.py work/<game>/spine/<anim>/<x>.json [--anim tap] [--delay 2.5] [--ui Equipment] [--only rig|anim]

Các bước (mỗi bước ghi đè <anim>/_live/<x>_dung.json, trang tự nạp lại, kèm chú thích):
  1. ảnh: mesh không weight gắn vào root
  2. thêm từng xương (bật lớp Xương)
  3. phủ lưới mesh (bật Lưới mesh)
  4. weight: gắn mesh vào xương, tô weight từng xương
  5. blocking: thêm dần từng key của anim (stepped), dừng ở frame của key đó
  6. spline: anim hoàn chỉnh, chạy
Không sửa file gốc. Người dùng 2026-10-28: muốn "xem quá trình dựng" trên Spine Live.
"""
import copy, json, math, os, subprocess, sys, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
FPS = 30


def opt(args, name, default=None):
    if name in args:
        i = args.index(name)
        v = args[i + 1]
        del args[i:i + 2]
        return v
    return default


def local_mat(b):
    r = math.radians(b.get("rotation", 0.0))
    sx, sy = b.get("scaleX", 1.0), b.get("scaleY", 1.0)
    return (math.cos(r) * sx, -math.sin(r) * sy, math.sin(r) * sx, math.cos(r) * sy, b.get("x", 0.0), b.get("y", 0.0))


def mul(p, l):
    a, b, c, d, x, y = p
    la, lb, lc, ld, lx, ly = l
    return (a * la + b * lc, a * lb + b * ld, c * la + d * lc, c * lb + d * ld, a * lx + b * ly + x, c * lx + d * ly + y)


def apply(m, px, py):
    return (m[0] * px + m[1] * py + m[4], m[2] * px + m[3] * py + m[5])


def setup_world(bones):
    W = {}
    for b in bones:
        lm = local_mat(b)
        W[b["name"]] = mul(W[b["parent"]], lm) if b.get("parent") else lm
    return W


def unweighted_on_root(att, slot_bone, bones):
    """Mesh có weight -> mesh không weight, tọa độ tính từ root ở setup pose."""
    W = setup_world(bones)
    names = [b["name"] for b in bones]
    v, out = att["vertices"], []
    n = len(att["uvs"]) // 2
    if len(v) == n * 2:   # vốn không weight: đổi từ không gian xương của slot sang root
        for i in range(n):
            out += list(apply(W[slot_bone], v[2 * i], v[2 * i + 1]))
    else:
        k = 0
        for _ in range(n):
            cnt = int(v[k]); k += 1
            x = y = 0.0
            for _ in range(cnt):
                bi, bx, by, w = int(v[k]), v[k + 1], v[k + 2], v[k + 3]; k += 4
                wx, wy = apply(W[names[bi]], bx, by)
                x += wx * w; y += wy * w
            out += [x, y]
    a = dict(att)
    a["vertices"] = [round(t, 3) for t in out]
    return a


def weighted_bones(att, bones):
    v, used, k = att["vertices"], [], 0
    n = len(att["uvs"]) // 2
    if len(v) == n * 2:
        return used
    for _ in range(n):
        cnt = int(v[k]); k += 1
        for _ in range(cnt):
            bi = int(v[k])
            if bones[bi]["name"] not in used:
                used.append(bones[bi]["name"])
            k += 4
    return [b["name"] for b in bones if b["name"] in used]


def main(argv):
    args = list(argv)
    if not args:
        print(__doc__)
        return 1
    anim = opt(args, "--anim")
    delay = float(opt(args, "--delay", "2.5"))
    ui = opt(args, "--ui")
    only = opt(args, "--only")
    src = args[0].replace("\\", "/")
    full = os.path.join(ROOT, src)
    d = json.load(open(full, encoding="utf8"))
    base = os.path.splitext(os.path.basename(src))[0]
    live_dir = os.path.join(os.path.dirname(full), "_live")
    os.makedirs(live_dir, exist_ok=True)
    out = os.path.join(live_dir, base + "_dung.json")
    out_rel = os.path.relpath(out, ROOT).replace("\\", "/")
    anim = anim or next(iter(d.get("animations", {})), None)
    bones = d["bones"]
    sk = dict(d["skeleton"]); sk["images"] = "../" + sk.get("images", "./images/").lstrip("./")
    step = [0]
    n_steps = [0]

    def push(data, say, frame=None, play=False, **view):
        step[0] += 1
        tmp = out + ".tmp"
        json.dump(data, open(tmp, "w", encoding="utf8"))
        os.replace(tmp, out)
        cmd = [sys.executable, "-I", os.path.join(ROOT, "tools", "spine_live_cmd.py"), "show", out_rel,
               "--say", f"Bước {step[0]}/{n_steps[0]}: {say}"]
        if data.get("animations"):
            cmd += ["--anim", next(iter(data["animations"]))]
        cmd += ["--play"] if play or frame is None else ["--frame", str(frame)]
        for k, val in view.items():
            if isinstance(val, bool):
                cmd.append(("--" if val else "--no-") + k)
            else:
                cmd += ["--" + k, val]
        if ui is not None and step[0] == 1:
            cmd += ["--ui", ui]
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"bước {step[0]}: {say}")
        time.sleep(delay)

    def skel(bs, slots, skins, anims=None):
        names = {b["name"] for b in bs}
        sl = [s for s in slots if s["bone"] in names]
        keep = {s["name"] for s in sl}
        sks = [dict(k, attachments={n: a for n, a in k["attachments"].items() if n in keep}) for k in skins]
        return {"skeleton": sk, "bones": copy.deepcopy(bs), "slots": sl,
                "skins": sks, "animations": anims or {}, "events": d.get("events", {})}

    # mesh không weight, gắn root (cho các bước trước khi có weight)
    root = bones[0]["name"]
    slot_bone = {s["name"]: s["bone"] for s in d["slots"]}
    skin0 = copy.deepcopy(d["skins"])
    meshes = []
    for sk_ in skin0:
        for slot, atts in sk_["attachments"].items():
            for name, a in list(atts.items()):
                if a.get("type") == "mesh":
                    atts[name] = unweighted_on_root(a, slot_bone[slot], bones)
                    meshes.append((slot, name, a))
    slots_root = [dict(s, bone=root) if any(m[0] == s["name"] for m in meshes) else s for s in d["slots"]]
    main_mesh = meshes[0] if meshes else None
    w_bones = weighted_bones(main_mesh[2], bones) if main_mesh else []

    keys = []
    if anim and only != "rig":
        A = d["animations"][anim]
        times = set()
        for tls in list(A.get("bones", {}).values()) + list(A.get("slots", {}).values()):
            for tl in tls.values():
                for k in tl:
                    times.add(round(k.get("time", 0.0), 4))
        keys = sorted(times)
    rig = only != "anim"
    n_steps[0] = (len(bones) + (1 if main_mesh else 0) + len(w_bones) + (0 if keys else 1) if rig else 0) + (len(keys) + 1 if keys else 0)

    if rig:
        push(skel(bones[:1], slots_root, skin0), "đặt ảnh lên gốc skeleton (dấu + đỏ = điểm chạm)", bones=True, mesh=False, weight="")
        for i in range(1, len(bones)):
            b = bones[i]
            what = f"thêm xương {b['name']}" + (f" (con của {b['parent']})" if b.get("parent") else "")
            if b.get("length"):
                what += f", dài {b['length']:.0f}"
            if b.get("rotation"):
                what += f", xoay {b['rotation']:.0f}°"
            push(skel(bones[:i + 1], slots_root, skin0), what, bones=True)
        if main_mesh:
            a = main_mesh[2]
            push(skel(bones, slots_root, skin0),
                 f"phủ lưới mesh lên ảnh {main_mesh[1]}: {len(a['uvs']) // 2} đỉnh, {len(a['triangles']) // 3} tam giác, viền cam = hull",
                 mesh=True)
            for bn in w_bones:
                push(skel(bones, d["slots"], d["skins"]), f"weight {bn}: đỏ = đi theo {bn} hoàn toàn, xanh = không theo",
                     mesh=False, weight=bn)
        if not keys:   # kết phần rig: tắt lớp tô weight / lưới, không thì trang giữ tô màu sau khi replay xong
            push(skel(bones, d["slots"], d["skins"], {anim: d["animations"][anim]} if anim else None),
                 "rig hoàn chỉnh", play=bool(anim), bones=True, mesh=False, weight="")
    if keys:
        A = d["animations"][anim]
        for ki, t in enumerate(keys):
            part = copy.deepcopy(A)
            for group in ("bones", "slots"):
                for tls in part.get(group, {}).values():
                    for tlname in list(tls):
                        ks = [k for k in tls[tlname] if round(k.get("time", 0.0), 4) <= t]
                        for k in ks:
                            k["curve"] = "stepped"
                        if ks:
                            tls[tlname] = ks
                        else:
                            del tls[tlname]
            part.pop("events", None)
            fr = round(t * FPS)
            moved = sorted({bn for bn, tls in A.get("bones", {}).items() for tl in tls.values()
                            for k in tl if round(k.get("time", 0.0), 4) == t})
            push(skel(bones, d["slots"], d["skins"], {anim: part}),
                 f"blocking key F{fr}: " + (", ".join(moved) if moved else "slot") + " (stepped, chưa nội suy)",
                 frame=fr, bones=True, weight="")
        push(skel(bones, d["slots"], d["skins"], {anim: A}), f"spline: nội suy giữa các key, anim {anim} hoàn chỉnh",
             play=True, bones=False)
    print("xong:", out_rel)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
