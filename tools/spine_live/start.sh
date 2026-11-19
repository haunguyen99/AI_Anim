#!/usr/bin/env bash
# Mở Spine Live (server riêng 127.0.0.1:8781), Ctrl+C để tắt. Thêm --lan cho máy khác cùng mạng.
cd "$(dirname "$0")/../.."
[ -x .venv/bin/python ] || { echo "Chưa có .venv: chạy  bash tools/setup.sh  trước"; exit 1; }
(command -v xdg-open >/dev/null && (sleep 1.5; xdg-open http://127.0.0.1:8781/spine >/dev/null 2>&1) &) 
exec .venv/bin/python -I tools/spine_live/server.py "$@"
