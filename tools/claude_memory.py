"""Sao lưu / khôi phục bộ nhớ Claude Code của dự án, để đổi tài khoản / máy vẫn giữ.

Bộ nhớ Claude nằm ngoài dự án: ~/.claude/projects/<tên thư mục dự án>/memory/.
Script chép nó vào .claude/memory_store/ (nằm trong git của dự án) và chép ngược lại.

  python tools/claude_memory.py backup              # máy cũ: memory -> .claude/memory_store
  python tools/claude_memory.py backup --sessions   # thêm zip lịch sử phiên (to, ~500 MB) ra work/_claude_sessions.zip
  python tools/claude_memory.py restore             # máy / tài khoản mới: .claude/memory_store -> memory
  python tools/claude_memory.py status              # so hai bên
Kèm cấu hình MCP: .mcp.json + .claude/settings.local.json -> .claude/mcp_store (git),
khoá .env của MCP chat -> .claude/mcp_store/secrets (git bỏ qua). restore chỉ ghi file MCP còn thiếu, --force ghi đè.

Restore chỉ ghi thêm / ghi đè file cùng tên, không xoá file đang có ở đích.
"""
import argparse
import re
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT / ".claude" / "memory_store"
CLAUDE_HOME = Path.home() / ".claude"


def project_slug(p: Path) -> str:
    # Claude Code đặt tên thư mục: mọi ký tự không phải chữ/số thành "-" (E:\AI Animation -> E--AI-Animation)
    return re.sub(r"[^A-Za-z0-9]", "-", str(p))


def live_dir() -> Path:
    return CLAUDE_HOME / "projects" / project_slug(ROOT) / "memory"


def files(d: Path):
    return {f.relative_to(d).as_posix(): f for f in d.rglob("*") if f.is_file()} if d.exists() else {}


def copy_all(src: Path, dst: Path) -> int:
    n = 0
    for rel, f in files(src).items():
        t = dst / rel
        if t.exists() and t.read_bytes() == f.read_bytes():
            continue
        t.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, t)
        n += 1
    return n


MCP_STORE = ROOT / ".claude" / "mcp_store"
# cấu hình MCP + quyền của dự án (không có khoá) -> commit vào git
MCP_FILES = [".mcp.json", ".claude/settings.local.json"]
# khoá của MCP chat -> mcp_store/secrets (git bỏ qua, chỉ đi theo khi chép thư mục)
MCP_SECRETS = ["tools/horuschat_mcp/.env", "tools/rocketchat_mcp/.env"]


def mcp_pairs():
    for rel in MCP_FILES:
        yield ROOT / rel, MCP_STORE / rel
    for rel in MCP_SECRETS:
        yield ROOT / rel, MCP_STORE / "secrets" / rel


def mcp_backup():
    (MCP_STORE / "secrets").mkdir(parents=True, exist_ok=True)
    (MCP_STORE / ".gitignore").write_text("secrets/\n", encoding="utf-8")
    n = 0
    for live, store in mcp_pairs():
        if live.exists():
            store.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(live, store)
            n += 1
        else:
            print("  không thấy:", live.relative_to(ROOT))
    print(f"MCP: đã lưu {n} file -> {MCP_STORE}")


def mcp_restore(force: bool):
    for live, store in mcp_pairs():
        rel = live.relative_to(ROOT)
        if not store.exists():
            print("  chưa có bản lưu:", rel)
        elif live.exists() and live.read_bytes() != store.read_bytes() and not force:
            print("  giữ bản đang có (khác bản lưu, thêm --force để ghi đè):", rel)
        elif not live.exists() or force:
            live.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(store, live)
            print("  đã khôi phục:", rel)
    print("MCP: nhớ cài uv + Frolvy (C:/Program Files/Frolvy) trên máy mới; ComfyUI exe nằm sẵn trong ComfyUIMCP/")


def status():
    a, b = files(live_dir()), files(STORE)
    print(f"memory : {live_dir()}  ({len(a)} file)")
    print(f"store  : {STORE}  ({len(b)} file)")
    only_a = sorted(set(a) - set(b))
    only_b = sorted(set(b) - set(a))
    diff = sorted(k for k in set(a) & set(b) if a[k].read_bytes() != b[k].read_bytes())
    for k in only_a:
        print("  chỉ ở memory:", k)
    for k in only_b:
        print("  chỉ ở store :", k)
    for k in diff:
        print("  khác nhau   :", k)
    if not (only_a or only_b or diff):
        print("  hai bên khớp")
    for live, store in mcp_pairs():
        st = "thiếu bản lưu" if not store.exists() else ("khớp" if live.exists() and live.read_bytes() == store.read_bytes() else "khác")
        print(f"  MCP {live.relative_to(ROOT)}: {st}")


def backup(with_sessions: bool):
    src = live_dir()
    if not src.exists():
        sys.exit(f"Không thấy bộ nhớ ở {src}")
    n = copy_all(src, STORE)
    print(f"Đã chép {n} file thay đổi -> {STORE} (tổng {len(files(STORE))})")
    mcp_backup()
    if with_sessions:
        out = ROOT / "work" / "_claude_sessions.zip"
        proj = src.parent
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            for f in proj.rglob("*"):
                if f.is_file() and "memory" not in f.relative_to(proj).parts[:1]:
                    z.write(f, f.relative_to(proj).as_posix())
        print(f"Lịch sử phiên -> {out} ({out.stat().st_size // 2**20} MB)")


def restore(force=False):
    if not STORE.exists():
        sys.exit(f"Chưa có bản sao lưu ở {STORE}")
    dst = live_dir()
    n = copy_all(STORE, dst)
    print(f"Đã khôi phục {n} file -> {dst} (tổng {len(files(dst))})")
    mcp_restore(force)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["backup", "restore", "status"])
    ap.add_argument("--sessions", action="store_true")
    ap.add_argument("--force", action="store_true", help="restore: ghi đè cả file MCP đang có")
    a = ap.parse_args()
    {"backup": lambda: backup(a.sessions), "restore": lambda: restore(a.force), "status": status}[a.cmd]()
