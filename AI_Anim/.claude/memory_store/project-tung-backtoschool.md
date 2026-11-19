---
name: project-tung-backtoschool
description: "Order Tùng 2026-11-13: idle + active 2D Spine cho mascot cừu Back to School (6 bóng bay), 5 vòng góp ý, Hậu duyệt, zip giao gửi Tùng; bài học chuyển active -> idle, bóng + dây physics"
metadata:
  node_type: memory
  type: project
  originSessionId: 8d351cb2-9304-4788-954d-f311f18a2cd5
  modified: 2026-11-13T07:33:39.911Z
---

Tùng (ArtAnimVFX, thread "2d anim backtoschool") order idle + active cho `Mascot_Backtoschool.psd` (871x1275, 32 layer tách sẵn: 6 bóng gồm dây + cừu cầm dây + balo). Làm ở `work/_inbox/tung-backtoschool/`: `psd_extract.py` (tự đọc PSD), `spine/build_rig.py` (45 xương + mesh weight), `idle_cfg.py`, `active_cfg.py`, `smooth_tail.py`, `render_demo.py` (xem trước vá slot / noScale), demo `demo_v1..v5.mp4`, `active_v5.mp4`, bản giao `giao/` + `Mascot_Backtoschool_giao.zip` (1.8 MB: .spine + export JSON / .atlas.txt / PNG). Hậu duyệt "Oki rồi" 2026-11-13, zip gửi Tùng.

**Why:** Tùng chốt: ctrl tổng ở bóng + dây rồi xương kéo xuống người; idle lơ lửng nhẹ, mọi vật overlap, nhịp lệch nhau; active bay nhẹ lên + lắc 1 lần như gió. Góp ý đi qua lễ tân (Hậu): active v1 "chưa ổn" → bay cao hơn + một thùy gió → lắc cuối mạnh + thân dưới đứt rời → quần dính hông → "khựng" khi chuyển active -> idle (4 lượt) → tách 2 anim, chỉ playblast active → duyệt.
**How to apply (bài học):**
- Chuyển active -> idle: đo tốc độ đầu xương (px / frame) 30F cuối; lỗi là dừng rồi bật lại ở tay / chân. Sửa: đường hạ giảm dần, BLEND rộng, giảm chấn cao, bỏ chain tay, `smooth_tail.py` với `SMOOTH_SIG=5.5` (chi tiết skillactive mục 4b).
- Bóng + dây = chain physics 3 xương, wind amp ~18 (200 → ±70° văng); active giảm wind 0.3x, zeta 0.5-0.65, lim 28-40°.
- "Bay nhẹ" đo theo % chiều cao nhân vật: 90 px / 1275 px không thấy; dùng 150.
- Quần dính hông: mesh có `fade` (xương chân mất weight dần khi lên gần hông), không đưa body2 vào chain physics.
- Demo: video số frame tự ghi (30 fps, đếm từ 1), nêu mapping idle / active; không `--sync`. Bản giao chỉ idle + active (lọc mix); chưa test runtime Spine thật (Spine Live chưa mở), chỉ kiểm bằng Spine CLI + dựng lại ảnh.
- pip bị chặn trong phiên con: tự viết tool (psd_extract.py), không cài thư viện.
- Liên quan [[project-tung-rateus-idle]], [[reference-horuschat-mcp]], [[reference-subsession]].
