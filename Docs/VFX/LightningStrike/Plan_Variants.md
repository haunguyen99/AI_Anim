# LightningStrike: biến thể Toxic và Frost (2026-11-09)

Cùng hiệu ứng với bản gốc (sét đánh xuống một điểm đất; recipe 3 thành phần cốt lõi trong `.claude/skills/vfx-shader/references/thunder-core.md`: line_impact cột sáng, wave vòng nền, flare chớp lõi, setup y hệt, texture giữ nguyên). Không gian như `Plan.md`: ground, một điểm đánh, camera top-down 60° cách 22 m, cột cao ~25 m, vòng / nứt ~12-24 m, nằm đất = Billboard + Local (X ±90), mọi Particle System Hierarchy, root là Particle System (flare), mọi transform scale 1. Chưa build trong Unity (đang mở); chạy menu rồi xem `Docs/VFX/LightningStrike_<Tên>/Preview_sheet.png`.

## LightningStrike_Toxic (xanh độc)
Menu `VFX/LightningStrike/Build Toxic`, prefab `VFX_LightningStrike_Toxic`. Khác bản gốc ở 3 trục:
- **Bố cục:** cột chính hẹp hơn (12,5 x 25) + hai nhánh nghiêng ±18° (8 x 16, lệch x ±1,4 m, trễ 0,04 / 0,08 s).
- **Timing:** 3 nhịp cột (t = 0 / 0,12 / 0,3 s) thay vì 2; wave nhịp 0 và 0,6 s, vòng 22 m; vũng độc lan ra và tồn tại ~2,8 s.
- **Lớp phụ:** ToxicPool (vũng sáng xanh lan), bubbles (bong bóng độc nổi lên 1,5-3,5 m/s), nứt đất = mạng rễ xanh (Library `ground_crack_radial_010`) thay nứt vàng, cung điện ít hơn và xanh.
Màu: cột `(0.2,1,0.15)..(0.7,1,0.45)`, gradient trắng → `(0.75,1,0.55)` → `(0.1,1,0.5)` → trắng.

## LightningStrike_Frost (băng xanh-trắng)
Menu `VFX/LightningStrike/Build Frost`, prefab `VFX_LightningStrike_Frost`. Khác bản gốc ở 3 trục:
- **Bố cục:** MỘT cột rộng và thấp hơn (22 x 16 thay vì 17,5 x 25), vòng nhỏ 24 m.
- **Timing:** một nhịp duy nhất (cột, wave), rồi mặt đất đóng băng: nứt băng, vũng sáng và sương tồn tại ~3 s (gốc: nứt 1 s, 2 nhịp).
- **Lớp phụ:** bỏ cung điện; thêm sương thấp màu xanh (khói mặc định `fx_t_smoke_02` + shader Alpha Blended mặc định, tô bằng Start Color) và các tia lấp lánh băng (sao 4 cánh) rơi chậm.
Màu: cột `(0.35,0.85,1)..(0.85,0.97,1)`, gradient trắng → `(0.8,0.95,1)` → `(0.3,0.7,1)` → trắng; flare `(0.8,0.96,1)`.
