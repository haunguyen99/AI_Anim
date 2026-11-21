# VFX_FireballLoop — kế hoạch v1 (đã duyệt 2026-10-21)
Pipeline: Built-in · Loop đứng yên · Thân ~1 m, ngọn lửa ~2.2 m · Painterly bám ảnh tham chiếu · Camera 3/4 nhìn xuống

| # | Layer | Vai trò | Texture |
|---|---|---|---|
| 1 | Aura_Glow | quầng đỏ-tím, thở chậm | T_Glow_Soft (script glow) |
| 2 | Body_Outer | viền tím/đỏ | T_Fire_Flipbook_4x4 (script fire) |
| 3 | Body_Mid | thân cam | T_Fire_Flipbook_4x4 |
| 4 | Core_Hollow | lõi tối xoáy | T_Fire_Blob_2x2 (script fireblob) |
| 5 | Core_Light | điểm sáng + lấp lánh | T_Glow_Soft, T_Star_Glint |
| 6 | Tongues | lưỡi lửa bốc lên | T_Fire_Tongue_2x2 (script fire) |
| 7 | Embers | tàn lửa lơ lửng | T_Ember_Chunk (script ember) |

Bảng màu: #4A1030 · #C8281E · #FF7A1F · #FFC93C · #FFF1B0 · lõi tối #2A0E1C
Ngân sách: ~38 particle, 4 material, texture ≤ 512. Toàn bộ texture sinh bằng script.
