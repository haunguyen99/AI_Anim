# LightningTrail: biến thể Flame và Wind (2026-11-09)

Gốc: `Assets/VFX/LightningTrail/Editor/LightningTrailBuild.cs` (một lớp mesh `thunder_mesh2`, shader `Lightning_CustomBlend`, World space, đi 6 m theo X ở y 1, leg 2,4 s, `VfxPathMover` trên root).
Cả hai biến thể vẫn là cùng hiệu ứng: vật di chuyển để lại vệt phía sau (World space, root mang `VfxPathMover`, rate theo thời gian + theo quãng đường). Không gian: dir, camera 3/4 (40°), Billboard / Stretched Billboard, Scaling Mode Hierarchy, không scale. Texture từ `Assets/Library/` (copy vào `Assets/VFX/LightningTrail/Textures/`). Không dùng mesh, không dùng shader mới (Mobile/Particles/Additive).

## Flame (vệt lửa) `VFX_LightningTrail_Flame`
Menu `VFX/LightningTrail/Build Flame`, script `LightningTrailFlameBuild.cs`.
- Mesh / kỹ thuật: bỏ mesh tia điện; dùng hạt đốm lửa với module Trails (vệt lửa, `trail_ribbon_007`), thêm Glow và Sparks.
- Bố cục: đường đi thấp hơn (y 0,8) và vệt bay LÊN (gravity -0,2, noise) thay vì cột elip đứng 1 m.
- Timing: leg 2,0 s (gốc 2,4), đời hạt 0,6 - 1,4 s.
- Lớp: `Embers` (root, `spark_dot_sheet_001` 3x3 + trail), `Glow` (`glow_soft_oval_001`, cục sáng nóng), `Sparks` (`trail_streak_001`, stretched). 3 lớp thay vì 1.
- Khác gốc: mesh/kỹ thuật, bố cục, timing, lớp.

## Wind (vệt gió) `VFX_LightningTrail_Wind`
Menu `VFX/LightningTrail/Build Wind`, script `LightningTrailWindBuild.cs`.
- Mesh / kỹ thuật: dải ruy băng cong từ module Trails (hạt mang render mode None, `trail_ribbon_001`), `Wisps` stretched (`trail_ribbon_007`), `Specks` (`spark_dot_sheet_001`).
- Bố cục: đường đi cao và dài hơn (y 1,4, 7 m); ruy băng sinh từ vỏ cầu bán kính 0,25 quanh đường đi, noise uốn cong.
- Timing: leg 1,6 s (nhanh), đời hạt 0,7 - 1,1 s.
- Lớp: 3 thay vì 1. Màu trắng xanh nhạt, alpha 0,5 - 0,9.
- Khác gốc: mesh/kỹ thuật, bố cục, timing, lớp.

Chưa kiểm: Trails với render mode None phải hiện ruy băng (chưa chạy Unity); chưa build, chưa biên dịch thử.
