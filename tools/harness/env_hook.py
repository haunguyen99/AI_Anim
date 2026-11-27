"""Hook SessionStart: nhận biết phiên chạy ở đâu (app Claude desktop / Paseo / VS Code / terminal).
Ngoài app desktop thì nạp vào ngữ cảnh bảng "thiếu công cụ app X thì dùng công cụ harness Y" (docs/harness.md).
Trong app desktop: im lặng (không tốn ngữ cảnh).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mcp_server as h  # noqa: E402

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if h.detect_env() != "desktop":
        print("[harness] " + h.env_text().replace("\n", "\n[harness] "))
        print("[harness] Công cụ harness có tên mcp__harness__* (plan, wrap_up, publish_page, studio, studio_snap, session). "
              "Dùng plan cho việc nhiều bước và wrap_up khi xong, như trong app desktop. Chi tiết: docs/harness.md.")
