# Electric bolt nối A→B bằng code + shader (không texture)

Làm 2026-11-09, art lead duyệt ("ổn đó"). Đây là cách làm **realtime**: hình do shader tính trên quad của particle, **0 texture**. Khác hướng flipbook bằng Python của skill (`fxlib.bolt`, `examples/lightning_arc.py`). Dùng cách này khi art lead muốn "hoàn toàn bằng code và shader".

- Effect trong project: `Assets/VFX/ElectricBolt/` (prefab `VFX_ElectricBolt`, menu **VFX → ElectricBolt → Build**).
- Tài liệu: `Docs/VFX/ElectricBolt/Research.md` (4 kỹ thuật làm tia + nguồn), `Plan.md` (bảng lớp v2).
- Preview: `examples/previews/electric_bolt_preview.png`.
- Bản lưu trong skill, vì code trong `Assets/` không commit vào git:
  - `assets/shaders/SH_VFX_ElectricBolt.shader`
  - `assets/shaders/SH_VFX_GlowStar.shader`
  - `assets/ElectricBoltBuild.example.cs`

## Không gian (đã chốt với art lead)

| Mục | Giá trị |
|---|---|
| Ngữ cảnh | air (dir): tia nằm ngang từ tay (A, gốc prefab, cao 1.3 m) tới ngực mục tiêu (B, cách 8 m theo +Z) |
| Mặt phẳng | thân tia + cung dọc thân: Stretched Billboard; chớp / sao / cung cuộn: Billboard |
| Camera | 3/4 nhìn xuống 40°; preview nhìn từ bên hông (−X) để thấy đủ chiều dài |
| Timing | một phát ~0.45 s: tia vươn 0.05 s, nháy, mảnh dần, đứt khúc |
| Màu | xanh-trắng toon cứng: lõi HDR (1.4, 1.5, 1.6), viền HDR (0.25, 0.6, 2.0) |

## Shader

**`VFX/FX/Electric Bolt`** (`SH_VFX_ElectricBolt`): tia trên quad dài; u = dọc tia, v = ngang tia.

1. **Đường gấp khúc từ hash:**
   - Dùng value noise **tuyến tính**: `lerp(hash(i), hash(i+1), frac(t))` cho ra các đoạn thẳng gãy khúc, đúng chất sét (noise mượt nhìn như dây mềm).
   - 2 tầng: `_Segments` khúc lớn + 3× khúc nhỏ (`_Detail`).
   - Hash không dùng sin: Dave Hoskins `hash11`, ổn định trên mobile.
2. **Ghim hai đầu:** biên độ × `saturate(u(1−u)·_Pin)`. Đầu tia luôn chạm A và B.
3. **Khoảng cách đúng bề dày ở đoạn dốc:**
   - `|y − off| · rsqrt(1 + slope²)`; slope lấy luôn từ hiệu hai điểm hash (không cần đạo hàm).
   - Chia slope cho `_Aspect` (dài / rộng quad), nếu không thì đoạn dốc bị mảnh.
4. **Toon:**
   - lõi `_CoreWidth`, viền `_RimWidth`, mép cứng có AA bằng `fwidth` (target 3.0);
   - glow ngoài nhẹ `_Glow`;
   - sợi phụ mảnh (`_Strand`, seed khác, biên độ 0.8×).
5. **Đổi hình:** `frame = floor(_Time.y·_Fps + seed·17)` tính ở vertex. Hình đổi 12–20 lần/s, độ sáng nháy theo `hash(frame)` (`_FlickerMin`).
6. **Dữ liệu từ particle:** stream `Position, Color, UV, Custom1XYZ`.
   - x = mảnh / chết: tới 0.5 thì mảnh dần, từ 0.5 đứt từng khúc nhỏ (`step(cut, hash(khúc))`);
   - y = seed (random 0–1);
   - z = độ vươn 0→1, đo từ đầu u = 0 (`_Flip` đảo đầu).
7. Blend One One, màu nhân sẵn alpha. Chi phí: 0 sample, ~10 hash.

**`VFX/FX/Glow Star`** (`SH_VFX_GlowStar`):
- đĩa lõi trắng cứng + viền màu + glow mềm;
- keyword `_STAR`: sao 4 cánh `1 − |x||y|·sharp − r` + 4 cánh chéo mảnh (`_Diagonal`), toon 2 tông;
- hoạt ảnh bằng Size / Color over Lifetime. 0 sample.

**`VFX/FX/Spark`** (có sẵn trong project): tia lửa, stream `Custom1X` = tuổi (curve tuyến tính 0→1).

## Bảng lớp (số trong `ElectricBoltBuild.example.cs`)

| ID | Layer | Timing (s) | Carrier | Material |
|---|---|---|---|---|
| L1 | HandGlow (root) | 0–0.14 | Billboard 0.8 m | Glow Star: lõi 0.14, viền 0.26, glow 0.7 |
| L2 | Bolt | 0–0.32 | Stretched, size 1.6, lengthScale 5 → 8 m | Electric Bolt: aspect 5, seg 8, amp 0.26, detail 0.35, pin 12, lõi 0.025, viền 0.07, strand 0.6, 12 fps |
| L2b | Bolt2 | 0.1–0.34 | như L2, màu 0.8 | aspect 5, seg 10, amp 0.3, lõi 0.012, viền 0.04, không strand, 15 fps, viền xanh đậm |
| L3 | SideArcs | 0.03–0.33, 40/s, đời 0.06–0.12 | Stretched size 0.4–0.6, lengthScale 2, Box dài 7.5 m, hướng random | aspect 2, seg 4, amp 0.3, 20 fps |
| L4 | ImpactFlash | 0.04–0.18 tại B | Billboard 1.6 m | Glow Star: lõi 0.2, viền 0.34, glow 0.9 |
| L5 | ImpactStar | 0.05–0.14 | Billboard 1.4 m, xoay random | Glow Star `_STAR`, sharp 20, diagonal 0.45 |
| L6 | ImpactArcs | 0.05–0.35, burst 2 + 14/s | Billboard 0.6–1.0 m, xoay random | aspect 1, seg 3, amp 0.36, pin 6 |
| L7 | Sparks | 0.04, burst 12, 4–8 m/s, gravity 1 | Stretched, velocity scale 0.04, pivot (0,1,0) | Spark |

Custom1 của thân tia:
- x (thin): (0, 0) → (0.55, 0.05) → (0.85, 0.55) → (1, 1);
- z (reach): lên 1 trong 0.05 s;
- y (seed): random.

Thứ tự vẽ: SideArcs 1, ImpactArcs 2, Bolt2 3, Bolt 4, Sparks 5, HandGlow 6, ImpactFlash 7, ImpactStar 8.

## Đặt tia A→B bằng Stretched Billboard

- Hạt đặt **tại A** (Cone góc 0, `shape.rotation = (0, 180, 0)`), speed 0.01, nên bay **ngược** về −Z.
- Quad Stretched kéo **ra phía sau hạt**, tức là về phía B. Đã kiểm bằng preview.
- Velocity scale 0, lengthScale = dài / rộng; Start Rotation = 0.
- Độ dài tia gắn với size, nên **không làm tia mảnh bằng cách giảm size**: chỉnh `_CoreWidth/_RimWidth` hoặc dựng thêm lớp.
- Vào Showcase: instance cao 1.3 m, xoay Y 90°, `focusOffset` (0, 0, 4).

## Lỗi đã gặp

- **v1 dùng sprite sheet (`bolt_sheet_001`):** texture có lề trống hai đầu, nên tia chỉ phủ ~2/3 khoảng A–B. Shader vẽ trên toàn chiều dài quad thì hết lỗi.
- **Tên biến `cross` trong HLSL** trùng hàm có sẵn và có thể lỗi compile. Đổi tên biến.
- **Overload C# cùng tên, khác kiểu `int`/`float`:** lời gọi `fps: 12` rơi vào overload `int`. Chỉ giữ một hàm, tham số `float`.

## Biến thể (đổi ít nhất 2 trong mesh / bố cục / timing / lớp phụ)

- **Chain:** nhiều cặp A→B nối tiếp, mỗi đoạn trễ 0.06 s.
- **Loop / kênh liên tục:** `loop`, Custom1.x giữ ~0, rate 6/s đè nhau.
- **Màu nguyên tố:** chỉ đổi `_ColorRim` thì **chưa đủ** làm biến thể; phải đổi thêm amp / seg / timing / lớp phụ.
