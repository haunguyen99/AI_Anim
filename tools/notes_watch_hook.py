"""Hook Claude Code (SessionStart + UserPromptSubmit, cấu hình ở .claude/settings.json).
Có trang Studio đang mở (GET /api/studio/clients) mà không có bộ canh ghi chú nào chạy
(nhịp tim tools/notes_watch.py cũ hơn 10 s) → nhắc Claude bật bộ canh nền. Còn lại im lặng.
Không bao giờ chặn lượt chat: lỗi gì cũng thoát 0.
"""
import json, os, sys, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from notes_watch import alive  # noqa: E402


def studio_open():
    try:
        with urllib.request.urlopen("http://127.0.0.1:8780/api/studio/clients", timeout=1) as r:
            return len(json.loads(r.read() or b"[]")) > 0
    except Exception:
        return False


def main():
    try:
        ev = json.load(sys.stdin).get("hook_event_name") or "UserPromptSubmit"
    except Exception:
        ev = "UserPromptSubmit"
    if alive() or not studio_open():
        return 0
    msg = ("Studio đang mở nhưng chưa có bộ canh ghi chú vẽ. Trước việc khác, bật nó nền (Bash, run_in_background): "
           "`.venv/Scripts/python.exe -I tools/notes_watch.py`. Khi nó thoát và in danh sách ghi chú: làm theo /check_fb "
           "(phần Studio notes), sửa, `studio_cmd.py note-done`; mục kind rig_gate (Duyệt / Cần sửa một bước Rig) thì theo /rig mục 2 Studio: "
           "duyệt = tự làm bước kế, cần sửa = sửa bước đó, xong `studio_cmd.py gate-done`; rồi bật lại bộ canh. Không cần báo người dùng việc bật.")
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps({"hookSpecificOutput": {"hookEventName": ev, "additionalContext": msg}}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
