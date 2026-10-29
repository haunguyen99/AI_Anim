# Pose Lab: vật lý giai đoạn 1 (lò xo phụ kiện và bake)

Đã duyệt 2026-10-24 ("làm tiếp theo đề xuất": lớp vật lý sống, có dải ghim theo frame, chuỗi nhiều đốt để sau). **Đã làm xong**, xem mục 11.

## 1. Mục tiêu

Biến các bước polish làm tay bằng script cho Gaygor Hit (polish_v3 đến v7) thành công cụ trên Pose Lab. Animator chọn phần cần mềm, chọn độ nặng, xem ngay, rồi xuất FBX hoặc bake thành key.

**Trong giai đoạn 1:**
- Lò xo cho từng khớp: vai, khuỷu, cổ tay, đầu, vạt khố.
- Vật cầm tay: chùy lắc quanh tay nắm, tay bám lại cán.
- Vùng chắn hình cầu, ví dụ vai đỡ chùy.

**Ngoài giai đoạn 1:** va chạm cả thân bằng hình con nhộng, trọng tâm và cân bằng, gợi ý phản ứng trúng đòn, ragdoll.

## 2. Cách chạy

```
key → spline → khóa chân → chặn sàn → chùy bám vai/tay → [LỚP VẬT LÝ] → hiển thị / phát / playblast / xuất FBX
```

- **Mô phỏng chạy một lượt từ F1 tới frame cuối**, vì lò xo cần biết các frame trước. Kết quả lưu vào bộ nhớ đệm cho từng frame.
- **Đổi key hoặc thông số** thì tính lại cả clip. Với 32–133 frame và khoảng 10 phần, mất dưới 0,2 giây, nên kéo thanh trượt là thấy ngay.
- **Nút Bật/Tắt vật lý** để so trước và sau.
- **Xuất FBX lấy luôn kết quả vật lý**, không cần bake.
- **Bake thành key** chỉ dùng khi muốn sửa tay tiếp trên kết quả: ghi mọi frame thành key rồi tắt lớp vật lý. Có hoàn tác.

## 3. Các thành phần

| Loại | Cách hoạt động | Ví dụ Gaygor |
|---|---|---|
| **Khớp mềm** | Xương giữ hướng của nó trong thế giới và đuổi theo pose của key bằng lò xo, nên tự trễ, vượt rồi lắng | Vai phải, bả vai, cổ tay, đầu, DressFront/Back |
| **Khớp bản lề** | Như khớp mềm nhưng chỉ gập theo trục bản lề | Khuỷu tay, đầu gối nếu cần |
| **Đung đưa khuỷu** | Với tay đang nắm vật: khuỷu xoay quanh trục vai→cổ tay, bàn tay giữ nguyên | Khuỷu trái (tay nắm chùy) |
| **Vật cầm tay** | Vật xoay quanh điểm nắm, bàn tay IK lại lên cán | Chùy (xương Weapon) |
| **Vùng chắn** | Hình cầu gắn vào xương. Vật không được lại gần hơn khoảng lúc nghỉ (tự đo từ pose F1). Có đệm mềm 2,5 cm | Vai trái đỡ chùy |

Phần con được tính sau phần cha (bả vai → vai → khuỷu → cổ tay). Nhờ vậy mọi phần cùng nằm trong một lượt, không phải chồng các lớp lò xo lên nhau.

## 4. Thông số

Mỗi phần có 3 thanh trượt, đặt tên theo cảm giác chứ không theo công thức:

| Thanh | Ý nghĩa | Khoảng |
|---|---|---|
| **Độ nặng** (chu kỳ lắc, frame) | Càng lớn càng chậm, trễ càng lâu | 4–24 |
| **Độ nảy** (= 1 − hệ số hãm ζ) | 0 là không vượt; lớn thì vượt rồi dội lại nhiều lần | 0–0,8 |
| **Giới hạn góc** | Góc lệch tối đa so với pose key, chặn mềm (không gãy góc) | 3–40° |

**Mức có sẵn**, lấy từ các bản Hit đã duyệt:

| Mức | Độ nặng | Độ nảy | Giới hạn | Dùng cho |
|---|---|---|---|---|
| Nhẹ | 8 | 0,62 | 12° | Cổ tay, đầu |
| Vừa | 12 | 0,68 | 15° | Vai, khuỷu, vạt khố (≈ Hit v4/v5) |
| Nặng | 15 | 0,72 | 24° | Chùy (= Hit v7: chu kỳ 15, ζ 0,28) |
| Rất nặng | 20 | 0,75 | 30° | Vũ khí lớn hơn, vật kéo lê |

**Thêm theo từng frame:** một dải "trọng số vật lý" trên timeline, tô giống dải chạm đất, nhận giá trị từ 0 đến 1. Chỗ trọng số 0 thì giữ đúng pose key (ví dụ frame trúng đòn, frame phải khớp gameplay). Chuyển giữa các chỗ bằng đường cong êm.

## 5. Quy tắc (bài học từ Hit)

1. **Lò xo đuổi theo chuyển động của key, không làm mượt trước.** Đích đã làm mượt thì không còn chỗ dừng để vượt qua; Hit v6 chỉ vượt 0,4°.
2. **Va chạm nằm trong mô phỏng**, dạng đệm mềm. Đẩy vật ra sau mô phỏng gây bật 20–25° (Hit v7, các lần thử đầu).
3. **Luôn tính từ pose của key**, không chồng lò xo lên kết quả lò xo.
4. **Kết thúc clip:**
   - Clip một lần: N frame cuối (mặc định 8) trở về đúng pose key bằng đường cong êm (smoothstep), để frame cuối khớp Idle F1.
   - Clip lặp: chạy 2 vòng, lấy vòng sau, để chỗ nối vòng không giật.
5. **Bước con:** 8 bước con mỗi frame, để chuyển động nhanh (trúng đòn 8–12°/frame) vẫn ổn định.

## 6. Giao diện

Thêm thẻ **Vật lý** trong bảng bên phải:
- Nút Bật/Tắt; danh sách thành phần; nút "+ Thêm từ xương đang chọn" (tự đoán loại: Elbow/Knee là bản lề, xương có vật cầm là vật cầm tay).
- Mỗi thành phần có 3 thanh trượt, chọn mức có sẵn, và nút "Chỉ xem phần này".
- **Đồ thị tốc độ** của phần đang chọn theo frame, có cả đường của key để so. Tự đánh dấu chỗ "dừng rồi chạy", rung và ngoặt gắt bằng cùng phép đo đã dùng cho Hit.
- Dải trọng số vật lý dưới dải chạm đất.
- Nút **Bake thành key**.

## 7. Lưu và chia sẻ

- Thông số lưu cùng thiết lập anim của version (db `anims`, trường `phys`). AI đọc được để làm tiếp hoặc chạy lại bằng Python.
- Mức có sẵn theo nhân vật lưu trong `work/<nv>/phys_presets.json`, để clip sau của Gaygor dùng lại.
- Một bản Python dùng cùng công thức (tách từ `work/boss_gaygor/gaygor_hit/polish_v7.py`) để kiểm chéo: cùng thông số phải ra cùng kết quả, sai lệch dưới 0,1°.

## 8. Nghiệm thu

- **Dựng lại Hit:** từ key của polish_v2, bật vai, khuỷu, cổ tay phải, khuỷu trái và chùy với các mức có sẵn. Kết quả phải giống v7:
  - chùy trễ khoảng 14° lúc trúng đòn;
  - vượt khoảng 16° ở F14–F18;
  - dội lại khoảng 7°;
  - khe vai ≥ 8,5 cm;
  - không rung, không bật.
- Kéo một thanh trượt, kết quả cập nhật trong khoảng 0,2 giây.
- FBX xuất từ trang khớp cache vật lý (lệch dưới 0,001 cm).
- Áp lên Attack 50 polish_v3 và Walk mà không lỗi: dải trọng số và kết thúc clip hoạt động cả cho clip lặp.

## 9. Cần bạn quyết

1. **Mặc định khi mở clip:** lớp vật lý sống (sửa key là phụ kiện tự theo) hay phải bake? Đề xuất: sống.
2. **Dải trọng số theo frame:** có cần ngay trong giai đoạn 1 không? Đề xuất: có, vì frame trúng đòn và frame gameplay cần giữ đúng pose.
3. **Chuỗi nhiều đốt** (tóc, đuôi, dây): Gaygor chưa cần. Để giai đoạn sau hay làm luôn?

## 10. Ước lượng

- Lõi mô phỏng trong trang và kiểm chéo với Python: 1 buổi.
- Giao diện (thẻ, thanh trượt, đồ thị, dải trọng số, bake): 1 buổi.
- Nghiệm thu trên Hit, Attack, Walk, rồi cập nhật tài liệu: nửa buổi.

## 11. Đã làm (2026-10-24)

- **Code:** `work/pose_lab/index.html`, phần "physics layer": `computePhysCore`, `applyPhys`, `unphys`; giao diện ở phần "physics panel". Bản Python giống hệt: `tools/physics_sim.py <dump.json> [--compare]`.
- **Đúng như thiết kế:**
  - 4 loại thành phần, 3 thanh trượt, 4 mức, nút "Mức của nhân vật" (`CHAR_PHYS` trong trang; trang artifact không đọc được file trên máy, nên mức có sẵn nằm trong code thay vì file `phys_presets.json`);
  - dải "ghim pose" màu vàng trên timeline;
  - N frame cuối trả về pose key; clip lặp chạy 2 vòng;
  - đồ thị tốc độ;
  - Bake.
- **Khác thiết kế, do đo được khi làm:**
  - **Va chạm** là ràng buộc không nảy, không phải đệm mềm:
    - đệm mềm của v7 (2,5 cm) để lưới chùy thật của trang lún 2,7 cm;
    - đệm cứng hơn thì rung;
    - mọi kiểu đệm mềm đều hỗn loạn: nhiễu một phần triệu làm chùy lệch 12°;
    - ràng buộc không nảy (xoay vật ra đúng phần lẹm, bỏ vận tốc lao vào): cùng nhiễu chỉ còn lệch dưới 0,3°, không lơ lửng khi nằm yên.
  - **Sàn:** vật cầm tay luôn có ràng buộc sàn (không thấp hơn 0 hoặc thấp hơn chính pose key).
  - **Bước con:** vật cầm tay 64 bước con mỗi frame, khớp 8.
  - **Bake:** nút đổi thành "Hoàn tác bake". Ctrl+Z không dùng được, vì đổi frame là xóa lịch sử hoàn tác.
  - **Đồ thị:** chỉ báo dừng-rồi-chạy khi không đổi chiều, và chỉ báo chỗ do vật lý thêm vào.
- **Nghiệm thu:**
  - **Hit**, dựng lại từ polish_v2 bằng "Mức của nhân vật" (Gaygor), chùy giống v7:
    - trễ 14° lúc trúng đòn, 21° ở F9;
    - vượt 11° ở F15, dội 4° ở F24;
    - nằm yên từ F28.
  - **Tốc độ tính:** Hit 28 ms, Attack 58 ms, Walk (lặp, 57F) 127 ms.
  - **Kiểm chéo Python và trang:** khớp tối đa 0,0001°; chùy 0,02° (Hit), 0,0004° (Attack).
  - **Attack:** chùy không xuống dưới sàn (0 cm).
  - **Walk:** chỗ nối vòng liền mạch.
  - **Đặt key khi vật lý bật** thì key vẫn là pose gốc (lệch 0°).
  - **Bake rồi Hoàn tác bake** trả lại key đúng (lệch 0°).
- **Đã đăng:** trang Hit, Attack 50 (2026-10-24), Walk (2026-10-25; trên Walk vật lý mặc định tắt, key trong db giữ nguyên).
- **Chưa kiểm:** chưa bấm "Xuất FBX" trên claude.ai với vật lý bật. Xuất FBX dùng chung `sampleAt` nên có vật lý, nhưng chưa mở file ra xem.
