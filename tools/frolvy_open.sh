#!/usr/bin/env bash
# Mở file .fv trong Frolvy trên Linux (Mint). Dùng: tools/frolvy_open.sh "<đường dẫn .fv>"
# Frolvy chưa có lệnh mở file từ cầu nối trên Linux; chạy AppImage kèm đường dẫn thì mở ra một cửa sổ mới,
# tự lấy cổng MCP kế tiếp còn trống (9877 bận -> 9878...). Không đụng cửa sổ đang mở.
set -e
f="$1"
[ -f "$f" ] || { echo "Không thấy file: $f"; exit 1; }
APP="$HOME/Applications/Frolvy-0.9.69-x86_64.AppImage"
nohup "$APP" --no-sandbox "$f" >/tmp/frolvy_open.log 2>&1 &
name="$(basename "$f")"
for _ in $(seq 1 20); do
  sleep 1
  line="$(wmctrl -l | grep -F "$name" | grep -i frolvy || true)"
  [ -n "$line" ] && { echo "$line"; exit 0; }
done
echo "Chưa thấy cửa sổ $name sau 20 s (xem /tmp/frolvy_open.log)"; exit 1
