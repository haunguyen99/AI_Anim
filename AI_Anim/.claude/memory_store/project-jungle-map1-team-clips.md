---
name: project-jungle-map1-team-clips
description: Jungle (map1, cao bồi + súng, MC_char_map1) clip của team trong MC_char_map1_shoot.fbx là 24 fps; tách thành jungle_* trong Studio; GSDR-1497 Reload
metadata:
  type: project
---

Unity `Animations/Jungle/MC_char_map1_shoot.fbx` (team) gộp Sling_Shoot F0-15, Pump F15-30, Idle F31-40, Reload F43-57 theo **24 fps** (key cách 1.25 frame ở thang 30). Đọc bằng `rig.frame_of(A, f, 24)`, đăng ký POSES fps 24; dùng 30 sẽ cắt sai cửa sổ (lỗi 2026-11-05, đã sửa). Nhân vật Studio `Jungle` (tạo bằng fbx_import.new_char từ MC_char_map1_Rig.fbx, KHÔNG phải SDR01 con ném dao), clip `jungle_sling_shoot|pump|idle|reload` version `team`. Script ở `work/shoot_die_repeat/sdr01/_reload/`.

Đo: nòng súng 0° lệch so Idle suốt Reload; Pump chỉ tay trái + tay phải giật nhẹ, thân đứng im; Idle F31-40 hoàn toàn tĩnh. Controller: Reload ở Upper Layer, vào bằng Reload/ReloadNextShell.

**Why:** GD Thịnh (GSDR-1497) yêu cầu Reload không đổi hướng nòng; chưa rõ GD thấy nòng đổi chỗ nào. **How to apply:** hỏi user trước khi sửa; không dùng ik_arm, xem [[project-sdr06-reload-gun-f1]].

**Cập nhật 2026-11-06:** user duyệt `polish`. Reload dựng lại 30F (`reload30b.py`: cầm ốp súng → xuống túi lấy đạn → nâng → lắp (nòng chúi 1,4° tắt dần) → về ốp súng như Idle; bullet = xương slingshot_2) + polish đầu/cổ (`polish.py`); Pump polish gật đầu; Sling_Shoot/Idle = headfwd (đầu ngửa sau <=2°, góp ý Studio). FBX xuất ở `work/shoot_die_repeat/sdr01/jungle_export/MC_char_map1_<Clip>.fbx` bằng fbxwrite với `FPS=24, DT=46186158000//24` (tham số mới); CHƯA đẩy Unity (file team MC_char_map1_shoot.fbx gộp 4 clip, controller trỏ guid đó: thay thế cần user xác nhận). Controller blend Aim→Reload = 0 (lỗi của team, đã báo).

**Đẩy Unity 2026-11-06:** user chọn cách 2 (4 file riêng, không đụng file team). Commit `fef3a551` lên TungNV_Dev (temp index): `Animations/Jungle/MC_char_map1_{Sling_Shoot,Pump,Idle,Reload}.fbx` + meta tối thiểu. Chưa gắn vào controller (team làm). Checkout cục bộ E:/Horus/shot-die-repeat đang lệch 8f385ac0, dirty — chưa merge.

**Bài học 2026-11-06 (Unity báo "Copied Avatar Rig mismatch: Transform 'Root_M' for human bone 'Hips' not found"):** anim FBX phải có cùng cây xương với Base. Rig team Jungle KHÔNG có nút Armature (root là gốc) → xuất bằng `fbxwrite.ARMATURE=False, FPS=24, DT=46186158000//24`; meta dựng bằng `_reload/make_meta.py` từ meta team (Humanoid, avatar nguồn = MC_char_map1_Base 22bcb4d6…). SDR06 thì Base có Armature nên giữ Armature. Đã đẩy lại TungNV_Dev.

**Cách xuất đúng (2026-11-06, thay fbxwrite cho Jungle):** `_reload/export_team.py` lấy FBX team (`MC_char_map1_shoot.fbx`) làm khuôn, thay curve bằng pose, bỏ mesh (đường Western/Gatling) → có `root` + PreRotation y như rig team; fbxwrite (không PreRotation, nút khác) làm Unity báo thiếu Hips/root. Pose đọc từ `jungle_export/_fbxwrite/`. Frame 0..N-1, meta firstFrame 0. Đã đẩy TungNV_Dev.
