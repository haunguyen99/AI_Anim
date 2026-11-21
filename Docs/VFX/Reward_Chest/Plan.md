# Reward_Chest — VFX nhận thưởng kiểu mở rương Clash Royale (2026-11-19)
Project đích: `real-war` (Unity 2022.3, Built-in). Prefab `Assets/VFX_Library/Prefab/VFX_Reward_Chest.prefab`; texture `Assets/VFX_Library/Texture/Reward/RW_*.png`; material `Materials/Reward/MAT_RW_*` (Mobile/Particles/Additive). Demo: `Assets/VFX_Library/Demo_VFX.unity` → `Canvas_RewardDemo` (UIParticle scale 140, Animator `RewardDemo.controller` loop 5 s). Dựng bằng `execute_code` qua Unity MCP (`RewardChestBuild.execute_code.cs.txt`).
Ref: video art lead (Clash Royale, mở rương Legendary, 10,6 s). Tạo hình gần `_Anatomy/reward-burst.md`, khác ở nhịp rương mở + pixel.

Không gian (đề xuất, chưa duyệt): billboard hướng camera / UI, tâm = thẻ thưởng (3×4 đơn vị), rương neo ở y −3,2; một lần ~3,2 s.
Nhịp: 0,10 rương mở (chớp xanh + 44 hạt pixel + cột sáng) → 0,45 quầng vàng quanh thẻ "?" + sao → 0,90 thẻ trắng dần + sao gai → 1,28 lật thẻ: chớp trắng, 8 tia nhiều màu, 2 vòng, sao nổ → 1,3–3,2 quầng tím-hồng (độ hiếm) + sao trôi.
Texture: sao/vòng/chớp/tia lấy lại từ StarDrop (đã duyệt, nguồn Library); mới vẽ PIL: `RW_CardGlow` (quầng chữ nhật mềm), `RW_CardShape` (thẻ trắng), `RW_Pixel` (ô vuông, Point filter).
Đã xem Play mode (timescale 0,2): `Play_montage.jpg`; mô phỏng edit mode: `Preview_sheet.jpg`. Chưa qua agent review / art lead.

## Sửa 1 (2026-11-19, art lead): bỏ đoạn rương mở
Bỏ `ChestAnchor` (chớp xanh, pixel, cột sáng). Thay bằng **tia hội tụ vào giữa**: `ConvergeRays` (Streak, Stretch, 4 đợt × 10 tia từ vòng r=7, bay vào tâm, 0,05–0,5 s) + `ConvergeGlow` (cầu xanh lớn dần). Các nhịp sau giữ nguyên (quầng 0,45 → thẻ trắng 0,9 → lật 1,28 → quầng tím). Demo: thẻ "?" xuất hiện lúc 0,45 s. Preview mới: `Preview_sheet.jpg`.

## Sửa 2 (2026-11-19, art lead): ánh sáng giữa bị cắt vuông
Nguyên nhân: `RW_CardGlow` / `RW_CardShape` có alpha còn khác 0 sát mép ảnh nên scale lớn + Additive lộ khung chữ nhật. Vẽ lại cả hai: hình mờ nhỏ hơn trong khung, nhân thêm cửa sổ smoothstep về 0 trước mép (alpha mép = 0 đã kiểm), bo góc lớn / mờ hơn; phóng to lại size (aura 6,2×7,8; rarity 7,6×9,5; card white 3,9×5,1). Luật thêm vào "Lỗi đã gặp" nếu art lead duyệt: ảnh glow chữ nhật phải về alpha 0 trước mép ảnh.

## Sửa 3 (2026-11-19, art lead): root prefab phải có ParticleSystem
Mọi prefab trong `VFX_Library/Prefab` (Gun_Hit, PisGun_Hit, Slash_Cavalry, SoldierFactory_Upgrade…) đều có `ParticleSystem` ở root (cụm chứa thì emission + renderer tắt). Bản đầu của `VFX_Reward_Chest` chỉ có Transform ở root. Đã thêm root ParticleSystem rỗng (duration 3,5 s, no loop, emission tắt, renderer tắt). Quy ước này lấy từ các prefab có sẵn, không tìm thấy luật viết ra trong `AGENTS.md` của real-war.

## Sửa 4 (2026-11-19, art lead): tia hội tụ lâu hơn
`ConvergeRays` 4 → 10 đợt (cách 0,1 s, 0,05–~1,3 s); `ConvergeGlow` sống 1,25 s. Mọi nhịp sau đẩy lùi **+0,7 s**: quầng vàng 1,15 → thẻ trắng 1,6 → lật thẻ **1,98 s** → quầng tím đến ~3,9 s. Tổng ~4,2 s; duration root 4,5 s. Demo: thẻ "?" lúc 1,15 s, lật 1,98 s, vòng lặp 5,7 s.
