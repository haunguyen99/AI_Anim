"""Điều khiển Studio đang mở (Chrome hay trình duyệt trong app) qua server Home — không cần chụp màn hình hay trình duyệt của Claude.

  python tools/studio_cmd.py state                         # nhân vật, workspace, mesh (ẩn/hiện, skin), joint đang chọn, pose
  python tools/studio_cmd.py vis EN_Boss_Gragas1 off       # on | off | toggle ; tên "*" = mọi mesh
  python tools/studio_cmd.py select joint Shoulder_L       # select mesh <tên> | select joint <tên> | select none
  python tools/studio_cmd.py joint Shoulder_L --r 0,0,-30  # xoay thêm (độ) quanh joint; --t x,y,z (cm, tuyệt đối); --s
  python tools/studio_cmd.py bindpose
  python tools/studio_cmd.py ws general | run <id lệnh> | open <nhân vật> [ws] | clients
  python tools/studio_cmd.py focus rig                     # mesh | rig | pose: module đang sửa (chuột, gizmo, Channel Box, phím)
  python tools/studio_cmd.py layer anim on [--both]        # scene (nhân vật; rig là chế độ sửa của nó) | anim; on | off | toggle; --both = không ẩn lớp khác
  python tools/studio_cmd.py cmds [chữ cần tìm]            # mọi lệnh: id, nhãn, module, phím, dùng được ngay không
Workspace chỉ là bố cục: lệnh nào cũng chạy được ở workspace nào (run tự focus sang module của lệnh).

  Chung:  undo | redo | save | view [1|4] [persp|top|front|side] [all|sel] | snap [file.png] [WxH]   (ảnh viewport để AI tự kiểm)
  Rig:    rig lms | rig lm Elbow_R x,y,z | rig sel Elbow_R Wrist_R | rig step 4 (1–5; 6 = panel Vật lý)
  Anim:   anim clips | anim clip gaygor_walk (đổi anim: trang tải lại) | anim info | anim joints | anim read [khớp…] | anim select khớp… | anim frame 12 | anim play on|off
          anim rot Chest_M 0,0,15 [--abs]     # xoay thêm quanh trục local (độ); --abs: góc local XYZ tuyệt đối
          anim pos Root_M 0,0,-5              # dời thêm (cm, trục Blender, Z lên); hông / cổ chân / cổ tay theo IK
          anim key [f] | anim unkey [f] | anim versions | anim version v3
  Cổng duyệt Rig (nút Duyệt / Cần sửa): gate-done <chữ trong tên kho> <bước> ["việc đã làm"]   # trang hiện "AI đã xong"
  Ghi chú vẽ (nút ✎ trong viewport): notes [chữ trong tên kho] [--all] [--out DIR]   # in ghi chú đang mở + ghi ảnh (đọc thẳng work/store/*_studio)
          note-done <id> [--open]                                                    # đánh dấu đã sửa (hoặc mở lại)
  Rig / anim tự focus, bật lớp và chờ lõi nạp (lần đầu vài giây). Sửa khớp ở bản dạng key thì Auto key đặt key luôn.
Chỉ có các lệnh có tên (không chạy mã tuỳ ý trong trang).
Nhiều lệnh một lần (nhanh hơn: Python chỉ khởi động một lần):  studio_cmd.py vis A off ";" select joint B ";" state
Thêm --time để in thời gian khứ hồi; --cid <id> để gửi tới đúng một trang (studio_cmd.py clients liệt kê) khi đang mở nhiều trang Studio. Cổng: HOME_PORT (mặc định 8780). Server: tools/home/studio_bridge.py; trang: tools/studio/modules/bridge.js.
"""
import json
import os
import sys
import time
import urllib.request

BASE = f"http://127.0.0.1:{os.environ.get('HOME_PORT', '8780')}"


CID = None   # --cid <id>: gửi tới đúng trang này (xem "clients"), không thì tới trang đang hiện gần nhất


def call(op, args=None, timeout=10):
    body = json.dumps({"op": op, "args": args or {}, "timeout": timeout, **({"cid": CID} if CID else {})}).encode()
    req = urllib.request.Request(BASE + "/api/studio/cmd", body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout + 5) as r:
        return json.loads(r.read())


def vec(s):
    return [float(x) for x in s.split(",")]


def strokes_world(d, img):
    """Khung trực giao (front / side / top): mỗi nét → điểm đầu, cuối, tâm (cm, trục Studio: x phải nhân vật âm, y lên, z trước).
    Khung phối cảnh: không đổi được (thiếu độ sâu), trả None."""
    v = (d.get("ctx") or {}).get("view") or {}
    if v.get("pane") not in ("front", "side", "top") or not d.get("strokes"): return None
    asp = v.get("aspect")
    if not asp and img:
        try:
            from PIL import Image
            w, h = Image.open(img).size; asp = w / h
        except Exception: return None
    x, y, z, w = v["quat"]
    right = (1 - 2 * (y * y + z * z), 2 * (x * y + z * w), 2 * (x * z - y * w)); up = (2 * (x * y - z * w), 1 - 2 * (x * x + z * z), 2 * (y * z + x * w))
    zh = 2 / (v.get("zoom") or 1); zw = zh * asp; t = v["target"]
    P = lambda p: [round((t[k] + right[k] * (p[0] - 0.5) * zw + up[k] * (0.5 - p[1]) * zh) * 100, 1) for k in range(3)]
    out = []
    for s in d["strokes"]:
        pts = s.get("pts") or []
        if not pts: continue
        c = [sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)]
        out.append({"color": s.get("c"), "n": len(pts), "start": P(pts[0]), "end": P(pts[-1]), "center": P(c)})
    return out


def notes_cmd(op, rest):
    """Ghi chú vẽ lưu ở work/store/<nhân vật>_studio/notes/<id>.json (+ noteimg/<id>.json: ảnh JPEG data URL)."""
    import base64, glob, tempfile
    store = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "work", "store")
    docs = []
    for f in glob.glob(os.path.join(store, "*_studio", "notes", "*.json")) + glob.glob(os.path.join(store, "*_notes", "notes", "*.json")):
        d = json.load(open(f, encoding="utf8")); d = d.get("data", d) if isinstance(d, dict) and "data" in d and isinstance(d["data"], dict) else d
        docs.append((f, d))
    if op == "note-done":
        nid = rest[0]; hit = [x for x in docs if x[1].get("id") == nid]
        if not hit: print(json.dumps({"ok": False, "error": "không có ghi chú " + nid}, ensure_ascii=False)); return 1
        f, d = hit[0]; d["status"] = "open" if "--open" in rest else "done"
        raw = json.load(open(f, encoding="utf8")); (raw["data"] if "data" in raw and isinstance(raw["data"], dict) else raw).update(d)
        json.dump(raw, open(f, "w", encoding="utf8"), ensure_ascii=False); print(json.dumps({"ok": True, "id": nid, "status": d["status"]}, ensure_ascii=False)); return 0
    out = rest[rest.index("--out") + 1] if "--out" in rest else os.path.join(tempfile.gettempdir(), "studio_notes")
    flt = next((x for x in rest if not x.startswith("--") and x != out), "")
    os.makedirs(out, exist_ok=True); res = []
    for f, d in sorted(docs, key=lambda x: x[1].get("at", "")):
        ns = os.path.basename(os.path.dirname(os.path.dirname(f)))
        if flt and flt.lower() not in ns.lower(): continue
        if d.get("status") == "done" and "--all" not in rest: continue
        img = os.path.join(os.path.dirname(os.path.dirname(f)), "noteimg", os.path.basename(f)); path = None
        if os.path.isfile(img):
            j = json.load(open(img, encoding="utf8")); j = j.get("data", j); u = j.get("img", "")
            if u.startswith("data:"):
                path = os.path.join(out, ns + "_" + d["id"] + ".jpg"); open(path, "wb").write(base64.b64decode(u.split(",", 1)[1]))
        res.append({"ns": ns, "id": d.get("id"), "at": d.get("at"), "status": d.get("status"), "sent": d.get("sent"), "text": d.get("text"), "ctx": d.get("ctx"),
                    "strokes": len(d.get("strokes") or []), "strokes_cm": strokes_world(d, path), "image": path})
    print(json.dumps({"ok": True, "result": res}, ensure_ascii=False, indent=1)); return 0


def gate_done(rest):
    """gate-done <chữ trong tên kho rig> <bước> ["việc đã làm"]: ghi done cho cổng duyệt Rig, trang hiện "AI đã xong"."""
    import glob
    store = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "work", "store")
    flt, n, msg = rest[0].lower(), str(int(rest[1])), (rest[2] if len(rest) > 2 else "")
    fs = [f for f in glob.glob(os.path.join(store, "*_rig_lab", "rig", "gates.json")) if flt in f.lower()]
    if len(fs) != 1:
        print(json.dumps({"ok": False, "error": "khớp %d kho rig" % len(fs), "files": fs}, ensure_ascii=False)); return 1
    raw = json.load(open(fs[0], encoding="utf8")); d = raw["data"] if isinstance(raw.get("data"), dict) else raw
    g = (d.get("g") or {}).get(n)
    if not isinstance(g, dict):
        print(json.dumps({"ok": False, "error": "bước %s chưa có cổng" % n}, ensure_ascii=False)); return 1
    g["done"] = time.strftime("%Y-%m-%dT%H:%M:%S"); g["doneMsg"] = msg
    json.dump(raw, open(fs[0], "w", encoding="utf8"), ensure_ascii=False)
    print(json.dumps({"ok": True, "step": int(n), "status": g.get("status")}, ensure_ascii=False)); return 0


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if ";" in argv:   # nhiều lệnh một lần chạy: studio_cmd.py vis A off ; joint B --r 0,0,30 ; state
        groups, cur = [], []
        for a in argv + [";"]:
            if a == ";":
                if cur:
                    groups.append(cur)
                cur = []
            else:
                cur.append(a)
        return max(main(g) for g in groups)
    global CID
    show_time = "--time" in argv
    if "--cid" in argv:
        i = argv.index("--cid"); CID = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    argv = [a for a in argv if a != "--time"]
    if not argv:
        print(__doc__)
        return 2
    op, rest = argv[0].lower(), argv[1:]
    t0 = time.perf_counter()
    if op in ("notes", "note-done"):
        return notes_cmd(op, rest)
    if op == "gate-done":
        return gate_done(rest)
    if op == "clients":
        with urllib.request.urlopen(BASE + "/api/studio/clients", timeout=5) as r:
            res = {"ok": True, "result": json.loads(r.read())}
    elif op == "vis":
        on = {"on": True, "off": False, "toggle": "toggle"}[(rest[1] if len(rest) > 1 else "toggle").lower()]
        res = call("vis", {"name": rest[0], "on": on})
    elif op == "select":
        kind, name = (rest + ["none", None])[:2]
        res = call("select", {"joint": name} if kind == "joint" else {"mesh": None if kind == "none" else name})
    elif op == "joint":
        a, i = {"name": rest[0]}, 1
        while i < len(rest):
            a[rest[i].lstrip("-")] = vec(rest[i + 1]); i += 2
        res = call("joint", a)
    elif op == "bindpose":
        res = call("bindPose")
    elif op == "ws":
        res = call("ws", {"id": rest[0]})
    elif op == "run":
        res = call("run", {"id": rest[0]})
    elif op == "focus":
        res = call("focus", {"id": rest[0]})
    elif op == "layer":
        on = {"on": True, "off": False, "toggle": "toggle"}[(rest[1] if len(rest) > 1 else "toggle").lower()]
        res = call("layer", {"id": rest[0], "on": on, "solo": "--both" not in rest})
    elif op in ("undo", "redo", "save"):
        res = call(op)
    elif op == "view":
        a = {}
        for x in rest:
            if x in ("1", "4"): a["layout"] = x
            elif x in ("persp", "top", "front", "side"): a["cam"] = x
            elif x in ("all", "sel"): a["frame"] = x
        res = call("view", a)
    elif op == "snap":
        size = next((x for x in rest if "x" in x and x.replace("x", "").isdigit()), None)   # snap [file] [2400x2400]
        rest = [x for x in rest if x != size]
        res = call("snap", dict(zip(("w", "h"), map(int, size.split("x")))) if size else {}, timeout=30)
        if res.get("ok"):
            import base64, tempfile
            out = rest[0] if rest else os.path.join(tempfile.gettempdir(), "studio_snap_%d.png" % int(time.time()))
            open(out, "wb").write(base64.b64decode(res["result"].pop("png")))
            res["result"]["file"] = os.path.abspath(out)
    elif op == "rig":
        d, a = (rest[0] if rest else "lms"), {}
        if d == "lm": a = {"name": rest[1], "xyz": vec(rest[2])}
        elif d == "sel": a = {"names": rest[1:]}
        elif d == "step": a = {"n": int(rest[1])}
        res = call("rig", dict(a, do=d), timeout=90)
    elif op == "anim":
        d, r, a = (rest[0] if rest else "info"), rest[1:], {}
        if d in ("read", "select"): a = {"names": r}
        elif d == "rot": a = {"name": r[0], "r": vec(r[1]), "abs": "--abs" in r}
        elif d == "pos": a = {"name": r[0], "t": vec(r[1])}
        elif d == "frame": a = {"f": int(r[0])}
        elif d == "play": a = {"on": (r[0] if r else "on").lower() != "off"}
        elif d in ("key", "unkey") and r: a = {"f": int(r[0])}
        elif d == "version": a = {"v": r[0]}
        elif d == "clip": a = {"id": r[0]}
        res = call("anim", dict(a, do=d), timeout=90)
    elif op == "cmds":
        res = call("cmds", {"q": " ".join(rest)})
    elif op == "open":
        res = call("open", {"char": rest[0], "ws": rest[1] if len(rest) > 1 else None})
    else:
        res = call(op, json.loads(rest[0]) if rest else {})
    if show_time:
        res["roundtrip_ms"] = round((time.perf_counter() - t0) * 1000, 1)
    print(json.dumps(res, ensure_ascii=False))
    return 0 if res.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
