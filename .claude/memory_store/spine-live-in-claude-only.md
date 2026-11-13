---
name: spine-live-in-claude-only
description: "Spine Live chỉ mở trong khung trình duyệt của Claude (show_pane preview), không mở / không đưa link ra Chrome"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 7a2ac033-b389-4c9d-92bc-a3517d3d0b0d
  modified: 2026-11-06T05:30:37.407Z
---

Mở Spine Live (http://127.0.0.1:8781/spine?json=...) chỉ trong khung trình duyệt của app Claude: `navigate` tab có sẵn hoặc `preview_start {url}`, khung bị ẩn thì tự gọi `mcp__ccd_view__show_pane {pane: "preview"}`. Không mở bằng Chrome / `Start-Process`, không đưa link bảo người dùng tự mở ngoài.

**Why:** người dùng 2026-11-05: "mở spinelive ngay trong claude, lưu vào luật, chỉ mở trong claude, không đẩy ra ngoài chrome" (sau khi Claude đưa link Chrome lúc khung bị ẩn).

**How to apply:** mọi lần cần cho người dùng xem / duyệt rig, anim Spine; liên quan [[spine-feedback-scope]].

**Ngoại lệ VS Code (2026-11-06):** Claude Code trong VS Code không có `preview_start`. Khi đó tự bật server bằng `Start-Process` (không dùng start.bat vì nó mở Chrome) và đưa link `127.0.0.1` để người dùng bấm: `.vscode/settings.json` đặt `workbench.browser.openLocalhostLinks: true` nên link mở trong trình duyệt tích hợp của VS Code, không ra Chrome. Chi tiết ở skill `/spinelive`, `/studio`.
