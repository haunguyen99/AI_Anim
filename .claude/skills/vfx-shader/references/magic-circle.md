# Magic circle (vòng phép) — dùng cách làm đã có, không viết shader

Art lead, 2026-11-03: vfx dạng magic circle **lấy cách làm của các skill khác** (vfx-maker). Vòng phép vẽ bằng script ra rất tốt (hình học chính xác: vòng, chấm, vạch, cánh); đây là loại duy nhất script vẽ tốt. Hình hữu cơ (lửa, khói, nổ) thì không (xem bộ nhớ `script-shapes-geometric-vs-organic`).

Vì vậy với magic circle, **vfx-shader không viết shader mới**: texture vẽ bằng script + particle + shader có sẵn (stock Additive của `VfxBuildKit`, hoặc `ColosoShaderAdditive` nếu cần ramp màu / dissolve). Bước định hướng không gian, kế hoạch duyệt 1 lần, Review Lab giữ nguyên như mọi effect.

## Cách làm (mẫu: HealCircle, `Assets/VFX/HealCircle/`)

1. **Vẽ texture bằng script**: `scripts/heal_circle_textures.py` (bản sao của `Docs/VFX/HealCircle/heal_circle_textures.py`).
   - Trắng trên đen, 512 px, supersample 4× cho nét mảnh sạch; màu do hạt tô.
   - `RuneOuter`: vành ngoài (vòng đôi, chấm, vạch, cung nhỏ) xoay một chiều. `RuneInner`: hoa văn trong (vòng, cánh, vòng tâm) xoay chiều ngược lại. `Beam`: cột sáng cho Stretched Billboard (mép phải sáng = sát đất, mép trái = hướng bay lên).
   - Hình theo ý nghĩa: hồi máu = tròn / chấm / cánh lá, **không gai**; sát thương / cấm = có thể vạch, gai, tam giác. Hỏi art lead khi brief chưa nói.
2. **Dựng bằng particle** (`assets/MagicCircleBuild.example.cs`, từ `HealCircleBuild.cs`): các lớp GroundGlow, RuneOuter, RuneInner, Beam, Motes, Sparkles.
   - Vòng nằm đất = **Billboard + Render Alignment Local, GameObject xoay X 90°** (không dùng Horizontal Billboard). Neo bám nhân vật = simulation space Local.
   - Hai vòng xoay ngược chiều bằng Rotation over Lifetime; vòng phát một lần (1.5 s) hoặc lặp tuỳ brief.
   - Mỗi lớp `sortingOrder` khác nhau (mặt phẳng nằm đất trước, rồi độ sáng).
3. **Muốn thêm hiệu ứng shader** (viền sáng chạy quanh vòng, hiện dần theo góc, dissolve kết thúc): dùng bộ Coloso ([coloso.md](coloso.md)) với texture vòng xám làm `_MainTex`, `_ColorTex` / Color over Lifetime cho màu, dissolve theo Custom1.x. Chỉ khi cần thật mới đụng tới shader mới.

## Luật

- Quy mô: so với người 2 m (HealCircle ~2 m dưới chân). Camera mặc định 3/4 nhìn xuống 40°; vòng nằm đất bị dẹt theo góc nhìn.
- Texture là hình học đơn phần tử cho particle; không bake cả effect vào một ảnh.
- Frame over Time (nếu có sheet) phải tuyến tính.
- Skill vfx-maker (`/vfx-maker`) vẫn là chỗ gốc của quy trình texture + particle: nếu effect chỉ là vòng phép thuần (không cần shader nào ngoài stock), người dùng có thể gọi thẳng `/vfx-maker`.
