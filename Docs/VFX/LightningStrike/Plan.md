# LightningStrike – sét đánh xuống (bản 3, 2026-11-04)

Dựng đúng 3 thành phần cốt lõi của rpg-game Thunder (art lead chốt): line_impact (cột sáng vàng), wave (vòng nền), flare (chớp lõi): setup y hệt, số liệu trong `.claude/skills/vfx-shader/references/thunder-core.md`. Texture được phép thay bằng texture cùng thuộc tính (hằng `Tex*` đầu `LightningStrikeBuild.cs`).
Lớp phụ như mẫu: nứt đất toả tròn, cung điện trắng (electric_remain). Cấu trúc: `VFX_LightningStrike` (root là Particle System = flare) → Cracks, line_impact, wave, electric_remain; không nhóm scale, mọi transform scale 1 (scale 0.5 của mẫu đã nhân vào size). Mọi Particle System Scaling Mode Hierarchy.
Bỏ so với bản 1–2: tia zig-zag, impact mix, vết cháy, ánh sáng nền (gây rối).
Không gian: ground, một điểm đánh, camera top-down 60°; cột cao 25 m, vòng/nứt ~15 m (kích thước của mẫu).
Build: VFX → LightningStrike → Build, rồi VFX → Showcase → Build Scene.
