# Director log – windy_skill1

## Director – Windy Skill1 skill1_p10 – mốc blocking – 2026-11-10
**Kết luận: Cần sửa** (chưa gửi user duyệt; chưa đủ ảnh, thiếu cam game)
Ý chính: Ba pose F8/F12/F16 đọc được ý "lấy đà, quét ra, đẩy trước", nhưng chưa ai nhìn được pose đẩy ra trước + 2 vòng xoay ở cam game và F16 bị thân che mất trượng. Nhịp chậm→nhanh chưa chứng minh được vì thiếu breakdown và F20–F24 chưa có ảnh.

| # | Mức | Ở đâu | Đang thấy | Nên thấy / sửa |
|---|---|---|---|---|
| 1 | A | F16–F34, cam game | Chưa có ảnh cam top-down. Trượng dựng trước mặt xoay trong mặt phẳng trước ngực: từ trên chỉ còn vạch ngang ngắn, 2 vòng xoay gần như không đọc được ở ~60–70 px | Chụp top-down F16/F18/F20/F22/F24. Nếu dẹt: nghiêng mặt phẳng xoay ra khoảng 20–30° (đầu trượng quét chéo trước-phải) hoặc nâng hông/đẩy thân để vạch dài hơn. Đừng chốt trước khi thấy ảnh |
| 2 | A | F16 | Từ cam persp (nhìn từ sau/chéo) trượng gần như bị thân và đầu che, chỉ thấy đầu trượng cạnh đầu; không xác nhận được "dựng trước mặt", trượng có thể sát/chạm đầu | Chụp lại F16 từ trước và từ bên; đo cán cách đầu ≥ 10 cm |
| 3 | A | F12 | Trượng quét ngang sang phải, thân trượng đi qua trước ngực, mũi trượng có vẻ cắt gần thân/tay trái (xuyên thân?) [mắt] | Đo khoảng cách trục trượng tới ngực/bụng; nếu < ~5 cm dời tay ra trước 5–10 cm |
| 4 | B | F8→F12→F16 | Có 3 pose lớn nhưng F8→F12 (4F) quét cả cung rộng sang phải rồi F12→F16 hạ lại: "chậm và ít" mà F12 là pose xa nhất và khá to. Ref Lux cũng quét rộng nhưng user bảo chậm/ít | Giảm biên độ F12 (đầu trượng ra ngoài vai ít hơn ~30%) và thêm breakdown F10, F14 để thấy gia tốc, hoặc để F12 hold lâu hơn F8 |
| 5 | B | F16 | Số đo tầm với 0,38 m ổn (<0,42). Đuôi trượng thấp nhất 0,12 m: sát đất, ở top-down và chân tạo cảm giác chạm | Nâng tay thêm vài cm hoặc nghiêng trượng ra trước; nhớ đo lại sau khi sửa #1 |
| 6 | B | F16→F34 | Hông hạ 4,5 cm, đổ 15° ổn; nhưng toàn bộ xoay 2 vòng + hold 10F là thân cứng, vai/ngực không phản ứng | Thêm vai phải nhấc/ngực xoay theo ~2–3 cm ở F18–F24; tay trái giơ có thể lắc nhẹ cân bằng |
| 7 | C | F34→F44 | Chưa có đoạn về: 10F từ pose đẩy thẳng về Idle sẽ giật | Thêm 1 key hạ trượng chéo thấp (như ref f46–f58) ở ~F38 |
| 8 | C | tổng thể | Vải/áo choàng chưa có (để polish, đúng thứ tự) | Sau khi chốt thân/trượng |

### Trả lời câu hỏi
1. Chưa đủ để gửi duyệt: lỗi A là #1–#3 (thiếu cam game, F16 không xác nhận được, F12 có thể xuyên thân).
2. Chưa chắc ra "chậm và ít": F12 là pose rộng nhất, cần giảm hoặc thêm breakdown. Quét sang phải theo ref là hợp lý về hướng, nhưng ref là nhịp nhanh.
3. Không chấm được. Rủi ro cao ở top-down.
4. Tầm với 0,38 ổn; đuôi cắm đất không (0,12 m) nhưng sát; xuyên thân F12 nghi ngờ; cán-đầu F16 chưa xác nhận.
5. Thứ tự hông→thân→tay→trượng hợp lý; thiếu pha vai (#6) và vải.

### Giữ nguyên
- F8 lấy đà đọc rõ (ngả sau, trượng lên-sau, tay trái giang). Hông hạ + đổ trước ở F16, trọng tâm chân phải. Tay trái giơ cân bằng như ref. Giải xoay bằng Weapon_R, tay đứng yên.

### Cần animator render
- Cam game top-down: F8, F12, F16, F18, F20, F22, F24, F34 (≥ 512 px)
- Cam bên phải và cam trước: F8, F12, F16, F20 
- F0 và F44 để so với Idle

### Ghi chú kỹ thuật
- [mắt] toàn bộ lỗi trên dựa ảnh persp F08/F12/F16 (ảnh F18 không đọc kèm). Số đo (0,38; 0,12; 0,23) lấy từ animator, chưa kiểm.
- Euler ry ±88° gimbal: key từng frame đã ghi; cần verify muted vs on khi thêm layer.
- Lỗi khoảng cách cán-đầu "≥17 cm" đo bản cũ, F12/F16 mới chưa đo lại.
