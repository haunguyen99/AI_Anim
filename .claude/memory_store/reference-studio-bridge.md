---
name: reference-studio-bridge
description: Control the open Studio page via tools/studio_cmd.py (bridge through Home server) instead of browser tools
metadata:
  node_type: memory
  type: reference
  originSessionId: 98415810-dce9-4d70-8e09-d4120141ccff
  modified: 2026-10-27T11:40:38.015Z
---

`.venv/Scripts/python.exe -I tools/studio_cmd.py <lệnh>` gửi lệnh có tên tới trang Studio đang mở (Chrome của user hoặc trình duyệt trong app) qua server Home :8780 (`tools/home/studio_bridge.py`, trang `tools/studio/modules/bridge.js`). Lệnh: state, vis <mesh|*> on|off|toggle, select mesh|joint <tên>|none, joint <tên> --r x,y,z --t … --s …, bindpose, ws, run <id lệnh>, open <nhân vật>, clients; W1: focus, layer, cmds; W2 (2026-10-28): undo/redo/save, view, snap [file] (ảnh viewport tự kiểm), rig lms|lm|sel|step, anim info|joints|read|select|frame|play|rot (độ, local; --abs)|pos (cm Blender)|key|unkey|versions|version — rig/anim tự focus + chờ lõi nạp; lõi Pose API = engine.ai sinh trong port_pose.py. Gom nhiều lệnh bằng `";"`. Không có eval (hệ thống chặn bề mặt chạy mã tuỳ ý). Thiếu lệnh thì thêm vào OPS trong bridge.js.

Đo 2026-10-27: trong trang 2–5 ms; một lệnh lẻ ~160 ms (khởi động Python), curl ~60 ms; công cụ trình duyệt cũ ~170–340 ms và chỉ chạy trong app. Server Home phải chạy bản mới (khởi động lại sau khi sửa server.py). Liên quan [[project-studio]], [[feedback-screenshot-on-request]].

**2026-10-28 test run:** several Studio pages can be connected (user's own browser + the preview tab); without `--cid <id>` commands go to the most recently visible page, which may be the user's real page — list with `clients`, pass `--cid` when testing on a `?ns=studio_test_*` page. `snap` works with the pane hidden (renders 1280×720 offscreen). `anim clips` / `anim clip <id>` switch anim (page reloads).
