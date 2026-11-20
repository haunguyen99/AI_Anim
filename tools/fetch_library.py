#!/usr/bin/env python3
"""Tải thư viện texture VFX (Assets/Library) từ Google Drive về đúng vị trí.

Asset Unity không nằm trong git, nên sau khi clone nhánh VFX chạy:

    python -I tools/fetch_library.py            # thiếu thì tải, đủ rồi thì bỏ qua
    python -I tools/fetch_library.py --force    # tải lại, ghi đè
    python -I tools/fetch_library.py --dry-run  # chỉ báo sẽ làm gì

Nguồn: thư mục Drive chứa `Library.tar.gz` (đường dẫn trong file bắt đầu bằng
`Library/`, kèm .meta giữ GUID) -> giải nén vào `<gốc project>/Assets/`.
Cần `gdown` (tự cài bằng pip nếu thiếu). Giải nén an toàn: từ chối đường dẫn
tuyệt đối / `..` / link.
"""
import argparse
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

FOLDER_URL = "https://drive.google.com/drive/folders/1Yar5LDgR5drwZ2-1LaOi-xHExtbJHMVm"
ARCHIVE = "Library.tar.gz"
ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "Assets"
TARGET = ASSETS / "Library"


def have_library():
    return TARGET.is_dir() and any(TARGET.rglob("*.png"))


def ensure_gdown():
    try:
        import gdown  # noqa: F401
    except ImportError:
        print("Cài gdown ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "gdown"])
    import gdown
    return gdown


def safe_members(tar):
    for m in tar.getmembers():
        p = Path(m.name)
        if p.is_absolute() or ".." in p.parts or m.issym() or m.islnk() or m.isdev():
            raise SystemExit(f"File nén có mục không an toàn: {m.name}")
        if p.parts[0] != "Library":
            raise SystemExit(f"Mục ngoài Library/: {m.name}")
        yield m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="tải lại và ghi đè")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if have_library() and not a.force:
        print(f"Đã có {TARGET}, bỏ qua (dùng --force để tải lại).")
        return
    if a.dry_run:
        print(f"Sẽ tải {ARCHIVE} từ {FOLDER_URL}\nvà giải nén vào {ASSETS}/ (-> {TARGET})")
        return

    gdown = ensure_gdown()
    with tempfile.TemporaryDirectory() as tmp:
        gdown.download_folder(url=FOLDER_URL, output=tmp, quiet=False)
        arc = Path(tmp) / ARCHIVE
        if not arc.is_file():
            raise SystemExit(f"Không thấy {ARCHIVE} trong thư mục Drive.")
        ASSETS.mkdir(exist_ok=True)
        with tarfile.open(arc, "r:gz") as tar:
            tar.extractall(ASSETS, members=safe_members(tar))
    n = sum(1 for _ in TARGET.rglob("*.png"))
    print(f"Xong: {n} ảnh png trong {TARGET}")


if __name__ == "__main__":
    main()
