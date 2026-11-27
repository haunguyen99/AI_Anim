---
name: project-pirate-wars
description: "Dự án Unity Pirate-wars nằm ở /home/haunv/Documents/Project/pirate-wars (máy Linux), có AGENTS.md + CONTEXT.md + Docs"
metadata:
  node_type: memory
  type: project
  originSessionId: 261c2070-e4a4-427e-bba8-8f044e8e5112
  modified: 2026-11-20T04:37:42.048Z
---

Dự án game **Pirate-wars**: Unity project tại `/home/haunv/Documents/Project/pirate-wars` (user báo 2026-11-20). Gốc có `AGENTS.md`, `CONTEXT.md`, `Docs/`, `Assets/`.

**Why:** đích giao anim/VFX cho game này; khác với nhánh SDR Pirate (map4 bạch tuộc) [[project-pirate-reload]].

**How to apply:** trước khi đụng Unity, đọc `AGENTS.md` và `CONTEXT.md` của repo; chưa rõ có commit/push được không thì hỏi (xem [[feedback-runner-hybrid-no-commit]] làm ví dụ về repo cấm commit).

**Tàu ship_202_new (2026-11-20):** rig 14 joint (Root_M + buồm A/B + cờ + buồm mũi) trong Frolvy, anim Idle 90F loop (v4 duyệt). Review Lab: project `pirate_wars`, clip `ship202_idle`, file ở `work/pirate_wars/ship202_idle/`. Đã chép `Ship_202_Rig.fbx` + `Ship_202_Rig@Idle.fbx` (+.meta, Generic) vào `Assets/3D_kho/Ship/Playable/`, chưa kiểm import trong Unity, không động prefab `_Game/Prefabs/ShipSkins/s_0202.prefab`.
**Bài học:** Frolvy export mặc định nhị phân → dùng `fbx_ascii`; FBX Frolvy ghi UnitScaleFactor 1 nhưng mét → đổi 100 cho khớp FBX team; Base cần export ở pose nghỉ (xóa key, trả rest) mới qua `fbx_add_bindpose`; cờ sóng lan cần key từng frame; Linux: dùng `python3 -I`, không có numpy.

**Tàu 202 Move (2026-11-20):** clip Move 60F loop (Hậu duyệt qua demo v2 Idle→Move→Idle) + `Ship_202_Rig@Move.fbx`, controller `Ship_202_Idle.controller` = 1 state Locomotion (blend tree 1D `Speed01`, Idle ngưỡng 0.05, Move 0.75), code `Ship/Reaction/ShipMoveAnimationDriver.cs` (Speed01 từ `NormalizedSpeed` + xoay yaw `Flag1` theo `Wind.Instance.DirectionXZ` ở LateUpdate). Chưa thử trong Play. File: `work/pirate_wars/ship202_move/`; scene `Ship_202_new_rig_v5_move.fv`.
**Bài học:** `clip_registry.py new Ship202 Move` ghi review.clip = "Move": sửa tay thành `Ship202_Move` trong clips.json (khớp `CLIPS` index.html) rồi chạy `work/review_page/split_pages.py`, không thì trang không có version; ảnh/webm truy cập qua `/work/review_page/clips/`. Frolvy `open_scene` trả False nếu cảnh dirty: `save_scene` trước; không `save_scene` lên v4 (đổi byte). Playblast Frolvy Linux ~5 s/frame (150F > 13 phút, đặt timeout 900). UnitySkills không có blend tree: ghi YAML controller tay (BlendTree `!u!206`), fileID clip lấy bằng cách `animator_add_state` với clipPath rồi đọc YAML.
**Tàu 202 chốt Move + Idle v6 (2026-11-20):** Hậu duyệt sau khi tăng độ căng Move (buồm lớn/trên/mũi +30/+25/+23 cm tz so với gốc) và giảm phồng Idle (v6: buồm lớn −7, trên −7, mũi −5 cm; `Ship_202_new_rig_v6_idle.fv`, Idle v4 gốc backup ở `ship202_idle/export_v6/..._v4_backup.fbx`). Ngưỡng blend Idle 0.05 → Move 0.5. Camera game từ xa nên anim phụ (buồm) phải làm đậm hơn so với xem trong Frolvy. Cách so sánh hai trạng thái: áp pose Idle lên cảnh Move bằng set_attr, chụp viewport, rồi `undo` (cùng camera scene).
**Phản hồi anh Cường (2026-11-20):** buồm tam giác (Jib, buồm mũi) phải cố định, chạy dọc dây thừng như buồm to, không lắc lư → Jib rx/ry chỉ còn ~15–20%, Jib2.tz 0.35 (Idle v7) / 0.40 (Move). Cờ sóng uốn S: trễ pha ~110°/đốt, xoắn rz, 8 chu kỳ/60F. Gió: object `Wind` trong PW_Gameplay đang TẮT (m_IsActive 0), driver dùng hướng dự phòng (1,0,1). Bẫy: `open_scene` trả False khi scene dirty, rồi `save_scene` ghi cảnh cũ sang tên mới → luôn kiểm `list_instances` scene_path sau khi mở; sửa bản Idle phải kiểm SailA2.tz/frame_range đúng bản.
