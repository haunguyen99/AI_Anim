"""Đóng gói Spine Live + các skill Spine 2D thành một thư mục / zip dùng được với Codex (OpenAI Codex CLI / app).

  .venv/Scripts/python.exe -I tools/spine_live/pack_codex.py            -> work/_pack/spinelive_codex_<ngày>.zip
  .venv/Scripts/python.exe -I tools/spine_live/pack_codex.py --out D:/x  -> thư mục + zip ở chỗ khác

Gói giữ đúng bố cục thư mục của dự án (tools/spine_live, tools/home/spine_*.py, tools/spine, tools/spine_mcp,
tools/spine_live_*.py) nên code chạy y như ở đây; thêm AGENTS.md (luật cho Codex), skill trong .agents/skills/,
setup.bat / start_spine_live.bat, mẫu cấu hình MCP cho Codex. Không chép dữ liệu work/ (file Spine của các game).
"""
import os, re, shutil, sys, time, zipfile

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
SKIP_DIRS = {"__pycache__", ".venv", ".git", "node_modules", ".pytest_cache"}

COPY = [
    "tools/spine_live",
    "tools/spine",
    "tools/spine_mcp",
    "tools/home/spine_live.py",
    "tools/home/spine_edit.py",
    "tools/home/spine_bridge.py",
    "tools/spine_live_cmd.py",
    "tools/spine_live_recent.py",
    "tools/spine_live_replay.py",
    "requirements.txt",
]
SKILLS = ["spine2d", "skillidle", "skillactive", "exportspine"]   # spinelive viết lại cho Codex bên dưới

# Câu riêng của Claude trong skill -> cách làm tương ứng trong Codex (ghi chú đầu mỗi skill, không sửa nội dung gốc)
SKILL_NOTE = """> **Ghi chú khi chạy trong Codex** (gói spinelive_codex): skill này viết cho Claude. Chỗ nào nhắc
> `preview_start`, `navigate`, `javascript_tool`, `show_pane`, "khung trình duyệt của Claude": trong Codex
> thay bằng `start_spine_live.bat` (bật server + mở trình duyệt) hoặc đưa link `http://127.0.0.1:8781/spine?json=...`
> cho người dùng tự mở, rồi kiểm bằng `python -I tools/spine_live_cmd.py status`. Mọi lệnh `.venv/Scripts/python.exe -I tools/...`
> giữ nguyên. Đọc `AGENTS.md` ở gốc gói trước.

"""

AGENTS_MD = """# Luật cho Codex: Spine Live + anim Spine 2D

Gói này tách từ dự án AI Animation (đóng gói {date}). Người dùng là animator 2D, nói tiếng Việt.

## Trả lời
- Mọi câu trả lời bằng **tiếng Việt**, câu đầu là kết quả, câu ngắn, dùng từ của nghề anim (xương, slot, mesh, weight, key, pose, loop).
- Không dán code / log / JSON dài vào câu trả lời trừ khi được hỏi. Báo trước bước nào lâu.

## Skill
Skill nằm ở `.agents/skills/` (mỗi thư mục một `SKILL.md`). Đọc skill tương ứng trước khi làm:
| Việc | Skill |
|---|---|
| Mở Spine Live, file Spine sửa gần nhất | `.agents/skills/spinelive/SKILL.md` |
| Rig / anim Spine 2D nói chung (xương, mesh, weight, key, export, Spine Live, cầu nối lệnh) | `.agents/skills/spine2d/SKILL.md` |
| Dựng idle loop | `.agents/skills/skillidle/SKILL.md` |
| Dựng active (một lần, vào ra đúng idle F0) + mix | `.agents/skills/skillactive/SKILL.md` |
| Xuất bản giao (JSON + atlas + PNG) | `.agents/skills/exportspine/SKILL.md` |

Các skill viết cho Claude: thay công cụ trình duyệt của Claude bằng trình duyệt thường của người dùng (xem mục dưới); mọi lệnh Python giữ nguyên.

## Chạy
- Lần đầu: `setup.bat` (tạo `.venv`, cài numpy / opencv / pillow). Python 3.10+ phải có sẵn trên máy.
- Bật Spine Live: `.venv/Scripts/python.exe -I tools/spine_live/ensure_server.py` (chạy riêng, không cửa sổ, thoát ngay khi server sống). Kiểm: `curl http://127.0.0.1:8781/api/spine/ping`. Log: `work/store/_sys/spine_live/server.log`.
- Người dùng tự bật + mở trang: `start_spine_live.bat`.
- Codex không có khung trình duyệt riêng: chọn file bằng `tools/spine_live_recent.py [từ khoá]`, đưa link `url` nó in ra thành một dòng riêng để người dùng bấm mở; kiểm trang đã mở bằng `tools/spine_live_cmd.py status`.
- Dữ liệu Spine để ở `work/<game>/spine/<anim>/` (JSON + images/ + atlas). Trang chỉ thấy file trong `work/`. Bản thử tạm để trong `work/<game>/spine/<anim>/_live/`.
- Đẩy bước đang làm lên trang (người dùng bật "Theo Claude" trên trang): `tools/spine_live_cmd.py show <json> --anim <a> [--frame N] [--say "..."]`, `say "..."`.
- Đo / chụp bằng runtime Spine thật trên trang đang mở: `tools/spine_live_cmd.py pose|measure|snap ...` (xem spine2d). Ghi chú người dùng vẽ trên trang: `spine_live_cmd.py notes --bones`, xong `note-done <id>`.
- Mỗi lượt yêu cầu có ghi file Spine: chạy `tools/spine_live_cmd.py gen-start "<tóm tắt>"` trước để mọi lần ghi trong lượt gộp vào một phiên bản ở cột Phiên bản.
- Thử rig / anim trên bản sao: `tools/spine/trial.py new <json> <tên> --why "..."`, có kết quả thì `trial.py done <tên> --result "..."`.

## Spine editor + MCP (tuỳ chọn)
- Xuất / đóng gói atlas cần Spine editor 4.2.x (`SPINE_EXE`, mặc định `C:\\Program Files\\Spine\\Spine.com`).
- Server MCP `spine` (sửa skeleton JSON, gọi Spine CLI) ở `tools/spine_mcp` (chạy bằng `uv`). Cách khai báo cho Codex: `codex_config_example.toml`.

## Bản đồ file
Mô tả từng tool Spine: `docs/SPINE_MAP.md`.
"""

SPINELIVE_SKILL = """---
name: spinelive
description: Mở Spine Live (trang xem / sửa skeleton Spine 2D chạy trên máy, http://127.0.0.1:8781/spine) với file Spine sửa gần nhất hoặc file khớp từ khoá. Dùng khi người dùng gõ /spinelive, nói "mở spine live", "mở file spine gần nhất", hoặc /spinelive <tên game / anim / file>.
---

# /spinelive (bản cho Codex)

Trả lời bằng tiếng Việt, ngắn. Trang: `tools/spine_live/`; xử lý: `tools/home/spine_live.py` + `spine_edit.py` + `spine_bridge.py`; server `tools/spine_live/server.py` cổng 8781 (`SPINE_PORT`). Luật làm Spine ở skill `spine2d`.

1. **Server:** `curl -s -o /dev/null -w "%{http_code}" --max-time 3 http://127.0.0.1:8781/api/spine/list`.
   Không ra `200` thì `.venv/Scripts/python.exe -I tools/spine_live/ensure_server.py` (bật server chạy riêng, đợi `/api/spine/ping` rồi thoát). Không bật lại khi đã chạy.
2. **Chọn file:** `.venv/Scripts/python.exe -I tools/spine_live_recent.py [từ khoá]` -> một dòng JSON `{json, label, kind, sửa lúc, url}`.
   Người dùng gõ `list` / "chọn file": `... spine_live_recent.py --list 8`, đưa danh sách và hỏi file nào. `{"error": ...}`: báo đúng câu đó; không khớp từ khoá thì gợi ý bằng `--list 8`.
3. **Mở trang:** Codex không có khung trình duyệt riêng. Đưa `url` thành một dòng riêng để người dùng bấm mở (hoặc người dùng chạy `start_spine_live.bat`).
   Trên Windows có thể mở thay người dùng bằng `start "" "<url>"` nếu họ muốn.
4. **Kiểm đã mở:** đợi người dùng mở rồi `.venv/Scripts/python.exe -I tools/spine_live_cmd.py status` (thấy trang đang mở + file).
5. **Báo một dòng:** file nào (label + sửa lúc), các anim trong file (đọc tên trong mục `animations` của JSON).

## Sau khi mở
- Đẩy bước đang làm lên trang: `tools/spine_live_cmd.py show <json> --anim <a> [--frame N] [--say "..."]` (trang ở chế độ Theo Claude tự nhảy theo); `status` xem trang nào đang mở.
- Ghi chú / pose người dùng gửi từ trang: `tools/spine_live_cmd.py notes --bones`.
"""

SETUP_BAT = r"""@echo off
rem Tao moi truong Python cho Spine Live (chay mot lan).
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  py -3 -m venv .venv 2>nul || python -m venv .venv
)
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
echo.
echo Xong. Bat Spine Live: start_spine_live.bat
pause
"""

START_BAT = r"""@echo off
rem Bat server Spine Live (chay rieng) roi mo trang trong trinh duyet.
cd /d "%~dp0"
".venv\Scripts\python.exe" -I tools\spine_live\ensure_server.py
start "" http://127.0.0.1:8781/spine
"""

CODEX_TOML = """# Khai báo server MCP `spine` cho Codex: chép khối dưới vào ~/.codex/config.toml
# (hoặc .codex/config.toml trong thư mục gói nếu Codex của bạn đọc cấu hình theo dự án).
# Cần `uv` (https://docs.astral.sh/uv/) và Spine editor 4.2.x. Sửa đường dẫn cho đúng chỗ giải nén gói.

[mcp_servers.spine]
command = "uv"
args = ["run", "--directory", "C:/duong_dan/spinelive_codex/tools/spine_mcp", "spine-mcp"]
"""

WORK_README = """Dữ liệu Spine để ở đây: work/<game>/spine/<anim>/ (skeleton JSON + images/ + atlas).
Spine Live chỉ thấy file trong thư mục work/. Thư mục work/store/_sys/ do server tự tạo (log, phiên bản, ghi chú).
"""


def copy_tree(src, dst):
    for d, dirs, files in os.walk(src):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        rel = os.path.relpath(d, src)
        os.makedirs(os.path.join(dst, rel), exist_ok=True)
        for f in files:
            if f.endswith((".pyc", ".log")):
                continue
            shutil.copy2(os.path.join(d, f), os.path.join(dst, rel, f))


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n" if not path.endswith(".bat") else "\r\n") as f:
        f.write(text)


def map_rows():
    """Các dòng Spine trong MAP.md -> docs/SPINE_MAP.md."""
    try:
        lines = open(os.path.join(ROOT, "MAP.md"), encoding="utf-8").read().splitlines()
    except OSError:
        return "(không có MAP.md)\n"
    keep = [l for l in lines if l.startswith("|") and re.search(r"spine", l.split("|")[1] if "|" in l[1:] else "", re.I)]
    return "# Bản đồ tool Spine\n\n| File | Mô tả |\n|---|---|\n" + "\n".join(keep).replace(".claude/skills/", ".agents/skills/") + "\n"


def main():
    args = sys.argv[1:]
    date = time.strftime("%Y%m%d")
    base = os.path.join(ROOT, "work", "_pack")
    if "--out" in args:
        base = args[args.index("--out") + 1]
    name = f"spinelive_codex_{date}"
    out = os.path.join(base, name)
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)

    for rel in COPY:
        src = os.path.join(ROOT, rel)
        dst = os.path.join(out, rel)
        if os.path.isdir(src):
            copy_tree(src, dst)
        else:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)

    sk = os.path.join(out, ".agents", "skills")
    for s in SKILLS:
        copy_tree(os.path.join(ROOT, ".claude", "skills", s), os.path.join(sk, s))
        p = os.path.join(sk, s, "SKILL.md")
        t = open(p, encoding="utf-8").read()
        m = re.match(r"(---\n.*?\n---\n)", t, re.S)     # chèn ghi chú sau phần đầu (name / description)
        t = (m.group(1) + "\n" + SKILL_NOTE + t[m.end():]) if m else SKILL_NOTE + t
        t = t.replace(".claude/skills/", ".agents/skills/")
        write(p, t)
    write(os.path.join(sk, "spinelive", "SKILL.md"), SPINELIVE_SKILL)

    write(os.path.join(out, "AGENTS.md"), AGENTS_MD.format(date=time.strftime("%Y-%m-%d")))
    write(os.path.join(out, "setup.bat"), SETUP_BAT)
    write(os.path.join(out, "start_spine_live.bat"), START_BAT)
    write(os.path.join(out, "codex_config_example.toml"), CODEX_TOML)
    write(os.path.join(out, "work", "README.txt"), WORK_README)
    write(os.path.join(out, "docs", "SPINE_MAP.md"), map_rows())

    zp = out + ".zip"
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for d, _, files in os.walk(out):
            for f in files:
                full = os.path.join(d, f)
                z.write(full, os.path.join(name, os.path.relpath(full, out)))
    n = sum(len(f) for _, _, f in os.walk(out))
    print(f"gói: {out}\nzip: {zp} ({os.path.getsize(zp) // 1024} KB, {n} file)")


if __name__ == "__main__":
    main()
