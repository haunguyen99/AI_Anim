#!/usr/bin/env bash
# Cài môi trường cho Linux / macOS (như tools/setup.ps1 trên Windows). Chạy ở thư mục gốc dự án:  bash tools/setup.sh
# Tạo .venv, cài thư viện (có psd-tools đọc PSD, scipy cho anim active), tạo lối tắt .venv/Scripts/python.exe
# để mọi lệnh trong CLAUDE.md / skill chạy y như trên Windows.
set -e
cd "$(dirname "$0")/.."
PY=${PYTHON:-python3}
if [ ! -x .venv/bin/python ]; then
  rm -rf .venv
  if ! "$PY" -m venv .venv; then
    rm -rf .venv
    echo
    echo "Python này không tạo được venv (Ubuntu / Debian thiếu gói python3-venv)."
    echo "Cách 1: sudo apt install python3-venv   rồi chạy lại  bash tools/setup.sh"
    echo "Cách 2: dùng Python khác có venv:  PYTHON=/đường/dẫn/python3 bash tools/setup.sh"
    exit 1
  fi
fi
.venv/bin/python -m pip install -q --upgrade pip
.venv/bin/python -m pip install -q -r requirements.txt
mkdir -p .venv/Scripts
ln -sf ../bin/python .venv/Scripts/python.exe
.venv/Scripts/python.exe -I -c "import cv2, numpy, PIL, psd_tools, scipy; print('thu vien OK')"
[ -f tools/claude_memory.py ] && .venv/Scripts/python.exe -I tools/claude_memory.py restore --if-empty || true
echo "Xong. Bật Spine Live: bash tools/spine_live/start.sh"
