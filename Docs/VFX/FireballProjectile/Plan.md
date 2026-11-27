# VFX_FireballProjectile — kế hoạch v1 (đã duyệt 2026-10-19)

Pipeline: Built-in · Loop, gắn lên projectile, hướng bay +Z · Quả cầu ~0.8 m, đuôi ~1.5–2 m · Anime/cel-shaded · Camera game: 3/4 nhìn xuống

| # | Layer | Vai trò | Kỹ thuật | Material / Shader | Texture |
|---|---|---|---|---|---|
| 1 | Flame_Outer | viền đỏ sẫm, silhouette | 14/s, flipbook 3×3, xoay ngẫu nhiên, trôi nhẹ về sau | M_FireballProjectile_Flame_Alpha · Mobile/Particles/Alpha Blended | T_Fire_Blob_3x3 |
| 2 | Flame_Mid | thân cam | như #1, nhỏ hơn | dùng chung #1 | T_Fire_Blob_3x3 |
| 3 | Flame_Inner | lõi vàng | như #1, nhỏ nhất | M_FireballProjectile_Flame_Add · Mobile/Particles/Additive | T_Fire_Blob_3x3 |
| 4 | Core | đốm trắng-vàng, pulse | 1 particle loop | M_FireballProjectile_Core_Add · Mobile/Particles/Additive | T_Glow_FatDot |
| 5 | Tongues | lưỡi lửa phía sau | stretched billboard về −Z, flipbook 2×4 | M_FireballProjectile_Tongue_Alpha · Mobile/Particles/Alpha Blended | T_Fire_Tongue_2x4 |
| 6 | Embers | tàn lửa | World space, 2×2 random frame, noise | M_FireballProjectile_Ember_Add · Mobile/Particles/Additive | T_Ember_Chunk_2x2 |

Bảng màu: #B3141A → #FF6A1A → #FFD34D → lõi #FFF6CC. Ngân sách ~45 particle, 5 material, texture ≤ 512.

Giả định: layer 1–5 Local space; chưa có ribbon trail; demo đứng yên.

## Nguồn asset (thư viện D:\Projects\animlibrary\Assets\VFX_Library\Textures)

| Asset trong project | Nguồn |
|---|---|
| T_Fire_Blob_3x3.png | cfxr fire small anim.png (3×3, 8 frame) |
| T_Fire_Tongue_2x4.png | Flipbooks/Hun0FX/Tx_Fire_directional_13.png (2 cột × 4 hàng) |
| T_Ember_Chunk_2x2.png | Flipbooks/Hun0FX/Tx_Ember_01.png (4 biến thể) |
| T_Glow_FatDot.png | Flare_FatDot.png |
