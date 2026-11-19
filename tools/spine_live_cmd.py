"""Cho người dùng thấy Claude đang làm gì trên Spine Live (Home /spine, chế độ "Theo Claude").

  python tools/spine_live_cmd.py show <json> [--anim tap] [--frame 8 | --play] [--bones] [--mesh] [--weight wrist] [--ui Equipment|""] [--say "..."]
  python tools/spine_live_cmd.py say "Đang bẻ thử cổ tay ±25° để kiểm mesh"
  python tools/spine_live_cmd.py status          # trang Spine Live nào đang mở, có đang Theo Claude không
  python tools/spine_live_cmd.py clear           # xoá nhật ký bước
  python tools/spine_live_cmd.py notes [--all] [--json <rel>] [--bones]   # ghi chú + pose người dùng gửi từ chế độ Sửa;
        góp ý vẽ (nút ✎ Vẽ góp ý trên khung xem): in từng nét (toạ độ skeleton, xương gần nhất, layer) + đường dẫn ảnh khung xem kèm nét
  python tools/spine_live_cmd.py note-done <id>... | --all                 # đánh dấu đã xử lý
  python tools/spine_live_cmd.py wait [--timeout s]   # chạy nền: thoát (in ghi chú) khi người dùng gửi ghi chú / bấm Gen tiếp

Cầu nối lệnh (trang Spine Live phải đang mở; chạy bằng runtime Spine thật, đúng inherit / IK / mesh; tools/home/spine_bridge.py + tools/spine_live/bridge.js):
  python tools/spine_live_cmd.py pose <json> --anim A [--frames 0,20] [--bones head,arm_R]   # góc / vị trí thế giới + local
  python tools/spine_live_cmd.py measure <json> --anim A [--from idle] [--attach arm_L2:basket_ctrl] [--slots eye_L] [--rot ear_L2,towel_L2] [--top 8]
        # loop (F0 vs Fcuối), nối với anim --from (vị trí + vận tốc đầu / cuối), xương giật nhất, vật bám trôi, ảnh slot theo frame, biên độ góc
  python tools/spine_live_cmd.py snap <json> --anim A --frames 0,10,20 [--out x.png] [--cell 360x420] [--cols 4] [--bones]
        [--nolabel] [--box x0,y0,x1,y1]   # bỏ dải nhãn; khung cố định (video: tools/spine/live_video.py)
        # contact sheet vẽ bằng runtime thật (thay render_spine.py khi rig có inherit / IK / clipping); mặc định <thư mục anim>/_live/snap.png
        # [--trial tên]: ảnh thuộc lần thử tools/spine/trial.py (tự nhận nếu <json> là bản sao / file gốc của lần thử đang mở) -> xoá khi done

<json>: đường dẫn tính từ gốc dự án (work/<game>/spine/<anim>/x.json). Bản thử tạm: tạo bằng tools/spine/trial.py new (lưu kết quả vào trials.md, tự xoá bản thử + ảnh + kho Hoàn tác khi done)
(trang liệt kê thư mục này, ảnh lấy từ ../images). Mỗi lần ghi file JSON thì trang tự nạp lại, không cần gọi lệnh.
Không gửi gì tới trình duyệt: lệnh chỉ ghi work/store/_sys/spine_live/focus.json, trang hỏi server mỗi 0.5 s.
--bones / --mesh / --weight chỉ bật trên trang khi có cờ; không có cờ thì giữ nguyên lựa chọn của người dùng
(--no-bones / --no-mesh / --weight "" để tắt).
"""
import json, os, sys, time, urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
FOCUS = os.path.join(ROOT, "work", "store", "_sys", "spine_live", "focus.json")
BASE = f"http://127.0.0.1:{os.environ.get('SPINE_PORT', '8781')}"   # server Spine Live riêng (tools/spine_live/server.py)
KEEP_LOG = 30
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def load():
    try:
        return json.load(open(FOCUS, encoding="utf8"))
    except (OSError, ValueError):
        return {"seq": 0, "log": []}


def save(f):
    os.makedirs(os.path.dirname(FOCUS), exist_ok=True)
    tmp = FOCUS + ".tmp"
    with open(tmp, "w", encoding="utf8") as fh:
        json.dump(f, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, FOCUS)


def opt(args, name, default=None):
    if name in args:
        i = args.index(name)
        v = args[i + 1] if i + 1 < len(args) else ""
        del args[i:i + 2]
        return v
    return default


def flag(args, name):
    if name in args:
        args.remove(name)
        return True
    return False


NOTES = os.path.join(ROOT, "work", "store", "_sys", "spine_live", "notes.json")


GEN_GROUP = os.path.join(ROOT, "work", "store", "_sys", "spine_live", "gen_group.json")
GEN_GROUP_MAX_S = 45 * 60          # nhóm gen tự hết hạn (quên gen-start thì lượt sau không bị gộp nhầm quá lâu)


def gen_start(label=""):
    """mở nhóm gen mới (đầu mỗi lượt yêu cầu của người dùng): mọi lần Claude ghi file trong nhóm = MỘT phiên bản."""
    g = {"id": str(time.time_ns()), "label": label, "t": time.time()}
    os.makedirs(os.path.dirname(GEN_GROUP), exist_ok=True)
    with open(GEN_GROUP, "w", encoding="utf8") as fh:
        json.dump(g, fh, ensure_ascii=False)
    return g


def gen_group():
    try:
        g = json.load(open(GEN_GROUP, encoding="utf8"))
        return g["id"] if time.time() - g.get("t", 0) < GEN_GROUP_MAX_S else None
    except (OSError, ValueError, KeyError):
        return None


def claude_backup(path, what):
    """Claude sắp ghi đè file (gen lại anim bằng script): cất bản hiện tại vào lịch sử Hoàn tác của Spine Live
    (who = claude), để nút Hoàn tác trên trang lùi đúng lần gen này. In sổ keypose của file để soát: mọi keypose
    người dùng còn trong sổ phải có trong bản gen (script dựng lại cả anim, key không đưa vào script sẽ mất)."""
    if os.environ.get("SPINE_LIVE_NO_BACKUP"):   # server chạy lại script từ bảng Tham số: đã tự cất một bản trước
        return None
    sys.path.insert(0, os.path.join(ROOT, "tools", "home"))
    import spine_live as SL
    if not os.path.isfile(path):
        return None
    name = SL.backup(path, "claude", what, extra={"group": gen_group()})
    js_rel = SL.rel(path)
    kd = (SL._load_keyed().get(js_rel) or {})
    for anim, lst in kd.items():
        if lst:
            print(f"  [Spine Live] keypose người dùng trong sổ ({anim}): " +
                  ", ".join(f"F{e['frame']} ({len(e['bones'])} xương, {e['t'][11:16]})" for e in lst))
    return name


def keyed_values(js, anim, frames):
    """giá trị key (so với setup) của mọi kênh có key đúng tại từng frame, đọc từ file JSON."""
    try:
        d = json.load(open(os.path.join(ROOT, js), encoding="utf8"))
    except (OSError, ValueError):
        return {}
    fps = (d.get("skeleton") or {}).get("fps") or 30
    bt = ((d.get("animations") or {}).get(anim) or {}).get("bones") or {}
    out = {}
    for f in frames:
        rows = []
        for bn, tls in bt.items():
            for ch, ks in tls.items():
                k = next((k for k in ks if abs(k.get("time", 0) * fps - f) < 0.01), None)
                if k:
                    v = {kk: vv for kk, vv in k.items() if kk not in ("time", "curve")}
                    rows.append(f"{bn}.{ch} {v}")
        out[f] = rows
    return out


def consume(js_rel, anim, frames):
    """gen xong: các keypose đã dùng (frames) đặt used=true (trang ẩn) và ghi vào lần ghi gần nhất của Claude trong lịch sử
    Hoàn tác của file (consumed), để Hoàn tác bản gen đó thì keypose hiện lại."""
    sys.path.insert(0, os.path.join(ROOT, "tools", "home"))
    import spine_live as SL
    items = [{"anim": anim, "frame": int(f)} for f in frames]
    SL.set_used(js_rel, items, True)
    base = SL._backup_name(js_rel)
    log = SL._load_log(SL.BACKUP, base)
    last = next((e for e in reversed(log) if e.get("who") == "claude"), None)
    if last is not None:
        last["consumed"] = (last.get("consumed") or []) + items
        SL._save_json(SL._log_path(SL.BACKUP, base), log)
    print(f"  keypose đã dùng để gen ({anim}): " + ", ".join(f"F{f}" for f in frames) + " -> ẩn khỏi danh sách")


def notes_cmd(cmd, args):
    """notes [--all] [--json <rel>] [--bones]: ghi chú người dùng gửi từ chế độ Sửa (kèm pose đã key);
    note-done <id> [id...] | --all: đánh dấu đã xử lý."""
    try:
        notes = json.load(open(NOTES, encoding="utf8"))
    except (OSError, ValueError):
        notes = []
    if cmd == "note-done":
        ids = set(args)
        n = 0
        for x in notes:
            if x.get("status") == "open" and ("--all" in ids or x.get("id") in ids):
                x["status"] = "done"
                x["done_t"] = time.strftime("%Y-%m-%d %H:%M:%S")
                n += 1
                if x.get("request") == "gen" and x.get("frames"):
                    consume(x["json"], x.get("anim"), x["frames"])
        os.makedirs(os.path.dirname(NOTES), exist_ok=True)
        with open(NOTES + ".tmp", "w", encoding="utf8") as fh:
            json.dump(notes, fh, ensure_ascii=False, indent=1)
        os.replace(NOTES + ".tmp", NOTES)
        print(f"đã đánh dấu xong {n} ghi chú")
        return 0
    if cmd == "wait":   # chạy nền: thoát khi có ghi chú / yêu cầu gen chưa xử lý (Claude được báo ngay)
        timeout = float(opt(args, "--timeout", "0") or 0)
        t0 = time.time()
        while True:
            try:
                notes = json.load(open(NOTES, encoding="utf8"))
            except (OSError, ValueError):
                notes = []
            if any(x.get("status") == "open" for x in notes):
                return notes_cmd("notes", ["--bones"])
            if timeout and time.time() - t0 > timeout:
                print("hết giờ chờ, chưa có ghi chú mới")
                return 2
            time.sleep(1)
    show_all, bones = flag(args, "--all"), flag(args, "--bones")
    js = opt(args, "--json")
    sel = [x for x in notes if (show_all or x.get("status") == "open") and (not js or x.get("json") == js)]
    if not sel:
        print("Không có ghi chú mới từ Spine Live")
        return 0
    for x in sel:
        b = x.get("bones") or {}
        print(f"[{x['id']}] {x['t']} {x.get('status')}{' · YÊU CẦU GEN TIẾP' if x.get('request') == 'gen' else ''}"
              f" · {x['json']} · {x.get('anim')} @F{x.get('frame')}"
              f" · {'ĐÃ KEY vào file' if x.get('keyed') else 'chỉ ghi chú'} · {len(b)} xương")
        if x.get("note"):
            print("   ghi chú:", x["note"])
        if x.get("image"):
            print("   ảnh khung xem kèm nét vẽ:", os.path.join(ROOT, x["image"]))
        for i, k in enumerate((x.get("sketch") or {}).get("strokes") or []):   # góp ý vẽ (sketch.js), toạ độ skeleton (y lên)
            nb = lambda L: ", ".join(f"{q['bone']} {q['d']}" for q in L[:3])
            print(f"   nét {i + 1} ({k['color']}): {k['start']} -> {k['end']}, dài {k['length']}, hướng {k['angle']}°, "
                  f"giữa {k['mid']} trên layer {k.get('layer_mid')}")
            print(f"      gần xương - đầu nét: {nb(k['near_start'])} | giữa: {nb(k['near_mid'])} | cuối: {nb(k['near_end'])}")
        if x.get("desc"):
            print("   mô tả anim:", x["desc"])
        if x.get("keyposes") or x.get("frames"):   # gen từ nhiều keypose
            print("   các key đã keypose lại:", x.get("keyposes") or [])
            print("   gen tiếp từ các keypose:", x.get("frames") or [])
            if bones:
                for f, chans in keyed_values(x["json"], x.get("anim"), x.get("frames") or []).items():
                    print(f"   F{f}:")
                    for c in chans:
                        print("     " + c)
                continue
        if bones:
            for k, v in b.items():
                print(f"     {k}: xoay {v.get('rotate')} x {v.get('x')} y {v.get('y')}")
    return 0


def bridge(op, a, timeout=60):
    body = json.dumps({"op": op, "args": a, "timeout": timeout}).encode()
    req = urllib.request.Request(BASE + "/api/spine/br/cmd", body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout + 5) as r:
        return json.loads(r.read())


def csv(v, num=False):
    if not v:
        return []
    out = [x.strip() for x in v.split(",") if x.strip()]
    return [int(x) for x in out] if num else out


def bridge_cmd(cmd, args):
    if not args or args[0].startswith("--"):
        print("thiếu <json>"); return 1
    js = args[0]
    a = {"json": js, "anim": opt(args, "--anim")}
    if cmd == "pose":
        a.update(frames=csv(opt(args, "--frames"), True), bones=csv(opt(args, "--bones")))
    elif cmd == "measure":
        a.update(**{"from": opt(args, "--from"), "attach": csv(opt(args, "--attach")), "slots": csv(opt(args, "--slots")),
                    "rot": csv(opt(args, "--rot")), "top": int(opt(args, "--top", "8") or 8)})
    else:   # snap
        cell = opt(args, "--cell")
        box = opt(args, "--box")   # khung cố định x0,y0,x1,y1 (2026-11-18, ghép nhiều lần chụp thành video không nhảy)
        a.update(frames=csv(opt(args, "--frames"), True), bones=flag(args, "--bones"), cols=int(opt(args, "--cols", "0") or 0) or None,
                 cell=[int(x) for x in cell.lower().split("x")] if cell else None, nolabel=flag(args, "--nolabel"),
                 box=[float(x) for x in box.split(",")] if box else None)
    r = bridge(cmd, a)
    if not r.get("ok"):
        print("lỗi:", r.get("error")); return 1
    res = r["result"]
    if cmd == "snap":
        import base64
        out = opt(args, "--out") or os.path.join(ROOT, os.path.dirname(js), "_live", "snap.png")
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        with open(out, "wb") as fh:
            fh.write(base64.b64decode(res["png"].split(",", 1)[1]))
        print(f"ảnh {res['w']}x{res['h']} ({len(res['frames'])} frame, {r.get('ms')} ms) -> {os.path.abspath(out)}"
              + (f" · khung {','.join(str(round(v, 2)) for v in res['box'])}" if res.get("box") else ""))
        # ảnh tự kiểm thuộc một lần thử (tools/spine/trial.py, 2026-11-05): đăng ký để xoá cùng lần thử khi `done`.
        # --trial <tên>, hoặc tự nhận lần thử đang mở có bản sao / file gốc là <json>
        try:
            sys.path.insert(0, os.path.join(ROOT, "tools", "spine"))
            import trial as TR
            act = TR._load(); name = opt(args, "--trial")
            name = name or next((k for k, t in act.items() if js in (t["path"], t["src"])), None)
            if name in act:
                TR.add(name, out); print(f"  (ảnh thuộc lần thử '{name}': xoá khi trial.py done {name})")
        except Exception as e:
            print("  (không đăng ký được vào lần thử:", e, ")")
        return 0
    if cmd == "pose":
        print(f"{res['anim']} ({res['frames']} frame @{res['fps']}fps)")
        for f, row in res["pose"].items():
            print(f"{f}:")
            for n, v in row.items():
                if v is None:
                    print(f"  {n}: (không có)"); continue
                print(f"  {n}: thế giới ({v['wx']}, {v['wy']}) xoay {v['wrot']}° đầu xương {v['tip']} | local xoay {v['rot']} (+{v['drot']}) "
                      f"x {v['x']} (+{v['dx']}) y {v['y']} (+{v['dy']}) scale {v['sx']}/{v['sy']}")
        return 0
    print(f"{res['anim']}: {res['frames']} frame @{res['fps']}fps · {r.get('ms')} ms")
    s = res["loop_seam"]; print(f"  loop F0 vs F{res['frames']}: lệch tối đa {s['px']} px ({s['bone']})")
    if res.get("join"):
        j = res["join"]; w = j["with"]
        print(f"  nối với {w}: đầu vị trí {j['start_pos']['px']} px ({j['start_pos']['bone']}), đầu vận tốc {j['start_vel']['px']} px/f ({j['start_vel']['bone']})")
        print(f"             cuối vị trí {j['end_pos']['px']} px ({j['end_pos']['bone']}), cuối vận tốc {j['end_vel']['px']} px/f ({j['end_vel']['bone']})")
    print("  giật nhất (gia tốc đầu xương px/f², tốc độ px/f):")
    for x in res["jerkiest"]:
        print(f"    {x['bone']}: {x['accel']} @F{x['at']} · tốc {x['speed']}")
    for x in res.get("attach") or []:
        print(f"  bám {x['pair']}: trôi tối đa {x['drift_px']} px @F{x['at']}")
    for k, v in (res.get("slots") or {}).items():
        print(f"  slot {k}: {v}")
    for k, v in (res.get("rot") or {}).items():
        print(f"  góc {k}: {v}")
    return 0


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    cmd, args = argv[0], argv[1:]
    f = load()
    f.setdefault("log", [])
    if cmd == "status":
        try:
            cl = json.load(urllib.request.urlopen(BASE + "/api/spine/clients", timeout=3))
        except OSError as e:
            print("Không gọi được Home:", e)
            return 1
        if not cl:
            print("Không có trang Spine Live nào đang mở (" + BASE + "/spine)")
        for c in cl:
            print(f"trang {c['id']}: {'Theo Claude' if c['follow'] else 'KHÔNG theo Claude'} · {c['json']} · {c['anim']} · đã thấy bước {c['seq']}/{f.get('seq')}")
        return 0
    if cmd in ("pose", "measure", "snap"):
        return bridge_cmd(cmd, args)
    if cmd in ("notes", "note-done", "wait"):
        return notes_cmd(cmd, args)
    if cmd == "gen-start":   # đầu mỗi lượt yêu cầu: các lần gen trong lượt gộp thành 1 phiên bản
        g = gen_start(" ".join(args))
        print("nhóm gen mới:", g["id"], g["label"])
        return
    if cmd == "clear":
        f["log"] = []
    elif cmd == "say":
        f["say"] = " ".join(args)
    elif cmd == "history":   # lịch sử Hoàn tác / Làm lại của file trên Spine Live
        sys.path.insert(0, os.path.join(ROOT, "tools", "home"))
        import spine_live as SL
        h = SL.history(args[0].replace("\\", "/"))
        for k in ("undo", "redo"):
            print(k + ":")
            for e in h[k][:10] or [{"t": " " * 19, "who": "", "what": "(trống)"}]:
                print("  " + e["t"][11:19], e["who"] + ":", e["what"])
        return 0
    elif cmd == "show":
        if not args:
            print("thiếu <json>")
            return 1
        js = args.pop(0).replace("\\", "/")
        if os.path.isabs(js):
            js = os.path.relpath(js, ROOT).replace("\\", "/")
        if not os.path.isfile(os.path.join(ROOT, js)):
            print("không thấy", js)
            return 1
        f["json"] = js
        say = opt(args, "--say")
        anim = opt(args, "--anim")
        frame = opt(args, "--frame")
        weight = opt(args, "--weight")
        ui = opt(args, "--ui")   # tên nền UI trong <anim>/ui/*.json ("" = tắt)
        play = flag(args, "--play")
        view = {}
        for k, on, off in (("bones", "--bones", "--no-bones"), ("mesh", "--mesh", "--no-mesh")):
            if flag(args, on):
                view[k] = True
            elif flag(args, off):
                view[k] = False
        if weight is not None:
            view["weight"] = weight
        if ui is not None:
            view["ui"] = ui
        f["anim"] = anim
        f["frame"] = None if play or frame is None else float(frame)
        f["view"] = view
        f["say"] = say if say is not None else f.get("say", "")
        if args:
            print("bỏ qua:", " ".join(args))
    else:
        print("lệnh không biết:", cmd)
        return 1
    if cmd != "clear":
        f["seq"] = int(f.get("seq") or 0) + 1
        f["what"] = cmd   # "say": trang chỉ đổi chú thích, không nhảy file / frame
        f["t"] = time.strftime("%H:%M:%S")
        if f.get("say"):
            f["log"] = (f["log"] + [{"t": f["t"], "say": f["say"]}])[-KEEP_LOG:]
    save(f)
    print(f"bước {f.get('seq')}: {f.get('json', '')} {f.get('anim') or ''} {'' if f.get('frame') is None else 'F' + str(f['frame'])} {f.get('say', '')}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
