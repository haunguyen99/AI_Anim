---
name: reference-paseo-linux-launcher
description: Paseo trên máy Linux của ngocvb chỉ dùng bản AppImage 0.16.x; lối tắt Desktop/menu phải trỏ AppImage và không có --gtk-version=3
metadata:
  type: reference
---

Máy Linux ngocvb (2026-11-19): chỉ giữ Paseo AppImage `~/Applications/Paseo-x86_64.AppImage` (0.16.2), lệnh `paseo` = symlink `~/.local/bin/paseo` tới file đó. Bản `.deb` 0.15.4 (`/opt/Paseo`) đã gỡ bằng `pkexec apt-get remove paseo`; không cài lại.
- Lối tắt `~/.local/share/applications/Paseo.desktop` + `~/Desktop/Paseo.desktop`: Exec = `env GTK_IM_MODULE=ibus QT_IM_MODULE=ibus XMODIFIERS=@im=ibus <AppImage> %U`, Icon `~/.local/share/icons/paseo.png`.
- **Bẫy:** bản 0.16.x không biết `--gtk-version=3` (báo "unknown option" rồi thoát ngay → bấm biểu tượng không lên, Terminal vẫn chạy). Đừng thêm lại.
- Không tắt Paseo đang chạy khi chưa được phép (phiên Claude nằm trong đó). Không có sudo: dùng `pkexec` (hiện hộp mật khẩu cho user).

**Why:** bản cũ + bản mới chạy song song làm lối tắt trỏ nhầm, user phải mở bằng Terminal.
**How to apply:** nếu user báo Paseo không mở bằng biểu tượng, chạy thử đúng dòng Exec trong Terminal rồi đọc lỗi. Liên quan [[reference-paseo]].
