# Prompt ChatGPT (tiếng Việt): bảng ref nhiều góc cho pose Idle Ninja (F1, đáy thở)

Nguồn: `../analysis.md` (mục A–C, I). Bản tiếng Anh: `chatgpt_ref_sheet_prompt.md`.

**Đính kèm khi gửi ChatGPT, đúng thứ tự:**
1. `k1r2_v1.png`: ảnh concept đã chốt (mẫu pose)
2. `ref/ninjafront.png`, `ref/ninjaside_l.png`, `ref/ninjaback.png`: render model thật ở góc vuông (tạo hình + góc camera)
3. `ref/kunaiside_r.png`: kunai

**Mẹo:** nếu ChatGPT đổi pose giữa các ô, nhắn một câu: "Cùng một mô hình, chỉ đổi camera. Chép đúng mọi góc khớp từ ô số 5."

---

Hãy tạo MỘT ảnh bảng tham chiếu nhân vật (khổ ngang 16:9, 3 cột x 2 hàng, sáu ô bằng nhau, viền ô mảnh màu xám nhạt, mỗi ô có nhãn nhỏ nền trơn bên dưới). Bảng chỉ có MỘT nhân vật 3D, trong MỘT pose đóng băng: tư thế Idle thủ thế của hero "Ninja" trong game mobile tower-defense thân thiện. Nhân vật và đạo cụ phong cách đồ chơi cách điệu.

QUY TẮC QUAN TRỌNG NHẤT: coi nhân vật là một mô hình tượng 3D đứng yên trên bàn xoay. Cả sáu ô là CÙNG một mô hình với CÙNG một pose. Chỉ có camera di chuyển. Mọi góc khớp, độ rộng tấn, chân nào ở trước, vị trí hai tay, góc kunai và hình dạng khăn phải giống hệt nhau giữa các ô. Không đổi pose, không làm pose đối xứng, không "sửa cho đẹp" theo từng góc nhìn.

TẠO HÌNH NHÂN VẬT (khớp đúng ảnh render model đính kèm): tỉ lệ chibi, cao khoảng 4 đầu (đầu bằng 1/4 chiều cao), đầu tròn rất to không có chi tiết mặt, thân trắng low-poly mịn tô phẳng, tay ngắn (cánh tay + cẳng tay chỉ dài hơn chiều cao đầu khoảng 1,2 lần), bàn tay kiểu găng, khăn đỏ quấn cổ với HAI đuôi khăn đỏ dài.
KUNAI (khớp ảnh render kunai đính kèm): lưỡi thép sẫm hình thoi, chuôi quấn đỏ, vòng nhỏ sẫm ở đuôi. Kunai rất lớn so với nhân vật: riêng phần lưỡi đã dài hơn cả cánh tay.

POSE (đáy một nhịp thở êm, thế thủ sẵn sàng; "trái" và "phải" là bên của chính nhân vật):
- Thế đứng: khom, gối gập rõ và hướng theo mũi chân, hai chân rộng hơn hông rõ rệt (khoảng 2 lần bề rộng hông). Chân TRÁI hơi lên trước, mũi chân hướng về địch; chân PHẢI ở sau, mũi chân mở ra khoảng 30 độ. Cả hai bàn chân đặt phẳng trên sàn.
- Hông hạ thấp, xương chậu xoay nhẹ để vai TRÁI dẫn về phía địch.
- Thân đổ về trước khoảng 12 độ từ hông, lưng cong đều, không gù; ngực xoay lại nhẹ về phía người xem.
- Đầu nhìn thẳng về phía địch, cằm hơi cúi.
- Tay TRÁI cầm kunai kiểu CẦM NGƯỢC (kiểu cầm dao găm): nắm tay đặt trước ngực trên, ngay dưới khăn, cách người khoảng một cẳng tay; khuỷu trái gập và chỉ ra ngoài, hơi chúc xuống. Lưỡi kunai đi ra từ phía ngón út của nắm tay, chạy ra sau và xuống dọc phía ngoài cẳng tay trái, chúc khoảng 30 độ dưới đường ngang; mũi lưỡi kết thúc cạnh hông trái, nằm ngoài thân, không chạm chân hay thân.
- Tay PHẢI để TRỐNG, nắm hờ như đang cầm một kunai vô hình kiểu cầm ngược; cánh tay phải đẩy ra sau, khuỷu gập nhẹ, nắm tay nằm cạnh và hơi lùi sau hông phải, tách khỏi thân.
- Khăn: gió rất nhẹ. Hai đuôi khăn rủ sau lưng theo đường cong chữ S mềm, chúc xuống nhẹ, tách nhau một chút, không chạm đất và không chạm chân.

SÁU Ô (giữ nhân vật cùng kích thước và hai bàn chân cùng một đường sàn nằm ngang ở các ô 1–4):
1. "FRONT" (chính diện): hình chiếu trực giao chính diện hoàn toàn, camera ngang tầm giữa thân, nhìn ngang theo hướng hông quay về, không phối cảnh. Tay cầm kunai nằm bên PHẢI của ô.
2. "LEFT SIDE" (bên trái): hình chiếu trực giao nhìn ngang đúng 90 độ từ bên trái nhân vật (phía có kunai); nhân vật quay mặt về mép TRÁI của ô. Tay phải và chân phải gần như khuất sau thân.
3. "BACK" (sau lưng): hình chiếu trực giao nhìn từ sau, thấy rõ hai đuôi khăn.
4. "RIGHT SIDE" (bên phải): hình chiếu trực giao nhìn ngang đúng 90 độ từ bên phải nhân vật (phía tay không); nhân vật quay mặt về mép PHẢI của ô.
5. "3/4 FRONT" (chéo trước): góc có phối cảnh từ phía trước-trái, ngang tầm mắt, giống ảnh concept đầu tiên đính kèm.
6. "GAME CAMERA" (camera game): camera game mobile tower-defense, nhìn XUỐNG 45 độ từ trên cao phía sau-bên phải, nhân vật quay mặt về phía trên của ô; đường kunai và hai cánh tay tách rõ khỏi hình bóng thân.

PHONG CÁCH: cùng cảm giác 3D low-poly trắng tô phẳng như ảnh tham chiếu, nền xám trung bình trơn phẳng ở mọi ô, ánh sáng phẳng đều, chỉ có bóng tiếp xúc rất nhẹ dưới chân, không có chữ nào ngoài sáu nhãn ngắn, không thêm nhân vật, không thêm vũ khí, không hiệu ứng.
