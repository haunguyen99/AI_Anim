---
name: project-pirate-reload
description: Pirate (SDR map4, bạch tuộc + súng hoả mai) Reload dựng lại 30F nòng giữ (GSDR-1497), version Studio polish_c (túi sau hông, đạn cầm ngang) USER DUYỆT + đẩy TungNV_Dev b3e69db8 2026-11-06
metadata:
  type: project
---

Pirate Reload (Studio `pirate_reload`, team = MC_char_map4_shoot F41-60) dựng lại theo khuôn Jungle [[project-jungle-map1-team-clips]]: `r30` → `polish` (2026-11-06), script `work/shoot_die_repeat/sdr04/_reload/` (reload30.py, polish.py, check.py, PHAN_TICH.md, director_log.md). Director duyệt vòng 2. Nạp đạn ở "khoang" +14 cm trước khoá (cheat, miệng nòng ngoài tầm tay), túi thắt lưng trước (phía cam phải), đạn joint27 kẹp đầu ngón cao ~9 cm trên súng; râu xúc tu né tay. Bỏ kéo búa: joint26 là cả miếng khoá súng (cần modeler tách búa nếu muốn).

**Why:** GD Thịnh GSDR-1497: Reload không đổi hướng nòng; user duyệt PHAN_TICH (30F, khoang, túi trước, kéo búa). **How to apply:** chờ user duyệt trong Studio; chỉ xuất FBX / đẩy Unity khi user bảo, theo cách `sdr01/_reload/export_team.py` (khuôn FBX team map4, Humanoid, avatar Base map4). Model Pose Lab clip 24 fps phải đặt `PM.FPS = 24` (mặc định 30 làm Studio chiếu nhanh 1,25x).

**Sửa 2026-11-06:** user "tay lấy đạn cần đưa ra sau" → `r30b`/`polish_b`: túi (25,90,17) hông trái chếch sau, ngoài vạt áo; director duyệt. Bản túi trước bụng còn ở `polish`.
**Sửa 2 (2026-11-06):** ghi chú Studio F16 "viên đạn cần cầm ngang" → `r30c`/`polish_c`: đạn dọc súng, mũi trước, ngóc 15°, phẳng khi chạm khoang.
**Duyệt 2026-11-06:** user "oki rồi" cho `polish_c`. Việc tiếp: xuất FBX + đẩy Unity chỉ khi user bảo.
**Đẩy 2026-11-06:** `Assets/_Game/Animations/Pirate/MC_char_map4_Reload.fbx` + meta, commit b3e69db8 (xuất `sdr04/_reload/export_pirate.py`, file ở `sdr04/pirate_export/`). Meta: avatarSetup 2 copy avatar từ MC_char_map4_shoot (guid 3c529820…) vì prefab dùng avatar đó và Base map4 là animationType None. Chưa gắn controller.
**Sửa Unity 2026-11-06:** đạn bay ngang người giữa F7-F8 trong preview Unity → a9d57887: key đổi chỗ tức thì + resampleCurves 0. User xác nhận hết bay → XONG.
