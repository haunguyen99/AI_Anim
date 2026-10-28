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

  Chung:  undo | redo | save | view [1|4] [persp|top|front|side] [all|sel] | snap [file.png]   (ảnh viewport để AI tự kiểm)
  Rig:    rig lms | rig lm Elbow_R x,y,z | rig sel Elbow_R Wrist_R | rig step 4
  Anim:   anim info | anim joints | anim read [khớp…] | anim select khớp… | anim frame 12 | anim play on|off
          anim rot Chest_M 0,0,15 [--abs]     # xoay thêm quanh trục local (độ); --abs: góc local XYZ tuyệt đối
          anim pos Root_M 0,0,-5              # dời thêm (cm, trục Blender, Z lên); hông / cổ chân / cổ tay theo IK
          anim key [f] | anim unkey [f] | anim versions | anim version v3
  Rig / anim tự focus, bật lớp và chờ lõi nạp (lần đầu vài giây). Sửa khớp ở bản dạng key thì Auto key đặt key luôn.
Chỉ có các lệnh có tên (không chạy mã tuỳ ý trong trang).
Nhiều lệnh một lần (nhanh hơn: Python chỉ khởi động một lần):  studio_cmd.py vis A off ";" select joint B ";" state
Thêm --time để in thời gian khứ hồi. Cổng: HOME_PORT (mặc định 8780). Server: tools/home/studio_bridge.py; trang: tools/studio/modules/bridge.js.
"""
import json
import os
import sys
import time
import urllib.request

BASE = f"http://127.0.0.1:{os.environ.get('HOME_PORT', '8780')}"


def call(op, args=None, timeout=10):
    body = json.dumps({"op": op, "args": args or {}, "timeout": timeout}).encode()
    req = urllib.request.Request(BASE + "/api/studio/cmd", body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout + 5) as r:
        return json.loads(r.read())


def vec(s):
    return [float(x) for x in s.split(",")]


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
    show_time = "--time" in argv
    argv = [a for a in argv if a != "--time"]
    if not argv:
        print(__doc__)
        return 2
    op, rest = argv[0].lower(), argv[1:]
    t0 = time.perf_counter()
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
        res = call("snap", timeout=20)
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
