"""Harness của repo: MCP server (stdio, không cần thư viện ngoài) bù các công cụ chỉ app Claude desktop mới có,
để phiên chạy trên Paseo / VS Code / terminal (Claude Code qua API) làm việc giống trong app.

Khai trong .mcp.json (tên "harness"). Tài liệu: docs/harness.md.

Công cụ:
  env           môi trường đang chạy + bảng "thiếu công cụ app X thì dùng Y"
  plan          danh sách việc (thay update_plan của app): ghi work/_harness/plans/<tên>.json, hiện ở Home /harness/
  wrap_up       chốt lượt (thay wrap_up của app): ghi tóm tắt + câu hỏi vào kế hoạch, trả khối chữ để in cho người dùng
  publish_page  đăng trang HTML local (thay Artifact): work/_harness/pages/<tên>/ → http://127.0.0.1:8780/harness/<tên>/
  studio        chạy lệnh cầu nối Studio (tools/studio_cmd.py), nhiều lệnh nối bằng ";"
  studio_snap   ảnh viewport Studio, trả ảnh cho model xem (thay chụp màn hình / trình duyệt của app)
  session       phiên con Paseo (thay start_session của app): run / ls / logs / send / mode / stop qua tools/paseo_cmd.py

Chạy thử tay:  .venv/Scripts/python.exe -I tools/harness/mcp_server.py --selftest
"""
import base64
import datetime as _dt
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
PY = sys.executable
HARNESS = os.path.join(ROOT, "work", "_harness")
PLANS = os.path.join(HARNESS, "plans")
PAGES = os.path.join(HARNESS, "pages")
HOME = "http://127.0.0.1:%s" % os.environ.get("HOME_PORT", "8780")
PROTOCOL = "2025-06-18"

# ---------------------------------------------------------------- môi trường

def detect_env():
    e = os.environ
    entry = e.get("CLAUDE_CODE_ENTRYPOINT", "")
    if entry == "claude-desktop" or e.get("CLAUDE_CODE_DESKTOP_APP_VERSION"):
        return "desktop"
    if any("PASEO" in k.upper() for k in e) or "paseo" in (e.get("CLAUDE_CODE_ENTRYPOINT", "") + e.get("TERM_PROGRAM", "")).lower():
        return "paseo"
    if "vscode" in entry or e.get("TERM_PROGRAM") == "vscode" or e.get("VSCODE_PID"):
        return "vscode"
    return "cli"


SUBSTITUTES = [
    ("Danh sách việc + ô bước tiếp theo (mcp__ccd_turn__update_plan / wrap_up)", "harness plan / harness wrap_up (Home /harness/)"),
    ("Artifact (trang review trên claude.ai)", "harness publish_page (trang local trên Home), hoặc Review Lab qua studio 'anim playblast'"),
    ("Trình duyệt trong app (mcp__Claude_Browser__*)", "Paseo: công cụ browser_* của Paseo; nơi khác: harness studio / studio_snap cho Studio"),
    ("Chụp màn hình / computer-use", "harness studio_snap (viewport Studio), ảnh render đọc bằng Read"),
    ("Tạo / chia phiên (mcp__ccd_session__start_session)", "harness session run|ls|logs|send|stop (Paseo), hoặc công cụ Agent cho việc ngắn"),
    ("visualize / show_widget (sơ đồ, bảng trong chat)", "viết HTML rồi harness publish_page"),
    ("Connector claude.ai (Gmail, Drive, Figma, Docs)", "không có khi chạy bằng key API; báo người dùng làm việc đó trong app desktop"),
    ("Skill anthropic-skills (pdf, docx, xlsx, pptx)", "chỉ dùng được skill trong .claude/skills/ của repo"),
    ("SendUserFile / thông báo điện thoại", "đưa đường dẫn file / link Home trong câu trả lời"),
]


def env_text():
    where = detect_env()
    lines = ["Môi trường: %s (thư mục %s)." % (where, ROOT)]
    if where == "desktop":
        lines.append("Đang trong app Claude desktop: dùng công cụ của app như thường; harness chỉ là dự phòng.")
    else:
        lines.append("Không có công cụ riêng của app desktop. Dùng thay thế:")
        lines += ["- %s: %s" % (a, b) for a, b in SUBSTITUTES]
    lines.append("Home %s: %s" % (HOME, "đang chạy" if home_alive() else "CHƯA chạy (Studio, trang /harness/ cần Home)"))
    return "\n".join(lines)


def home_alive():
    import urllib.request
    try:
        urllib.request.urlopen(HOME + "/api/studio/clients", timeout=1.5).read()
        return True
    except Exception:
        return False

# ---------------------------------------------------------------- kế hoạch

STATUS_MARK = {"completed": "[x]", "in_progress": "[>]", "pending": "[ ]"}


def _slug(s, fallback):
    s = re.sub(r"[^\w.-]+", "-", (s or "").strip(), flags=re.ASCII).strip("-.").lower()
    return s[:60] or fallback


def plan_name(name=None):
    if name:
        return _slug(name, "phien")
    sid = os.environ.get("CLAUDE_CODE_SESSION_ID") or os.environ.get("PASEO_AGENT_ID") or ""
    return _slug(sid[:8], "") or "phien-" + _dt.date.today().isoformat()


def _plan_path(name):
    return os.path.join(PLANS, name + ".json")


def load_plan(name):
    try:
        with open(_plan_path(name), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {"name": name, "items": [], "env": detect_env(), "created": _now()}


def save_plan(p):
    os.makedirs(PLANS, exist_ok=True)
    p["updated"] = _now()
    with open(_plan_path(p["name"]), "w", encoding="utf-8") as f:
        json.dump(p, f, ensure_ascii=False, indent=1)
    rebuild_index()


def _now():
    return _dt.datetime.now().isoformat(timespec="seconds")


def plan_text(p):
    out = ["Kế hoạch '%s':" % p["name"]]
    out += ["%d. %s %s" % (i + 1, STATUS_MARK.get(it.get("status"), "[ ]"), it.get("content", "")) for i, it in enumerate(p["items"])]
    if p.get("wrap"):
        out.append("Chốt: " + p["wrap"].get("recap", ""))
    return "\n".join(out)


def tool_plan(a):
    p = load_plan(plan_name(a.get("name")))
    items = p["items"]
    if a.get("items") is not None:
        items[:] = [{"content": str(x.get("content", "")), "status": x.get("status", "pending")} for x in a["items"]]
        p.pop("wrap", None)
        if a.get("title"):
            p["title"] = a["title"]
    if a.get("advance"):
        cur = next((i for i, it in enumerate(items) if it["status"] == "in_progress"), None)
        if cur is not None:
            items[cur]["status"] = "completed"
        nxt = next((it for it in items if it["status"] == "pending"), None)
        if nxt:
            nxt["status"] = "in_progress"
    for n in a.get("done") or []:
        if 1 <= int(n) <= len(items):
            items[int(n) - 1]["status"] = "completed"
    if a.get("start"):
        n = int(a["start"])
        for it in items:
            if it["status"] == "in_progress":
                it["status"] = "pending"
        if 1 <= n <= len(items):
            items[n - 1]["status"] = "in_progress"
    save_plan(p)
    return plan_text(p) + "\nXem trên Home: %s/harness/" % HOME


def tool_wrap_up(a):
    p = load_plan(plan_name(a.get("name")))
    for it in p["items"]:
        if it["status"] == "in_progress":
            it["status"] = "completed"
    p["wrap"] = {"recap": a.get("recap", ""), "ask": a.get("ask", ""), "actions": a.get("actions") or [], "at": _now()}
    save_plan(p)
    block = ["---", "Tóm tắt: " + a.get("recap", "")]
    if a.get("ask"):
        opts = " / ".join(a.get("actions") or [])
        block.append("Cần bạn quyết: %s%s" % (a["ask"], (" (" + opts + ")") if opts else ""))
    return ("Đã ghi chốt lượt. Không có ô 'bước tiếp theo' như app desktop: hãy in khối dưới đây ở CUỐI câu trả lời.\n\n"
            + "\n".join(block))

# ---------------------------------------------------------------- trang local

def tool_publish_page(a):
    name = _slug(a.get("name"), "")
    if not name or name in ("index", "plans"):
        raise ValueError("cần 'name' ngắn, không dấu (vd 'review-walk-v3')")
    dest = os.path.join(PAGES, name)
    os.makedirs(dest, exist_ok=True)
    if a.get("file"):
        src = os.path.abspath(os.path.join(ROOT, a["file"]))
        if not os.path.isfile(src):
            raise ValueError("không thấy file " + a["file"])
        shutil.copyfile(src, os.path.join(dest, "index.html"))
    elif a.get("html"):
        with open(os.path.join(dest, "index.html"), "w", encoding="utf-8") as f:
            f.write(a["html"])
    else:
        raise ValueError("cần 'html' hoặc 'file'")
    for rel in a.get("extra_files") or []:   # ảnh, js, css đi kèm: chép giữ tên file
        src = os.path.abspath(os.path.join(ROOT, rel))
        if os.path.isfile(src):
            shutil.copyfile(src, os.path.join(dest, os.path.basename(src)))
    meta = {"name": name, "title": a.get("title") or name, "updated": _now(), "env": detect_env()}
    with open(os.path.join(dest, "page.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False)
    rebuild_index()
    url = "%s/harness/%s/" % (HOME, name)
    return "Đã đăng: %s%s" % (url, "" if home_alive() else "\n(Home chưa chạy: mở Home trước rồi mới xem được link)")


def rebuild_index():
    """Trang tổng work/_harness/pages/index.html: kế hoạch các phiên + trang đã đăng."""
    os.makedirs(PAGES, exist_ok=True)
    plans = []
    for fn in sorted(os.listdir(PLANS)) if os.path.isdir(PLANS) else []:
        if fn.endswith(".json"):
            try:
                with open(os.path.join(PLANS, fn), encoding="utf-8") as f:
                    plans.append(json.load(f))
            except (OSError, ValueError):
                pass
    plans.sort(key=lambda p: p.get("updated", ""), reverse=True)
    pages = []
    for d in sorted(os.listdir(PAGES)):
        mp = os.path.join(PAGES, d, "page.json")
        if os.path.isfile(mp):
            try:
                with open(mp, encoding="utf-8") as f:
                    pages.append(json.load(f))
            except (OSError, ValueError):
                pass
    pages.sort(key=lambda p: p.get("updated", ""), reverse=True)
    e = html.escape
    rows = []
    for p in plans[:30]:
        li = "".join('<li class="%s">%s</li>' % (e(it.get("status", "")), e(it.get("content", ""))) for it in p.get("items", []))
        w = p.get("wrap") or {}
        wrap = ""
        if w:
            wrap = '<p class="wrap">%s%s</p>' % (e(w.get("recap", "")), ("<br><b>Cần quyết:</b> " + e(w["ask"])) if w.get("ask") else "")
        rows.append('<section><h3>%s <small>%s · %s</small></h3><ol>%s</ol>%s</section>'
                    % (e(p.get("title") or p["name"]), e(p.get("env", "")), e(p.get("updated", "")), li, wrap))
    pg = "".join('<li><a href="%s/">%s</a> <small>%s</small></li>' % (e(p["name"]), e(p.get("title", p["name"])), e(p.get("updated", ""))) for p in pages)
    doc = """<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Harness</title><meta http-equiv="refresh" content="5"><style>
:root{--bg:#fafafa;--fg:#1d1d1f;--mut:#777;--card:#fff;--line:#e3e3e3;--acc:#2f6fdb}
@media (prefers-color-scheme:dark){:root{--bg:#161616;--fg:#eee;--mut:#999;--card:#212121;--line:#333;--acc:#6ea0ff}}
body{background:var(--bg);color:var(--fg);font:14px/1.5 system-ui,sans-serif;margin:0;padding:16px;max-width:900px;margin:auto}
section{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:8px 14px;margin:10px 0}
h3{margin:4px 0}small{color:var(--mut);font-weight:normal}a{color:var(--acc)}
li.completed{color:var(--mut);text-decoration:line-through}li.in_progress{font-weight:600}li.in_progress::marker{color:var(--acc)}
.wrap{border-top:1px solid var(--line);padding-top:6px}
</style></head><body><h1>Harness</h1><h2>Trang đã đăng</h2><ul>%s</ul><h2>Kế hoạch các phiên</h2>%s</body></html>""" % (pg or "<li><small>chưa có</small></li>", "".join(rows) or "<p><small>chưa có</small></p>")
    with open(os.path.join(PAGES, "index.html"), "w", encoding="utf-8") as f:
        f.write(doc)

# ---------------------------------------------------------------- Studio, Paseo

def _run(args, timeout=120):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    p = subprocess.run([PY, "-I"] + args, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       cwd=ROOT, timeout=timeout, env=env)
    out = ((p.stdout or "") + (p.stderr or "")).strip()
    if len(out) > 12000:
        out = out[:12000] + "\n… (cắt bớt)"
    return p.returncode, out


def _split_cmd(s):
    import shlex
    return shlex.split(s, posix=True)


def tool_studio(a):
    cmd = (a.get("command") or "").strip()
    if not cmd:
        raise ValueError("cần 'command', vd 'state' hoặc 'vis A off ; select joint B'")
    if not home_alive():
        raise ValueError("Home chưa chạy (%s): mở Home / Studio trước (skill /studio)" % HOME)
    args = _split_cmd(re.sub(r"\s*;\s*", " ; ", cmd))   # studio_cmd.py nhận ";" là một tham số riêng
    code, out = _run([os.path.join(ROOT, "tools", "studio_cmd.py")] + args, timeout=int(a.get("timeout", 120)))
    return out or ("xong" if code == 0 else "lỗi (mã %d)" % code)


def tool_studio_snap(a):
    if not home_alive():
        raise ValueError("Home chưa chạy (%s): mở Home / Studio trước (skill /studio)" % HOME)
    fd, path = tempfile.mkstemp(suffix=".png", prefix="studio_snap_")
    os.close(fd)
    cmd = []
    if a.get("view"):
        cmd += ["view"] + _split_cmd(a["view"]) + [";"]
    cmd += ["snap", path] + ([a["size"]] if a.get("size") else [])
    code, out = _run([os.path.join(ROOT, "tools", "studio_cmd.py")] + cmd)
    if not os.path.isfile(path) or os.path.getsize(path) == 0:
        raise ValueError("không chụp được viewport: " + (out or "Studio chưa mở?"))
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return [{"type": "text", "text": (out + "\n" if out else "") + "ảnh: " + path},
            {"type": "image", "data": data, "mimeType": "image/png"}]


def tool_session(a):
    act = a.get("action")
    tool = os.path.join(ROOT, "tools", "paseo_cmd.py")
    if act == "run":
        if not a.get("name") or not a.get("brief"):
            raise ValueError("run cần 'name' (ngắn, không dấu) và 'brief'")
        d = os.path.join(ROOT, "work", "_subsessions", "paseo")
        os.makedirs(d, exist_ok=True)
        bf = os.path.join(d, _slug(a["name"], "viec") + ".brief.in.md")
        with open(bf, "w", encoding="utf-8") as f:
            f.write(a["brief"])
        args = ["run", _slug(a["name"], "viec"), "@" + bf]
    elif act == "ls":
        args = ["ls"] + ([a["filter"]] if a.get("filter") else [])
    elif act == "logs":
        args = ["logs", a["id"], "--tail", str(a.get("tail", 30))]
    elif act == "send":
        args = ["send", a["id"], a.get("text", "")]
    elif act in ("stop", "mode"):
        args = [act, a["id"]] + ([a["mode"]] if act == "mode" and a.get("mode") else [])
    else:
        raise ValueError("action phải là run | ls | logs | send | mode | stop")
    code, out = _run([tool] + args, timeout=180)
    return out or "lỗi (mã %d)" % code

# ---------------------------------------------------------------- khai báo công cụ

def _obj(props, req=()):
    return {"type": "object", "properties": props, "required": list(req)}


S = {"type": "string"}
TOOLS = [
    ("env", "Môi trường đang chạy (desktop / paseo / vscode / cli), Home có chạy không, và bảng công cụ thay thế khi thiếu công cụ của app Claude desktop. Gọi một lần đầu phiên.",
     _obj({}), lambda a: env_text()),
    ("plan", "Danh sách việc của phiên (thay update_plan của app desktop). Lần đầu: items = cả kế hoạch, bước đang làm 'in_progress'. Sau đó: advance=true khi sang bước mới; done=[số] / start=số khi làm lệch thứ tự. Hiện ở Home /harness/.",
     _obj({"items": {"type": "array", "items": _obj({"content": S, "status": {"enum": ["pending", "in_progress", "completed"]}}, ["content"])},
           "advance": {"type": "boolean"}, "done": {"type": "array", "items": {"type": "integer"}}, "start": {"type": "integer"},
           "title": S, "name": {"type": "string", "description": "tên kế hoạch; bỏ trống = theo phiên"}}), tool_plan),
    ("wrap_up", "Chốt lượt khi xong việc (thay wrap_up của app desktop): recap 2-3 câu, ask = một câu hỏi nếu người dùng cần quyết, actions = 1-2 lựa chọn. Trả khối chữ để in cuối câu trả lời.",
     _obj({"recap": S, "ask": S, "actions": {"type": "array", "items": S}, "name": S}, ["recap"]), tool_wrap_up),
    ("publish_page", "Đăng trang HTML để người dùng xem (thay Artifact): html (nội dung) hoặc file (đường dẫn trong repo), extra_files = ảnh/js/css đi kèm. Trả link Home http://127.0.0.1:8780/harness/<name>/. Đăng lại cùng name = cập nhật.",
     _obj({"name": S, "title": S, "html": S, "file": S, "extra_files": {"type": "array", "items": S}}, ["name"]), tool_publish_page),
    ("studio", "Chạy lệnh cầu nối Studio (tools/studio_cmd.py, xem đầu file đó / lệnh 'cmds'). Nhiều lệnh nối bằng ' ; '. Vd 'state', 'anim frame 12 ; anim read Chest_M'.",
     _obj({"command": S, "timeout": {"type": "integer"}}, ["command"]), tool_studio),
    ("studio_snap", "Ảnh viewport Studio đang mở, trả ảnh để tự kiểm (không phải chụp màn hình báo cáo). view = tham số lệnh view (vd '1 front all'), size = 'WxH'.",
     _obj({"view": S, "size": S}), tool_studio_snap),
    ("session", "Phiên con Paseo (thay start_session của app desktop). action: run (name + brief: tạo phiên), ls [filter], logs (id, tail), send (id, text), mode (id, mode), stop (id). Phiên con không tự báo về: đọc logs khi cần.",
     _obj({"action": {"enum": ["run", "ls", "logs", "send", "mode", "stop"]}, "name": S, "brief": S, "id": S, "text": S,
           "filter": S, "tail": {"type": "integer"}, "mode": S}, ["action"]), tool_session),
]
BY_NAME = {t[0]: t for t in TOOLS}

# ---------------------------------------------------------------- JSON-RPC stdio

def handle(msg):
    mid, method, params = msg.get("id"), msg.get("method"), msg.get("params") or {}
    if method == "initialize":
        return {"protocolVersion": params.get("protocolVersion") or PROTOCOL,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "harness", "version": "1.0"},
                "instructions": "Harness của repo AI Animation: bù công cụ của app Claude desktop khi chạy trên Paseo / VS Code / terminal. Gọi 'env' đầu phiên để biết dùng gì thay gì."}
    if method == "tools/list":
        return {"tools": [{"name": n, "description": d, "inputSchema": s} for n, d, s, _ in TOOLS]}
    if method == "tools/call":
        t = BY_NAME.get(params.get("name"))
        if not t:
            raise KeyError("không có công cụ " + str(params.get("name")))
        try:
            r = t[3](params.get("arguments") or {})
            content = r if isinstance(r, list) else [{"type": "text", "text": str(r)}]
            return {"content": content, "isError": False}
        except Exception as ex:   # lỗi công cụ trả cho model đọc, không làm sập server
            return {"content": [{"type": "text", "text": "Lỗi: %s" % ex}], "isError": True}
    if method == "ping":
        return {}
    if mid is None:   # thông báo (notifications/*): không trả lời
        return None
    raise KeyError("method " + str(method))


def serve():
    stdin = open(sys.stdin.fileno(), "r", encoding="utf-8", newline="\n", closefd=False)
    out = open(sys.stdout.fileno(), "w", encoding="utf-8", newline="\n", closefd=False)
    for line in stdin:
        line = line.strip().lstrip("﻿")
        if not line:
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            continue
        mid = msg.get("id")
        try:
            res = handle(msg)
            if mid is None:
                continue
            reply = {"jsonrpc": "2.0", "id": mid, "result": res}
        except Exception as ex:
            if mid is None:
                continue
            reply = {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601 if isinstance(ex, KeyError) else -32603, "message": str(ex)}}
        out.write(json.dumps(reply, ensure_ascii=False) + "\n")
        out.flush()


def selftest():
    print(env_text())
    print(json.dumps([t["name"] for t in handle({"id": 1, "method": "tools/list"})["tools"]]))
    name = "_selftest"
    print(tool_plan({"name": name, "items": [{"content": "A", "status": "in_progress"}, {"content": "B"}]}))
    print(tool_plan({"name": name, "advance": True}))
    print(tool_wrap_up({"name": name, "recap": "thử xong", "ask": "Tiếp?", "actions": ["Có", "Không"]}))
    print(tool_publish_page({"name": "_selftest", "title": "Thử", "html": "<!doctype html><title>Thử</title><p>ok</p>"}))
    os.remove(_plan_path(name))
    shutil.rmtree(os.path.join(PAGES, "_selftest"), ignore_errors=True)
    rebuild_index()
    print("selftest ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.stdout.reconfigure(encoding="utf-8")
        selftest()
    else:
        serve()
