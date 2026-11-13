"""Chọn danh tính đăng nhập WorkAI / HorusChat: `ai` (AI Animation, mặc định) hoặc `haunv` (tài khoản của người dùng).

Thứ tự chọn: cờ `--profile <tên>` (lấy ra khỏi sys.argv) > biến AI_PROFILE > file tools/.profile > `ai`.
Đổi nhanh danh tính mặc định: `python -I tools/identity.py haunv` (hoặc `ai`); không tham số = xem đang là ai; thêm `--daemons` để chạy lại 2 bộ canh nền theo danh tính mới.
  - Khoá / token: <thư mục công cụ>/.env.<tên>  (git-ignored). Mẫu: .env.example
  - File mốc / hộp thư / nhật ký / khoá của bộ canh: danh tính `haunv` giữ tên cũ, danh tính khác thêm hậu tố _<tên>,
    nên hai danh tính chạy song song không đụng nhau.
"""
import os
import sys


def _take_cli():
    a = sys.argv
    for i, x in enumerate(a):
        if x == "--profile" and i + 1 < len(a):
            os.environ["AI_PROFILE"] = a[i + 1]
            del a[i:i + 2]
            return
        if x.startswith("--profile="):
            os.environ["AI_PROFILE"] = x.split("=", 1)[1]
            del a[i]
            return


_take_cli()
_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".profile")


def _saved():
    try:
        return open(_FILE, encoding="utf8").read().strip()
    except OSError:
        return ""


NAME = (os.environ.get("AI_PROFILE") or _saved() or "ai").strip().lower() or "ai"
LEGACY = "haunv"


def env_file(folder):
    return os.path.join(str(folder), ".env." + NAME)


def state_path(path):
    if NAME == LEGACY:
        return path
    root, ext = os.path.splitext(path)
    return f"{root}_{NAME}{ext}"


def _restart_daemons(here, name):
    """Tắt bộ canh nền WorkAI / HorusChat đang chạy rồi bật lại bằng danh tính `name` (Windows)."""
    import subprocess
    root = os.path.dirname(here)
    ps = ("Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'workai_daemon|horuschat_daemon' } "
          "| ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }")
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=False)
    py = os.path.join(root, ".venv", "Scripts", "pythonw.exe")
    for d in ("workai_daemon.py", "horuschat_daemon.py"):
        subprocess.Popen([py, "-I", os.path.join("tools", d), "--profile", name], cwd=root, creationflags=0x08000000)
    print("Đã chạy lại 2 bộ canh nền với danh tính", name)


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    sys.stdout.reconfigure(encoding="utf-8")
    flags = [a for a in sys.argv[1:] if a.startswith("--")]
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if args:
        want = args[0].strip().lower()
        if not (os.path.exists(os.path.join(here, "workai", ".env." + want))
                or os.path.exists(os.path.join(here, "horuschat_mcp", ".env." + want))):
            sys.exit(f"Chưa có danh tính '{want}': tạo tools/workai/.env.{want} và tools/horuschat_mcp/.env.{want} trước.")
        open(_FILE, "w", encoding="utf8").write(want)
        NAME = want
        if "--daemons" in flags:
            _restart_daemons(here, want)
    sys.path.insert(0, os.path.join(here, "workai"))
    sys.stdout.reconfigure(encoding="utf-8")
    print("Danh tính mặc định:", NAME)
    try:
        import workai
        c, o = workai.call("GET", "/api/auth/me")
        u = (o.get("data") or {}).get("user") or {}
        print("WorkAI   :", c, u.get("display_name"), u.get("email"), "id", u.get("id"))
    except SystemExit as e:
        print("WorkAI   :", e)
    sys.path.insert(0, os.path.join(here, "horuschat_mcp"))
    try:
        from horuschat_mcp.client import HorusChat
        print("HorusChat:", HorusChat().me().get("user_id"))
    except Exception as e:
        print("HorusChat:", type(e).__name__, str(e)[:120])
