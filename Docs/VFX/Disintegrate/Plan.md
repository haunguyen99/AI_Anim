# Disintegrate (tan biến) — Plan, bản HTML v1 (2026-11-18)
Order: `work/vfx_orders/20261118_cuongdt_tanbien/order.md` (Cường). Anatomy: `Docs/VFX/_Anatomy/disintegrate.md`.

## Định hướng không gian (*đề xuất*, Cường chưa xác nhận từng điểm; chủ phiên cho chọn mặc định)
- Ngữ cảnh: **ground** (đối tượng đứng trên đất). Mặt phẳng: hạt + thân = billboard đứng (canvas 2D), **mặt đất ellipse ép theo camera 3/4 sin 40°** (không có Horizontal/Vertical Billboard vì không dùng Unity).
- Quy mô: người cao **2 m**; thùng ~1 m; chữ rộng 2,8 m. Camera 3/4, nhìn xuống 40°. Nền: đêm xanh tối + sàn tròn 8 m.
- Thời gian: một lần, **~3,1 s** (giữ 0,15 → tích 0,15 → quét 0,9 → hạt tàn 1,9; thân tan hết ~1,2 s), tuỳ chọn lặp.
- Màu: xanh lam (mặc định), thêm vàng kim / tím. Một chớp duy nhất: vòng pulse ở chân.

## Bất biến (chép từ Anatomy)
thân còn nguyên hình ở phần chưa tan + hạt lấy màu mảnh gốc; tan theo mặt sóng + noise (mảng); hạt bay lên + lệch gió, nhỏ + mờ dần, hết hẳn; có mép sáng; một ngữ cảnh một chớp.

## Dựng
- `Docs/VFX/Disintegrate/index.html`, 1 file tự chứa, không thư viện, không texture / ảnh ngoài. Đối tượng vẽ bằng canvas rồi lấy mẫu thành 3–7 nghìn hạt 1,2 cm; mô phỏng bước cố định 1/120 s (cùng seed → cùng kết quả).
- Mỗi hạt: trễ = mặt sóng bottom→top (42%) + value-noise 2 octave (58%) + jitter; sau đó bay lên (vy 0,35–1,85 m/s) + noise sin + gió +0,45; drag 1,6; sống 0,8–1,8 s; màu mảnh gốc (nhân 1,15) → mid → end (hot chỉ dùng cho vòng pulse); 1/8 hạt có glow sprite, 1/8 có vệt sao.
- **Texture Library: không dùng** (không có texture; mọi hình vẽ / mô phỏng bằng code web). Không có builder Unity nên `check_texture_plan.py` không áp dụng.
- Âm thanh: **WebAudio tự tổng hợp, không file ngoài, không giấy phép cần ghi**: vút lên lúc tích; thump sine 150→38 Hz; noise dải quét 450→6500 Hz; 70 hạt noise ngắn; 34 ping thang ngũ cung ngẫu nhiên pan; chuông 4 hài lúc thân tan hết; reverb bằng convolver nhiễu; compressor (−14 dB, 6:1) trước loa. Bắt buộc bấm 1 lần để bật tiếng (luật trình duyệt).
- Điều khiển: đối tượng (nhân vật / thùng / chữ), màu, phát lại (Space), lặp, âm thanh + âm lượng, tốc độ. Tham số URL: `?t=<giây>&target=&color=&seed=&ui=0` vẽ đúng 1 khung (dùng để kiểm / xuất ảnh).

## Cách hiểu brief
"Tan biến ngay lập tức" hiểu là **tan nhanh, bắt đầu ngay** (0,3 s sau khi phát, thân tan hết ~1,2 s), không phải biến mất trong 1 khung. Cường nói nếu muốn nhanh hơn / chậm hơn thì chỉnh `T` (hold, charge, sweep).

## Chưa làm / điểm yếu đã biết
- Chưa có prefab Unity (chờ Cường nói có cần không).
- Review vfx-director 3 vòng (xong vòng 3, còn lệch): thùng / chữ vẫn cháy trắng hơn nhân vật (thùng 13%, chữ xanh 10%, chữ vàng 18% pixel ≥225 ở mẫu số max kênh ≥100); gió ngang nhẹ (đã tăng 0,45→0,8 sau vòng 3, chưa đo lại); nhân vật vẽ cao ~1,83 m (không đủ 2 m); rung lúc tích ~1,4 px gần như không thấy.
- Nhân vật là hình vẽ phẳng giả lập (không phải nhân vật thật của game); người dùng thật sẽ thay bằng sprite của mình (cần hàm nạp ảnh — chưa làm).
- Lúc dày hạt, vùng giữa vẫn sáng do cộng sáng (v3: giữ màu mảnh gốc, alpha hạt 0,28; đo ≤ 4% pixel ≥ 225 và vẫn thấy mảnh đỏ ở 0,55–0,95 s).
- Chưa nghe thử bằng tai (chỉ kiểm không lỗi + tạo node được); cần Cường nghe.

---
# v2 (2026-11-18, theo feedback Cường)
Feedback gốc: (1) "nhân vật đang tấn công thì bị dính chưởng và tan biến, như cái búng tay của Thanos"; (2) "thiên về màu đất, cái chết mang thân xác trở về cát bụi"; (3) "game góc nhìn như Diablo 2, top-down xiên"; (4) "html chạy trực tiếp không cần mạng".
- Không gian (yêu cầu của người order, thắng mặc định 3/4 40°): **camera Diablo 2** = ô nền 2:1 (nhìn xuống 30°, mặt đất ép sin 30° = 0,5, chiều cao co cos30°/cos40°), lưới thoi 45° dưới chân. Chọn thêm 3/4 40° và top-down 60° trong UI (`?cam=d2|34|top`). Hiểu "top-down xiên" = đúng kiểu D2; nếu Cường muốn đứng hơn thì chọn top-down 60°.
- Nhịp: chưởng phóng 0,12 s → trúng 0,55 s (chớp duy nhất + giật lùi) → tan lan 0,63–1,73 s → bụi tàn tới ~4,0 s.
- Tan: trễ = 66% khoảng cách tới điểm trúng + 34% noise; hạt trộn **thường** (không `lighter`), màu mảnh gốc (45%) → cát `mid` (214,170,105) → đất sẫm `end`; trôi theo hướng chưởng (wind (−1,−1)/√2 trên mặt đất, +z ngẫu nhiên tạo độ sâu); chỉ lấp lánh + mép tàn dùng cộng sáng, rất nhẹ.
- Sound: chưởng vút (noise dải 500→3200 Hz) → thump 160→34 Hz + nổ lách tách → gió cát đi xuống + 90 hạt cát + 9 tiếng đá vỡ → hai nốt trầm kéo dài. Vẫn tự tổng hợp, không file ngoài.
- Offline: 1 file, không CDN / fetch / ảnh ngoài (đã grep không có `http`, `fetch(`, `src=` ngoài biến).
- Điểm yếu đã biết: nhân vật vẽ phẳng giả lập (không phải model thật); tư thế chỉ 1 pose đứng im + lao nhẹ (không có anim tung chưởng); chưởng phóng từ "ngoài khung" (không có đối thủ); chưa nghe âm thanh bằng tai.
- Bất biến v2 (chép từ Anatomy): thân ở tư thế tấn công trước khi dính; chưởng chạm trước, tan sau; tan từ điểm trúng + noise (mảng); hạt cát bụi màu đất (45% màu mảnh gốc → cát → đất sẫm), trôi theo hướng chưởng, nhỏ + mờ dần, hết hẳn (~4,0 s); mép tàn nhẹ; một chớp (ở điểm trúng); một ngữ cảnh.
- Sau review v2: chưởng vẽ trước thân (đã sửa), mép tàn hạ độ sáng, tint chỉ sau khi trúng, làm tròn toạ độ thân. Đo lại pixel ≥225 (mẫu số max kênh ≥100): 3,9% (0,9 s), 2,5% (1,0 s), 0,6% (1,2 s). Nhân vật vẽ cao ~1,7 m (không phải 2 m). Thùng / chữ chưa đo lại ở v2.

## Giao (2026-11-18)
Cường đồng ý demo v2 → giao gói html + GIF + `Usage.md`. Không prefab Unity. Chờ art lead duyệt nếu muốn đưa vào thư viện.
