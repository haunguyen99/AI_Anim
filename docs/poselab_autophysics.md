# Pose Lab AutoPhysics (giống Cascadeur), đợt 1

Ngày 2026-10-26. Bạn gửi bảng AutoPhysics của Cascadeur và duyệt đợt 1 ("1").

## Bảng trên Pose Lab

- Nằm trong bảng **Vật lý**, ngay dưới các nút Vật lý / Mức của nhân vật / Bake.
- Gồm 7 dòng như Cascadeur. Mỗi dòng có nút **Bật / Tắt** và thanh **0–100**, mặc định 50.
- Cài đặt lưu ở `ANIM.phys.ap = { traj, rot, sep, sec, pen: { on, v } }`, cùng chỗ với các cài đặt vật lý khác (db `anims`).
- Các lớp chồng lên key, lò xo và tác động, **không sửa key gốc**:
  - bóng mờ vẫn là pose key, để so trước / sau;
  - ưng thì bấm **Bake thành key**.
- Dòng báo dưới bảng ghi số đo của từng lớp: hông dời bao nhiêu cm, khớp xoay bớt bao nhiêu độ, trễ bao nhiêu frame, còn bao nhiêu chỗ xuyên, và thời gian tính.

| Dòng | Đợt | Làm gì |
|---|---|---|
| Hiệu chỉnh vật lý | 2 | trên không: trọng tâm bay parabol, giữ mômen quay; lúc đứng: trọng tâm trong chân |
| Làm mượt quỹ đạo | 1 | lọc Gauss vị trí hông (σ = 0,3 + 1,7·v frame) |
| Làm mượt xoay | 1 | lọc Gauss xoay local (σ = 0,3 + 1,5·v), mỗi frame đổi tối đa 1 + 9·v độ, chỉ gọt giật / rung |
| Chuyển động bù trừ | 2 | thân, tay đưa ngược để giữ thăng bằng |
| Tách nhịp chuyển động | 1 | mỗi cấp trong chuỗi trễ 1,2·v frame, lấy mẫu trên đường xoay của chính khớp đó |
| Chuyển động phụ | 1 | lò xo đã có; chưa có phần nào thì dùng `CHAR_PHYS` của nhân vật; độ lớn × 2·v |
| Xử lý xuyên | 1 | nâng thân khỏi sàn, nâng chân đang nhấc, đẩy tay / chân / đầu ra khỏi thân |

- **Chuỗi trong Tách nhịp:**
  - thân: lưng 1, ngực 2, cổ 3, đầu 4;
  - tay: bả vai 3, vai 4, khuỷu 5, cổ tay 6.
- **Gọt gai cho Chuyển động phụ:** frame nào lệch quá 8° so với điểm giữa hai frame bên cạnh thì được kéo về điểm giữa.

## Ràng buộc (luôn áp, mọi lớp)

- **Clip một lần:** F1 và frame cuối giữ đúng key (các lớp tăng dần vào trong 3 frame). Clip lặp thì lọc vòng.
- **Chân đang chống:**
  - lấy theo dải chạm đất; nếu chưa tô dải thì chân chậm hơn 1,5 cm/F và thấp trong 4 cm là đang chống;
  - chân đang chống được đặt lại đúng chỗ bằng IK;
  - chân "lún" chỉ tính khi thấp hơn mức của chính nó lúc chống. Lưới bàn chân Gaygor vốn nằm thấp hơn 0 khoảng 1,5–2 cm.
- **Vật cầm (chùy):**
  - tay đang cầm = có điểm của chùy nằm trong khối bàn tay + 6 cm, đo trên **pose key**. Đo trên kết quả đã có lò xo thì lò xo đã kéo tay phải lệch 67 cm.
  - một tay cầm: chùy đi theo tay đó, đúng chỗ cầm của frame đó.
  - hai tay cầm: chùy cứng theo ngực như trong key, hai tay IK về chỗ cầm.
  - quanh lúc đổi cách cầm (±4 frame) chùy chuyển dần.
  - quanh lúc chụp / buông chùy (±6 frame) cánh tay đó trả dần về pose key, để tay tới cán đúng chỗ.
- **Xử lý xuyên:**
  - không đẩy cánh tay đang cầm chùy (chỗ cầm thắng);
  - đầu chạm vai thì xoay cổ, không đẩy vai;
  - chùy chạm sàn là của người làm anim, không nâng người;
  - phần chỉnh trải mượt theo thời gian (σ = 2,5 frame): frame cần chỉnh nhận đủ, các frame bên cạnh chuyển êm. Σ = 1,5 làm tay bật 21°/F.

## Đo trên Attack (polish_v3, 68 F) và Hit (polish_v7, 32 F), mức 50

- Thời gian tính: Attack 1,1 giây, Hit 0,2 giây.
- Chùy trong tay trái: lệch 0 cm.
- Tay phải đang cầm cán (48 frame của Attack): lệch 0 cm.
- Xuyên ở Attack: 82 chỗ còn 23 khi chỉ bật Xử lý xuyên; 104 còn 40 khi bật cả 5 mục (Tách nhịp và lò xo tự sinh thêm chỗ chạm).
- Còn lại:
  - Attack F6–F8 (đoạn đổi tay cầm): khuỷu trái tăng giật thêm 12–26°;
  - Hit F13–14: cổ tay phải thêm 20° (lò xo khiên chạm thân).

## Đã học khi làm

- Làm mượt xoay không giới hạn ăn mất cú vung (Attack 25°). Phải giới hạn độ đổi mỗi frame.
- Chú thích `//` chèn giữa một dòng code một dòng làm hỏng cả trang, đã gặp hai lần. Dùng `/* */`, và luôn tải lại trang kiểm `POSES` sau mỗi lần sửa.

## Quỹ đạo khớp (motion trail), 2026-10-26

Bạn: "bật motion trail của 1 joint để check xem nó được làm mềm như nào".

- **Bật:** nút **Quỹ đạo** trên thanh công cụ (phím **T**), rồi chọn một khớp. Hiện đường đi của khớp đó qua cả clip:
  - **xanh lơ** = kết quả đang thấy (key + vật lý / AutoPhysics);
  - **xám nét đứt** = pose key gốc (bóng mờ);
  - mỗi chấm là một frame: chấm thưa là nhanh, chấm dày là chậm; chấm trắng to là frame đang xem;
  - đường vẽ xuyên qua thân để luôn thấy. Màu cam ban đầu lẫn với chấm khớp vàng và thân đỏ nên đã đổi sang xanh lơ.
- **Dòng số đo trên khung 3D:**
  - nhanh nhất (cm/F, frame);
  - đổi hướng gắt nhất (độ, frame);
  - đổi tốc lớn nhất (cm/F, frame), chỗ giật thường nằm ở đây;
  - cùng ba số đó cho đường key;
  - lệch tối đa so với key (cm, frame).
  - Khớp không bị vật lý đổi thì ghi "trùng pose key".
- **Tính lại** khi đổi khớp, đổi key hoặc kết quả vật lý đổi. Không tính lại mỗi frame.
- **Ví dụ** Hit polish_v7, Tách nhịp 70, khớp đầu:

  | | Key | Tách nhịp 70 |
  |---|---|---|
  | Nhanh nhất | 15,8 cm/F | 8,9 cm/F |
  | Đổi tốc lớn nhất | 15,8 cm/F | 4,9 cm/F |
  | Đổi hướng gắt nhất | 158° | 95° |
