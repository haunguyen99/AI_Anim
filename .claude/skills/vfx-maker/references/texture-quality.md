# Chuẩn chất lượng texture VFX (đo từ thư viện)

Đọc kèm [shape-language.md](shape-language.md): nguyên tắc thiết kế hình khối cho lửa, khói, điện, impact, slash, shockwave, sparkle (từ web và board Pinterest của người dùng).

Các con số dưới đây đo trực tiếp từ texture chất lượng cao trong `D:\Projects\animlibrary\Assets\VFX_Library\Textures` (Cartoon FX, VFX Epic Trio, Piloto Studio, Hun0FX, AAA Projectiles) ngày 2026-10-20. Dùng làm thước đo khi tạo texture bằng script, khi viết TEXTURE REQUEST cho ChatGPT và khi kiểm tra ảnh nhận về.

Cách đo: `occ` = cạnh lớn nhất của vùng có hình / cạnh ảnh; `mid` = tỉ lệ pixel ở vùng chuyển tiếp (không đen, không trắng) — thấp nghĩa là mép sắc; `tones` = số bậc sáng chính.

## Quy tắc chung

1. **Hình phủ 85–92% ô, lề chỉ 4–8%.** Lề rộng (≥10%) phí độ phân giải: particle trông nhỏ và mờ hơn ở cùng kích thước texture. Glow mềm có thể phủ 75–80% vì đuôi suy giảm.
2. **Mỗi texture một vai trò, một kiểu mép.**
   - Hình sắc (lửa anime, sao, tàn lửa, khói hoạt hình): `mid ≈ 0.05–0.3`, chỉ khử răng cưa 1–2 px.
   - Hình mềm (glow, ring, khói thật): `mid ≈ 0.65–0.8`.
3. **Lửa và tàn lửa anime chỉ dùng 1 tông trắng.** Tầng màu (đỏ sẫm → cam → vàng) tạo bằng nhiều layer particle tint khác nhau dùng chung một texture, không vẽ sẵn nhiều tông vào texture.
4. **Khói hoạt hình dùng 2 tông.** Thân trắng sáng (~0.95), dải bóng xám **nhạt** (~0.75–0.8) ở phía dưới-phải, cộng vài nếp gấp cong mảnh bên trong. Bóng tối hơn ~0.6 trông bẩn khi tint.
5. **Glow suy giảm kiểu Gaussian, không có đĩa lõi cứng.** Profile mẫu theo bán kính (0 → 0.9 nửa cạnh): `0.97, 0.85, 0.67, 0.46, 0.28, 0.15, 0.07, 0.03, 0.01`. Lõi cứng là dấu hiệu texture nghiệp dư.
6. **Ring/shockwave không đối xứng.** Vành nằm ở ~0.75–0.85 bán kính, mép ngoài sắc, mép trong mờ dần vào tâm (~0.2 bán kính). Ring có quầng đều hai phía trông phẳng.
7. **Sao anime là thân đặc, cạnh lõm, mũi nhọn** (dạng astroid/superformula), không phải các tia mảnh. Tia mảnh có glow là loại khác (glint).
8. **Spark là sao chổi bất đối xứng:** đầu tròn sáng ở một đầu, đuôi thon và tối dần về đầu kia. Flare đối xứng chỉ dùng cho lóe sáng anamorphic.
9. **Flipbook chỉ làm cho khói, lửa, điện** (quy định của art lead). Các loại khác (glow, ring, sao, spark, slash...) dùng texture đơn hoặc atlas biến thể; chuyển động do module particle (Size/Color/Rotation over Lifetime...). Quy tắc dissolve cho các flipbook này:
   - **Ít lỗ:** tổng khoảng 5–8 lỗ (1–2 lớn, 2–3 vừa, 2–4 nhỏ). Nhiều lỗ trông như pho mát.
   - **Lỗ chia 3 cỡ lớn / vừa / nhỏ** (~1 : 0,55 : 0,3), **không bao giờ để 2 lỗ cùng cỡ nằm cạnh nhau**, và thứ bậc này đúng ở **mọi frame** (lỗ bung nhanh rồi tất cả lớn lên cùng tỉ lệ).
   - **Ngẫu nhiên, hữu cơ:** lỗ méo ghép 2–3 khối, xoay ngẫu nhiên, mở lệch thời điểm, có lỗ ăn từ mép ngoài; nét còn lại có dày có mỏng (vài khe dài, lỗ lớn dần gặp nhau).
   - **Mờ theo hướng chuyển động:** texture tan theo hướng A thì phía ngược A tan trước và **làm mờ dọc theo vector A** (motion blur theo trục A, lệch về phía +A), độ mờ tăng dần theo frame; frame đầu sắc nét. Kiểu soft còn trộn mép lỗ mờ và sắc.
   - Frame cuối gần như trống.
10. **Lửa:** dùng luật lửa của art lead ([shape-language.md](shape-language.md), mục "Yêu cầu của art lead"): khung 2 đường lõm lưng đối lưng `) (`, ngọn móc cong. Dáng **hạt đậu** (hai mép cùng phồng) là **sai** theo luật đó. Số đo hạt đậu / chữ C trong bảng dưới chỉ mô tả texture cfxr của thư viện, không phải chuẩn.

## Bảng tham chiếu

| Loại | Mẫu thư viện | occ | mid | tones | Đặc điểm nhận diện |
|---|---|---|---|---|---|
| Glow | Glow_Standard, Tx_Glow_01 | 0.74–0.84 | 0.65–0.68 | 4 | Gaussian, không lõi cứng |
| Glow dot | Glow_Dot_01 | 0.87 | 0.31 | 2 | đĩa phẳng, mép mềm ~15% bán kính |
| Ring | Ring_Soft_Thin, GenericRing | 0.79–0.85 | 0.72–0.81 | 5–9 | vành ở r≈0.75, mép ngoài sắc, trong mờ |
| Sao | cfxr magic star, Star_FourSide | 0.85–0.94 | 0.08–0.35 | 1–2 | thân đặc, cạnh lõm, mũi nhọn |
| Khói hoạt hình | cfxr smoke cloud x4, explosion smoke | 0.92–0.94 | 0.28–0.38 | 2–3 | múi tròn, bóng xám nhạt dưới-phải, nếp gấp |
| Lửa anime | cfxr fire small anim | 0.83–0.92 | 0.05 | 1 | 1 tông, hình hạt đậu/chữ C, móc cong (*kiểu cfxr; khác luật art lead*) |
| Điện anime | cfxr electric arcs x4 | ~0.85 ngang | thấp | 1–2 | 5–8 góc gãy sắc lên/xuống luân phiên, nét chính dày mỏng + nét phụ mảnh đan chéo, quầng nhẹ |
| Điện realistic | T_Spark | ~0.9 | cao | nhiều | đường răng cưa li ti, có nhánh, quầng sáng rõ |

## Kiểm tra nhanh một texture

- Phủ ô 0.85–0.92? Không chạm mép?
- Đúng kiểu mép cho vai trò (sắc hay mềm)?
- Số tông đúng (lửa anime 1, khói hoạt hình 2, glow liên tục)?
- Nhìn ở 64 px vẫn đọc được silhouette?
- Flipbook dissolve: ít lỗ (5–8), đủ 3 cỡ, không 2 lỗ cùng cỡ cạnh nhau ở bất kỳ frame nào, nét có dày có mỏng, mờ dọc theo hướng tan A, frame cuối gần như trống?

Script `scripts/make_texture.py` đã được chỉnh theo các quy tắc này (glow lệch profile thư viện ≤ 0.04). Giới hạn còn lại: mép lửa dựng bằng hình học trơn hơn lửa vẽ tay; flipbook lửa/khói "hero" vẫn nên lấy từ thư viện hoặc ChatGPT.
