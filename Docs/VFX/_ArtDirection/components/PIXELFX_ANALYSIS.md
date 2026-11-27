# Phân tích pixelfx: cách làm VFX bằng code, và áp dụng cho phong cách toon của mình · nháp v0 (2026-11-02)

> Trạng thái: **NHÁP, chờ art lead đọc.** Chưa đưa vào skill. Chỉ tích hợp các mục art lead "chốt".
>
> Nguồn: [patch-gg/pixelfx](https://github.com/patch-gg/pixelfx) (MIT). Đường dẫn file ghi theo repo đó.
> 187 effect đã có trong Shape Lab, nhóm PixelFX (xem `tools/pixelfx/README.md`).

---

## 1. pixelfx làm VFX thế nào (tóm tắt)

**Không có một ảnh nào.** Mỗi effect là một file JS (`src/fx/<nhóm>/<tên>.js`). File đó tự vẽ từng frame bằng code, rồi xuất ra sprite sheet.

| Thành phần | Cách làm | File |
|---|---|---|
| **Khung effect** | Mỗi file khai báo:<br>• `meta`: kích thước, gốc, thời lượng, loop, fps 30, options gồm `palette` và `seed`.<br>• Một trong 2 kiểu hàm:<br>&nbsp;&nbsp;– `draw(t)`: frame chỉ phụ thuộc thời gian, nên loop liền và tua được;<br>&nbsp;&nbsp;– `create()` → `update(dt)` + `draw()`: mô phỏng, dùng cho đòn một lần.<br>• Mô phỏng chạy bước nhỏ ≥ 120 Hz, nên đổi fps không làm sai chuyển động. | `core/fx.js` |
| **Hạt theo loại** | Không mô phỏng chất lỏng. Mỗi **loại hạt** có bộ lực chỉnh tay riêng:<br>• SPARK: trọng lực ×0.45, drag 2.2, nảy 0.45;<br>• FIRE: bốc lên −95, lắc ngang;<br>• SMOKE: bốc chậm, phồng dần, nhạt dần;<br>• GRIT: nảy 1 lần rồi nằm;<br>• EMBER: bay lượn.<br>Lửa **chết thì sinh ra khói**. | `core/sim.js` |
| **Bảng màu dạng ramp** | Mỗi effect dùng **một dải 7–9 bậc màu** tối → sáng, lệch hue (bóng ngả lạnh/sẫm, sáng ngả ấm/trắng). Một con số **"nhiệt"** (thường là tuổi hạt) chọn bậc màu: mới sinh trắng, nguội dần sang vàng → cam → đỏ → khói. Đổi `palette` là lửa thành lửa xanh, không phải sửa code. | `core/color.js` (`at`, `fit`) |
| **2 lớp: màu + ánh sáng** | Lớp **màu** vẽ hình (bậc màu cứng). Lớp **light** cộng sáng lên trên (glow mềm, quầng sàn, đèn chớp lúc trúng rồi tắt dần). Họ ghi rõ: vật nóng trông nóng là nhờ lớp light. | `core/painter.js`, `Lights` |
| **Vẽ như shader** | `p.shade(fn)` tính màu và sáng cho từng pixel, giống fragment shader. Màu của vòng, vệt chém, cầu khói là **hàm của toạ độ trong hình** (từ mép vào lõi, dọc theo vệt), không phải màu phẳng. | `core/painter.js` |
| **Diễn đòn** | Đòn có cấu trúc wind-up → trúng → **hit-stop** (đóng băng 0.03–0.2 s) + rung → hồi.<br>• Tư thế nhân vật chạy bước **12 fps**, hạt chạy đủ 30 fps, tạo cảm giác hoạt hình tay.<br>• Ví dụ chém kiếm: freeze 0.14 s, rung 0.18 s. | `core/act.js` |
| **Kiểm tra tự động** | `check.mjs` bắt các lỗi sau:<br>• không ngẫu nhiên thật (cùng seed phải ra cùng hình);<br>• đòn một lần phải **kết thúc trống trơn**;<br>• loop không giật ở chỗ nối;<br>• không tràn khung;<br>• không chậm quá 4 ms/frame. | `tools/check.mjs` |

## 2. Luật nghệ thuật họ viết thành chuẩn (`docs/AUTHORING.md`, `skills/pixelfx/SKILL.md`)

1. **"Lines and light, not fills"**: dựng bằng nét, vòng, vệt, tia và ánh sáng, không bằng mảng màu lớn.
   - Lõi và mép trắng nóng, giữa có màu, màu sẫm chỉ ở vùng bóng.
   - Một mảng màu bão hoà phẳng gần như luôn sai.
2. **Ánh sáng ở khắp nơi**:
   - quầng lớn yếu và quầng nhỏ gắt ở lõi;
   - mỗi tia lửa có chút sáng;
   - đèn chớp lúc trúng rồi tắt;
   - vũng sáng trên sàn.
3. **Khói/bụi là khối trong mờ**, sáng ở đỉnh, phồng ra và loãng dần.
4. **Chuyển động thật**:
   - tia dài ra theo tốc độ và nảy;
   - mảnh vụn lăn rồi nằm yên;
   - lửa bốc lên và nguội thành khói;
   - **drag**: bắn nhanh, trôi chậm.
5. **Biên đạo theo pha**: tích lực → **1–2 frame trắng "hero"** → bùng → toả → giữ (lấp lánh, tàn lửa) → vỡ/tan → tắt dài.
   - Nhiều sự kiện nhỏ, mỗi cái khác nhau về cỡ, tốc độ, thời điểm, tuổi thọ.
6. **Chiều sâu**: vòng trên sàn là elip dẹt, nửa xa nằm sau nhân vật, nửa gần nằm trước. Lớp phía sau tối hơn một bậc.
7. **"Fast attack, slow release"**: đòn đánh 0.3–0.8 s nhưng vẫn có dư âm. Effect lớn kéo dài 2–4 s.
8. **Đọc được ở cỡ thật**: một tâm điểm, không lấm tấm nhiễu bên trong hình.

**Bảng sửa lỗi** (dịch từ SKILL.md):

| Thấy | Sửa |
|---|---|
| Lờ đờ, không lực | Ease `outExpo`/`outQuart`, thêm 1–2 frame trắng, rút ngắn tổng thời gian |
| Cứng | Mỗi hạt khác cỡ/tốc độ/delay/tuổi thọ, thêm chuyển động phụ |
| Bệt, nhạt | Glow 0.2–0.5, mép tối hơn một bậc, trắng chỉ ở lõi nóng nhất |
| Phẳng | Sáng từ trên-trái, tối một bậc ở dưới-phải và ở chân |
| Trông như vector | Màu theo **bậc cứng**; mềm chỉ ở ánh sáng và khói |
| Đòn một lần tắt cái bụp | Co lại / tan / rơi đi trước khi hết thời lượng |

**Quy trình của skill:**
1. Tìm effect có sẵn trước.
2. Mô tả bằng một câu.
3. Đọc 2–3 effect gần nhất.
4. Làm **3–5 bản nháp khác hẳn nhau**.
5. Render contact sheet và đặt cạnh bản tham chiếu.
6. Sửa chỗ tệ nhất, **tối thiểu 3 vòng**.
7. Xem từng bước 12 fps, vì lỗi chuyển động không lộ trên ảnh mẫu.
8. Chạy `check` phải sạch.

## 3. Con số đáng tham khảo (impact)

| Effect | Cấu trúc |
|---|---|
| `impacts/hit-spark` (0.5 s) | • Frame 1 (< 0.025 s): chớp 5 tia lệch + kim cương trắng.<br>• Tới 0.058 s: tia dài 1.2×, mảnh 0.55×.<br>• Tới 0.092 s: chỉ còn tia dài, cháy từ gốc.<br>• 9 tia lửa (170–360 px/s, nón ±0.6 rad, sống 0.25–0.45 s) + 6 mảnh vụn.<br>• 3 đèn chớp. |
| `impacts/crit-hit` (0.9 s) | • Sao 14 gai, gai dài lệch về hướng đòn.<br>• Bảng key: trắng → **vượt 1.3×** → về 1.05× và mảnh lại → vỡ trước 0.125 s.<br>• Vòng **đứt đoạn** 7 đoạn, nở ease `outCubic` trong 0.37 s, màu tụt bậc theo thời gian.<br>• 36 tia (22% bắn ngược) + 10 mảnh + 5 sao lấp lánh **trễ 0.08–0.32 s** (pha "giữ"). |
| `impacts/ground-slam` (3.2 s) | • Chớp nằm sàn, chỉ 1–2 frame.<br>• 10 vết nứt phát sáng rồi nguội.<br>• Vòng sàn tách nửa trước/sau + **2 mặt sóng hình lưỡi liềm** chạy ra trong 0.6 s, sau lưng có bụi.<br>• 56 tia, 20 đá, 110 hạt sạn, 38 cụm bụi lớn.<br>• Đèn 96 px / 0.6 s. |
| `explosions/big-explosion` | • **3 vụ nổ cách nhau một nhịp** (0 / 0.13 / 0.25 s).<br>• Vòm trắng < 0.04 s.<br>• Quả cầu lửa cuộn (42 thuỳ trên vòng xoáy) **nguội dần từ lửa thành khói**.<br>• Đá nóng chảy để lại lửa nơi rơi xuống.<br>• Vết cháy nguội trong 3.4 s, khói tan khoảng 4 s. |

---

## 4. So với cách mình đang làm

| | pixelfx | Mình (thành phần toon 3D) |
|---|---|---|
| Đơn vị | 1 file = 1 effect hoàn chỉnh | 1 thành phần = 1 vai trò. Tool mix ghép lại. **Tương đương lớp "kind" + pha của họ** |
| Màu | Ramp 7–9 bậc, chọn theo nhiệt | 3 ô màu Core/Mid/Outer + Color over Lifetime (mượt) |
| Ánh sáng | Lớp light riêng cho mọi thứ | Glow là một thành phần riêng. Tia, vòng, khói **chưa có** sáng riêng |
| Thời gian | Bậc theo frame 30 fps, key cứng, hero frame trắng | Curve mượt trong Unity, chưa có hero frame, chưa có hit-stop |
| Ngẫu nhiên | Seed, kiểm tra tất định | Có seed theo tên layer. Chưa có check tự động |
| Kiểm tra | Contact sheet + `check.mjs` | Preview sheet + Review Lab (có mắt người, **chưa có máy kiểm**) |

**Mình đã tự đi đúng hướng ở mấy chỗ** (pixelfx xác nhận):
- Sparks dùng Stretched Billboard + Speed Scale + Drag (họ có "tia dài theo tốc độ", drag 2.2).
- Dust: bắn nhanh rồi gần như dừng nhờ Drag 3; lúc đầu phải là một khối liền rồi mới loang ra.
- Ring: vòng mảnh nở ease-out, nét mỏng dần.

---

## 5. Đề xuất áp dụng cho phong cách toon gốc

Nguyên tắc: **lấy phương pháp, không lấy nét pixel.**
- Bỏ: dither Bayer, nét 1 px, "không blend".
- Giữ: **bậc tông cứng** (toon band) + mép khử răng cưa. Mềm chỉ ở glow và khói. Đây cũng chính là nguyên tắc của họ.

### Nhóm A · Làm ngay được, ít rủi ro

| # | Đề xuất | Áp vào | Cách làm |
|---|---|---|---|
| A1 | **Hero frame trắng** | `IMP_Hit` | • 1–2 frame đầu (≤ 0.033 s/frame) trắng tinh, to nhất.<br>• Frame 2 vượt **1.3×** rồi về 1.05× và mảnh lại.<br>• Vỡ trước ~0.125 s.<br>• Sinh sheet bằng Python từ một **bảng key** `[t, scale, độ dày, alpha, bậc màu]`, giống `crit-hit.KEYS`. |
| A2 | **Hit-stop + rung trong recipe** | Tool mix | • Thêm `freeze` (0.03–0.2 s), `shake`, `amp` vào `recipe.json`. t = 0 là lúc chạm, wind-up nằm ở thời gian âm.<br>• Unity: `Pause` / `Simulate` các particle trong `freeze` giây + Cinemachine Impulse.<br>• Mặc định: đòn nhẹ 0.05 s, đòn nặng 0.12–0.15 s. |
| A3 | **Sao lấp lánh trễ** (pha "giữ") | Sparks hoặc thành phần mới `TWK` | 3–5 sao chữ thập nhỏ, delay **0.08–0.32 s**, sống 0.15 s. Effect còn "sống" sau khi chớp đã tắt. |
| A4 | **Đa dạng mọi thứ** | Mọi thành phần | • Mọi hạt random delay 0–0.05 s, size, speed, lifetime.<br>• Dùng làm tiêu chí review (đã đúng với góp ý Sparks size).<br>• Ghi vào STANDARD mục "Ngẫu nhiên". |
| A5 | **Kiểm tra tự động** | Build kit + Review Lab | Thêm vào `ComponentKit.Report`:<br>• frame cuối của đòn một lần phải trống;<br>• không tràn ô sheet;<br>• loop không giật ở chỗ nối;<br>• cùng seed thì ra cùng ảnh.<br>Kết quả hiện ngay trong Review Lab. |

### Nhóm B · Đổi cách tô màu (cần thử trước)

| # | Đề xuất | Cách làm |
|---|---|---|
| B1 | **Ramp nhiệt thay cho 3 ô màu** | • Core/Mid/Outer mở rộng thành **ramp 6–8 bậc** (texture 1×N), sinh tự động từ 3 ô: thêm trắng ở đầu, thêm bậc sẫm lệch hue ở cuối.<br>• Shader toon nhẹ (1 sample sheet + 1 sample ramp) chọn bậc theo **độ sáng texture × tuổi hạt** (AgePercent qua Custom Vertex Stream).<br>• Hạt mới sinh trắng, nguội dần thành màu rồi sẫm, đúng kiểu `heat → idx`.<br>• Đổi nguyên tố chỉ cần đổi ramp. |
| B2 | **Lửa nguội thành khói** | Sub Emitter on Death: hạt lửa chết thì sinh cụm Dust/khói. Màu bóng của khói lúc còn nóng nhuốm ramp lửa. |
| B3 | **Khói toon "lobe"** | Cụm khói tô 3 bậc theo pháp tuyến cầu, sáng trên-trái (`lobe()` style 1). Sheet A Toon puff đang có gần đúng kiểu này. Có thể sinh thêm biến thể bằng script với cùng luật. |

### Nhóm C · Lớp ánh sáng cho mọi thành phần

| # | Đề xuất | Cách làm |
|---|---|---|
| C1 | **Mỗi thành phần có 2 phần: thân + sáng** | • Thân: bậc tông cứng.<br>• Sáng: billboard Add mềm, falloff `(1-d)²`.<br>• Tia lửa có chấm sáng nhỏ, vòng sóng có quầng mảnh, khói gần lửa được hắt sáng.<br>• Thêm `light` (0–1) vào thông số chung của mọi thành phần, tool mix chỉnh được. |
| C2 | **Đèn chớp `Lights`** | Một quad glow: cường độ theo `life²`, bán kính co còn 55%. Đây chính là Glow Air hiện tại; có thể chuẩn hoá đường cong theo họ. |
| C3 | **Vòng sàn tách nửa trước/sau** | Ring Ground chia 2 renderer, nửa xa sau nhân vật, nửa gần trước, để có chiều sâu thật. |

### Nhóm D · Quy trình (đưa vào skill khi chốt)

- Trước khi làm mới: **tìm trong thư viện trước** (giờ có thêm 187 PixelFX để tham chiếu hình và nhịp).
- Hướng còn mở thì làm **3–5 nháp khác hẳn nhau**, đúng kiểu `spark_options` / `dust_options` mình đang làm. Giữ cách này.
- **Sửa chỗ tệ nhất, tối thiểu 3 vòng.** Xem frame liên tiếp, không chỉ xem 8 mốc.
- Dùng bảng sửa lỗi ở mục 2 làm checklist review.

---

## 6. Đề xuất bước tiếp theo

Thử **A1 + A2 + A3** trên bộ Impact:
- hero frame trắng có overshoot cho `IMP_Hit`;
- sao lấp lánh trễ;
- `freeze`/`shake` trong preview combo.

Sau đó so trước/sau trên Review Lab. Nếu art lead thấy có lực hơn rõ thì làm tiếp B1 (ramp nhiệt + shader toon) trên Sparks và Glow.

## 7. Câu hỏi cho art lead

1. Đồng ý hướng **"lấy phương pháp, giữ toon mượt"** không? (Bỏ dither/nét pixel, giữ bậc tông cứng.)
2. Thử nhóm nào trước: **A** (nhịp + hero frame + hit-stop), **B** (ramp nhiệt), hay **C** (lớp sáng)?
3. Hit-stop có nằm trong phạm vi VFX không, hay thuộc phần gameplay/animation (mình chỉ xuất số liệu)?
