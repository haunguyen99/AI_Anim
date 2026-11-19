---
name: project-tung-rateus-idle
description: "Order Tùng 2026-11-13: idle 2D RateUs_anim.psd (nhân vật cam + chong chóng + 3 sao), v2 loop 120F được duyệt, zip giao đã gửi; bài học dựng"
metadata:
  node_type: memory
  type: project
  originSessionId: a8ecaaa1-f400-4d83-9afe-0c4f2382f71d
  modified: 2026-11-13T04:45:04.881Z
---

Tùng (ArtAnimVFX, thread "2d anim") order idle cho `RateUs_anim.psd` (777x658). Làm ở `work/_inbox/tung_rateus_idle/`: `build_rateus.py` (rig từ layers/), `idle_cfg.py` (anim, engine skillidle), `preview/idle_v1|v2`, `RateUs_idle_giao.zip` (.spine + images + export JSON/atlas/PNG, 2 MB). v2 duyệt, zip gửi Tùng 2026-11-13 ~11:30.

**Why:** Tùng chốt: lơ lửng vẫy tay với sao, chong chóng lắc không quay, mắt không chớp, nền + mây tĩnh, sao lấp lánh nhẹ; sau demo v1 xin nhịp chậm hơn (90F -> 120F, 1 nhịp/loop, biên độ -20%) và sửa mesh chong chóng.
**How to apply (bài học):**
- Cắt chong chóng khỏi thân gộp: đáy cánh nằm dưới hàng cắt → dải thừa đứng yên ở mũ. Cắt phải theo hình (cánh vào prop), không theo một hàng pixel.
- ffmpeg libx264 cần chiều rộng chẵn (777 → crop 776). Gửi kèm GIF đúng kích thước.
- `render_spine.py` + `--png_dir` mất ~1-2 phút/120F khi máy rảnh; chồng nhiều tiến trình thì vài phút.
- Gửi file qua `horuschat_cli.py sendfile` (≤10 MiB, vào thread của Tùng, --mention); phiên con chỉ gửi khi Hậu nói rõ. Xuất bản giao: `export_spine.py --out <thư mục>` ghi thẳng vào thư mục đó, tự gói vào RateUs/{.spine, images, export}.
- Spine Live chưa mở nên chưa kiểm runtime thật; kiểm bằng dựng lại từ JSON export (lệch ~0,2/255). Liên quan [[reference-horuschat-mcp]], [[feedback-horuschat-thread-reply]].
