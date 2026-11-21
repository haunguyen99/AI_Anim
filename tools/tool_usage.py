"""Đếm số lần mỗi công cụ của repo được gọi, để biết công cụ nào thật sự được dùng lại.

Lý do: trước khi đưa một công cụ vào Frolvy (hoặc xoá nó), phải có bằng chứng nó được
gọi nhiều lần, ở nhiều phiên. Git chỉ cho biết công cụ được VIẾT khi nào, không cho biết
nó được CHẠY bao nhiêu lần.

Hai chế độ:
  python -I tools/tool_usage.py hook     # hook PostToolUse: đọc JSON từ stdin, ghi 1 dòng mỗi lần gọi
  python -I tools/tool_usage.py report [--since 2026-11-01] [--kind tool|skill|plugin]

Ghi gì: thời gian, máy, phiên, loại (tool / skill / plugin), tên. KHÔNG ghi lệnh đầy đủ,
tham số hay nội dung file: chỉ cần biết tên công cụ.

Ghi vào đâu: .claude/usage/<tên máy>.jsonl, mỗi máy một file nên nhiều người commit
không đụng nhau. Báo cáo gộp mọi file trong thư mục đó.
"""
import datetime
import json
import os
import re
import socket
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USAGE_DIR = os.path.join(ROOT, ".claude", "usage")

# tools/<tên>.py hoặc tools/<thư mục>/<tên>.py, dấu / hoặc \
TOOL_RE = re.compile(r"tools[\\/]+((?:[A-Za-z0-9_\-]+[\\/]+)?[A-Za-z0-9_\-]+)\.py")
# Plugin Frolvy của repo, gọi qua api trong execute_code hoặc qua tên thư mục
PLUGIN_RE = re.compile(r"frolvy_plugins[\\/]+([A-Za-z0-9_\-]+)")

# Từ đầu tiên sau tên file, nếu là một chữ ngắn (không phải đường dẫn hay cờ): lệnh con.
SUBCOMMAND_RE = re.compile(r"\s+([a-z][a-z_\-]{1,24})(?=\s|$)")


def _plugin_names():
    d = os.path.join(ROOT, "tools", "frolvy_plugins")
    try:
        return [n for n in os.listdir(d) if os.path.isdir(os.path.join(d, n))]
    except OSError:
        return []


# Công cụ của chính hệ thống hook: không đếm, kẻo số liệu toàn là chính nó.
SKIP = {"tool_usage", "notes_watch_hook", "knowledge_sync", "harness/env_hook"}

# Lệnh chỉ ĐỌC hay SỬA mã nguồn công cụ, không chạy nó.
READ_ONLY = re.compile(r"^\s*(cat|head|tail|sed\s+-n|less|grep|rg|git\s+(log|diff|show|blame)|wc|ls)\b")


def _names(tool_name, tool_input):
    """Những (loại, tên) mà một lần gọi tool của Claude đã chạy."""
    out = []
    if tool_name == "Skill":
        skill = str(tool_input.get("skill", "")).strip()
        if skill:
            out.append(("skill", skill))
        return out

    if tool_name in ("Read", "Edit", "Write", "Grep", "Glob", "NotebookEdit"):
        return out

    if tool_name in ("Bash", "PowerShell"):
        text = str(tool_input.get("command", ""))
        # Mỗi lệnh con trong chuỗi && ; | xét riêng: "cat tools/x.py && python tools/y.py" chỉ chạy y.
        parts = re.split(r"&&|\|\||;|\n|\|", text)
    else:
        # mcp__*: code Python gửi vào Frolvy, hay tham số của server khác
        parts = [json.dumps(tool_input, ensure_ascii=False)]

    plugins = _plugin_names()
    for part in parts:
        if READ_ONLY.search(part):
            continue
        for m in TOOL_RE.finditer(part):
            name = m.group(1).replace("\\", "/")
            name = re.sub(r"/+", "/", name)
            if name in SKIP:
                continue
            # Lệnh con (frolvy_port.py clear, studio_cmd.py state): đếm riêng từng lệnh,
            # vì "công cụ nào hay dùng" thường là "lệnh con nào hay dùng".
            sub = SUBCOMMAND_RE.match(part[m.end():])
            out.append(("tool", name + (" " + sub.group(1) if sub else "")))
        for m in PLUGIN_RE.finditer(part):
            out.append(("plugin", m.group(1)))
        # Plugin gọi theo tên trong code gửi vào Frolvy (anim_ops.clear_part(...)).
        if tool_name.startswith("mcp__"):
            for p in plugins:
                if re.search(r"\b" + re.escape(p) + r"\b", part):
                    out.append(("plugin", p))
    # Một lệnh gọi cùng công cụ hai lần vẫn là một lần dùng.
    return sorted(set(out))


def hook():
    try:
        event = json.load(sys.stdin)
    except Exception:
        return 0
    names = _names(event.get("tool_name", ""), event.get("tool_input") or {})
    if not names:
        return 0
    os.makedirs(USAGE_DIR, exist_ok=True)
    host = re.sub(r"[^A-Za-z0-9_\-]", "_", socket.gethostname()) or "unknown"
    now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    session = str(event.get("session_id", ""))[:36]
    with open(os.path.join(USAGE_DIR, host + ".jsonl"), "a", encoding="utf-8") as f:
        for kind, name in names:
            f.write(json.dumps({"t": now, "host": host, "session": session,
                                "kind": kind, "name": name}, ensure_ascii=False) + "\n")
    return 0


def load(since=None):
    rows = []
    if not os.path.isdir(USAGE_DIR):
        return rows
    for fn in sorted(os.listdir(USAGE_DIR)):
        if not fn.endswith(".jsonl"):
            continue
        with open(os.path.join(USAGE_DIR, fn), encoding="utf-8", errors="replace") as f:
            for line in f:
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                if since and r.get("t", "")[:10] < since:
                    continue
                rows.append(r)
    return rows


def report(argv):
    # -I bỏ qua PYTHONIOENCODING: console Windows mặc định cp1252 không in được tiếng Việt.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    since = kind = None
    if "--since" in argv:
        since = argv[argv.index("--since") + 1]
    if "--kind" in argv:
        kind = argv[argv.index("--kind") + 1]
    rows = [r for r in load(since) if not kind or r.get("kind") == kind]
    if not rows:
        print("Chưa có lần gọi nào được ghi (.claude/usage/ trống).")
        return 0

    stats = {}
    for r in rows:
        key = (r.get("kind", "?"), r.get("name", "?"))
        s = stats.setdefault(key, {"calls": 0, "sessions": set(), "hosts": set(), "days": set(),
                                   "first": r["t"], "last": r["t"]})
        s["calls"] += 1
        s["sessions"].add(r.get("session"))
        s["hosts"].add(r.get("host"))
        s["days"].add(r.get("t", "")[:10])
        s["first"] = min(s["first"], r["t"])
        s["last"] = max(s["last"], r["t"])

    # Dùng lại = nhiều PHIÊN, không phải nhiều lần trong một phiên.
    order = sorted(stats.items(), key=lambda kv: (-len(kv[1]["sessions"]), -kv[1]["calls"]))
    print(f"{'loại':6} {'tên':34} {'lần':>5} {'phiên':>5} {'ngày':>4} {'máy':>3}  gần nhất")
    for (k, n), s in order:
        print(f"{k:6} {n[:34]:34} {s['calls']:5} {len(s['sessions']):5} {len(s['days']):4} "
              f"{len(s['hosts']):3}  {s['last'][:10]}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "hook":
        sys.exit(hook())
    if len(sys.argv) > 1 and sys.argv[1] == "report":
        sys.exit(report(sys.argv[2:]))
    print(__doc__)
