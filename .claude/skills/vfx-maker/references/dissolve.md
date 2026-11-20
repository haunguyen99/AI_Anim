# Kết thúc và dissolve theo layer

Đọc khi một layer cần tan/kết thúc khác fade thường, hoặc khi viết cột "Kết thúc" trong kế hoạch. Gộp từ thư viện dissolve của dynamic-vfx-prompt-builder (2.0.0) và quy tắc art lead. Quy tắc art lead đứng trên.

## Quy tắc art lead (ưu tiên cao nhất)

- Lỗ tan có nhịp **lớn / vừa / nhỏ**, ít lỗ (5–8). **Không bao giờ có hai lỗ cùng cỡ nằm cạnh nhau**. `make_texture.py --anim` in số cặp như vậy: phải bằng 0.
- Mờ có hướng **dọc theo vector tan A** (`--dir`), không nhoè đều.
- Flipbook chỉ cho khói, lửa, điện. Loop = 8 frame (4×2), không loop = 16 frame (4×4).
- Nhịp tan đều theo diện tích: frame đầu 100%, frame cuối 0%. Khói đã thử: CoreOut (tan theo khối từ lõi cụm ra, quả nhỏ tan trước).
- Đã bị loại cho khói: dissolve noise thường (Cells/Streaks/Chunks), tan từ trong ra theo từng quả (bị khoét thành vòng).

Thử nhanh các kiểu tan trên **Shape Lab** trước khi làm texture hoặc shader. Các kiểu có sẵn:
- Từ lõi ra, Từ mép vào, Từ dưới lên, Từ trên xuống, Chỉ noise.
- **Theo độ dày**: nét mỏng tan trước, mép tan sang mép đối diện.
- **Theo độ sáng**: tối tan trước, hoặc sáng tan trước.

## 1. Phân biệt hành vi trước khi chọn kỹ thuật

| Hành vi | Nghĩa | Ghi chú |
|---|---|---|
| Fade | Giảm độ phủ/độ sáng toàn bộ | Không đổi silhouette có cấu trúc |
| Thu nhỏ | Size over Lifetime về 0 | Rẻ nhất, hợp spark/ember |
| Ăn mòn (dissolve) | Vùng mất theo mask thứ tự, vùng khác giữ lâu hơn | Shader hoặc frame vẽ |
| Quét / rút | Đầu quét hoặc rút theo trục/đường | Không thay bằng lỗ noise nếu brief cần rút về nguồn |
| Vỡ mảng | Hình tách thành mảnh | Mảnh bay thật cần particle/asset riêng |
| Flipbook | Hình biến đổi mạnh mà mask/module không đủ | Theo quy tắc art lead ở trên |

Nếu fade/thu nhỏ đã đủ thì không thêm dissolve. Đừng thêm dissolve chỉ vì thư viện có.

## 2. Hợp đồng mask

`A` = coverage gốc theo kênh shader đọc, `M` = mask thứ tự trong [0,1] (cao = giữ lâu), `p` = tiến độ 0→1, `w > 0` = độ mềm.

```text
t = lerp(-w, 1, saturate(p))
keep = smoothstep(t, t + w, M)
coverage = A * keep * particleOpacity
```

p = 0 giữ nguyên, p = 1 mất hết (kể cả texel M = 1). Không để hai cạnh smoothstep bằng nhau. Additive phải giảm cả RGB/emission theo `keep`, không chỉ alpha. Mask dữ liệu import **linear** (tắt sRGB).

Tan theo sáng tối thì M phải là độ sáng **có ý nghĩa trong hình**: vùng mờ mất trước, lõi sáng giữ cuối. Alpha trắng phẳng không có phân cấp sáng; noise độc lập không biết lõi ở đâu.

## 3. Gợi ý theo nguyên tố

| Nhóm | Kết thúc hợp | Tránh |
|---|---|---|
| Lửa | Mép/lưỡi mỏng co, tan trước; khối nóng giữ lâu | Noise trắng đục lõi |
| Khói / hơi | Mảng tách, khoảng hở nở có cấu trúc (CoreOut) | Rách cứng đều, noise li ti |
| Điện / plasma | Nhánh con tắt trước, thân đứt khúc, lõi mảnh dần | Rung hình/dư chấn tự thêm |
| Nước / chất lỏng | Màng mỏng tách, co thành giọt | Threshold tự tạo giọt chuyển động |
| Băng / đá / pha lê | Nứt theo mảng (cell/crack), mòn mép | Viền cháy, tự thêm nước |
| Gió / slash | Mỏng đuôi, tan từ đuôi về đầu dọc nét | Phá cả cung thành sợi |
| Độc / acid | Bọt vỡ, loang theo blob có nhịp | Rách nhỏ đồng đều |
| Ánh sáng / thánh | Ngoài mờ mất trước, lõi thu và tắt cuối | Noise thủng lõi |
| Bóng tối / void | Co hút về tâm hoặc ăn mảng | Mặc định xoá từ sáng tới tối |
| Ma thuật / rune | Tắt theo nét, mảnh panel mất lần lượt | Biến rune thành đám noise |
| Vụ nổ nhiều lớp | Mỗi lớp một cách kết thúc riêng | Một mask chung cho flash/khói/đá |

## 4. Kiểm tra

- Xem tiến độ 0, 0.25, 0.5, 0.75, 1 và playback đúng thời lượng thật.
- Kết thúc phải sạch: không còn hạt hay lõi sáng sót lại. Vùng quan trọng không mất quá sớm. Không có viền sáng ngoài silhouette.
- Random seed không làm topology mask nhảy giữa các frame. Replay/pool reuse reset đúng.
- Mobile: hạn chế nhiều noise sample/pass và overdraw. Tiến độ tan không được kéo dài lifetime đã duyệt.
