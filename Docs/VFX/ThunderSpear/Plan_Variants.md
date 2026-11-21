# ThunderSpear: biến thể Frost và Flame (2026-11-09)

Gốc: `Assets/VFX/ThunderSpear/Editor/ThunderSpearBuild.cs` (cán đứng 2,6 m tại gốc, loop 5 s, 3 lớp: glow, Thunder, electric; số liệu `.claude/skills/vfx-shader/references/thunder-core.md`, `lightning-set.md`).
Cả hai biến thể vẫn là cùng hiệu ứng: giáo loop, glow dọc cán + cung điện dọc cán + vật nhỏ bắn ra quanh cán. Không gian: loop, camera 3/4 (40°), quy mô ~3 m, Stretched Billboard (texture ngang, hướng bay = mép TRÁI) hoặc Billboard, không Horizontal / Vertical, Scaling Mode Hierarchy, không scale trên transform. Texture lấy từ `Assets/Library/` (bản copy vào `Assets/VFX/ThunderSpear/Textures/`). Không có mesh nên không cần log trục mesh.

## Frost (giáo băng) `VFX_ThunderSpear_Frost`
Menu `VFX/ThunderSpear/Build Frost`, script `ThunderSpearFrostBuild.cs`.
- Bố cục: cán nghiêng 28° (đỉnh ngả về +X), tâm y 1,4 (gốc: thẳng đứng, y 1,5). Cone / ellipsoid xoay theo trục nghiêng.
- Timing: loop 4 s (gốc 5 s), hai nhịp lạnh (glow burst t = 0 và 2 s), cung băng sống 0,25 - 0,5 s (gốc 0,1 - 0,2), burst 3 cung ở 1 s và 3 s.
- Lớp: glow oval `glow_soft_oval_001` xanh nhạt; `FrostArcs` = `lightning_bolt_sheet_001` (1x4, tuyến tính); bỏ lớp `electric`, thêm `Shards` (`spark_shard_001` 1x4, mảnh băng xoay, rơi) và `Motes` (`spark_dot_sheet_001` 3x3, bụi sương rơi chậm). 4 lớp thay vì 3.
- Khác gốc ở 3 trục: bố cục, timing, lớp phụ (và texture / màu).

## Flame (giáo lửa) `VFX_ThunderSpear_Flame`
Menu `VFX/ThunderSpear/Build Flame`, script `ThunderSpearFlameBuild.cs`.
- Bố cục: cán nằm NGANG dọc trục X (cầm ngang), tâm y 1,25; cung điện sinh từ box dài 2,4 m dọc cán, đoạn ngắn 0,6 - 1,5 m (gốc: một cung từ một điểm). Embers / Sparks sinh từ box dọc cán và bay lên.
- Timing: loop 3 s, glow nhấp nháy nhanh (sống 0,5 - 0,9 s, rate 6), đợt bùng ở 1,5 s (burst 8 cung + 14 tia lửa); cung trượt dọc cán (speed 0,3 - 0,8).
- Lớp: glow cam; `MagmaArcs` (bolt sheet cam); bỏ `electric`; thêm `Embers` (`spark_dot_sheet_001`, bay lên, gravity -0,25, noise) và `Sparks` (`trail_streak_001` stretched, bắn lên, rơi lại).
- Khác gốc ở 3 trục: bố cục, timing, lớp phụ.

Chưa kiểm: số kích thước Stretched lấy theo gốc (X = bề ngang, Y = chiều dài theo hướng bay) nên cần xem trong Review Lab / Showcase sau khi build; build chưa chạy (Unity đang mở), chưa biên dịch thử.
