# Định hướng không gian (bước 2 của vfx-shader; bắt buộc)

Art lead, 2026-11-02: "vẫn phải xác định không gian như chúng ta đã làm; khi tôi yêu cầu tạo fx thì phải **hỏi** nếu cảm thấy chưa đủ thông tin về không gian."

Mục tiêu: trước khi lập kế hoạch hay viết code, phải biết rõ **effect nằm ở đâu trong game, to bao nhiêu, nhìn từ đâu, chạy theo thời gian ra sao, gồm những lớp nào**. Thiếu bước này thì effect đúng kỹ thuật nhưng sai quy mô hoặc sai góc nhìn. Ví dụ: Meteor bản đầu bị nhỏ, không rõ camera.

Nguồn: bản sao của `vfx-maker/references/direction.md` (2026-11-03). Luật không gian (không dùng Horizontal / Vertical Billboard, camera mặc định 3/4 nhìn xuống 40°) giống vfx-maker; nếu hai bản lệch nhau thì theo vfx-maker.

## 1. Phân tích brief (tự làm, không hỏi)

Đọc mô tả, ảnh/video tham chiếu (Read) và JSON Shape Lab nếu có. Viết gọn:
- **Effect là gì:** vai trò gameplay (đòn đánh, buff, cảnh báo, trang trí) và cảm giác chính (mạnh/nhẹ, nhanh/chậm, nóng/lạnh).
- **Tâm điểm:** phần nào phải đọc rõ nhất, phần nào là phụ.
- **Hướng lực:** rơi xuống, toả ra, bay thẳng, xoáy, bốc lên.
- **Nguồn của từng thông tin:**
  - *đã chốt*: người dùng nói;
  - *quan sát được*: thật sự thấy trong ảnh;
  - *đề xuất*: Claude tự đề ra;
  - *chưa rõ*.

  Không nâng đề xuất thành lựa chọn của người dùng. Ảnh tĩnh không cho biết timing.

## 2. Không gian hoạt động (luôn xác định)

| Mục | Lựa chọn | Quyết định gì |
|---|---|---|
| **Ngữ cảnh** | `air` (trúng giữa không) · `ground` (tại đất) · `dir` (có hướng đòn) | Bố cục: toả cầu / nằm đất / nón theo hướng. Chọn biến thể thành phần (`*_Air` / `*_Ground` / `*_Dir`) |
| **Mặt phẳng** | đứng quay về camera (Billboard) · nằm đất (**Billboard + Render Alignment Local**, GameObject xoay X 90°, hoặc World) · đứng/bay theo hướng (**Stretched Billboard**, texture ngang, hướng bay = mép TRÁI ảnh) · Mesh | Renderer mode. **Không dùng Horizontal / Vertical Billboard** (một số game không render được; art lead 2026-10-31) |
| **Góc camera game** | 3/4 nhìn xuống 40° (mặc định dự án) · top-down · ngang (side) · sau lưng · UI | Hướng quad, độ dẹt của vòng nằm đất (vòng vuông góc hướng đòn bị nhìn từ cạnh thì nghiêng ~50°), hướng đèn khi tô sáng, camera preview |
| **Neo** | điểm trong thế giới · bám nhân vật/bone · bám vũ khí · nối 2 điểm (nguồn → đích) · màn hình (UI) | Simulation space Local / World, follow, pivot |
| **Quy mô** | so với người cao 2 m: nhỏ < 0.5 m · vừa 1–2 m · lớn 3–6 m · rất lớn > 6 m | Start Size, nét mảnh nhất còn đọc được ở cỡ màn hình, overdraw |
| **Di chuyển** | đứng yên · bay thẳng · quỹ đạo cong/rơi · bám mục tiêu | Velocity/script, có để lại vết (World) không |
| **Nền phía sau** | tối · sáng · nhiều màu | Additive chỉ hợp nền tối. Nền sáng / lẫn thì dùng Alpha hoặc thêm viền tối |

## 3. Thời gian

- Kiểu phát: **một lần** (impact, nổ) / **lặp** (aura, lửa) / **bay + chạm** (projectile).
- Thời lượng tính bằng giây. Nếu có gameplay: mốc hiệu lực (ví dụ chạm đất ở 0.9 s).
- Nhịp: **chuẩn bị → đỉnh → tan**. Fast attack, slow release: frame sáng nhất ở đầu đỉnh.

## 4. Thành phần (lớp)

Đề xuất danh sách lớp theo loại effect, cho người dùng tích chọn. Không tự thêm damage, rung camera, decal hay mảnh vỡ nếu chưa được chọn.

| Loại effect | Lớp thường có | Câu hỏi rẽ nhánh |
|---|---|---|
| Nổ / impact | Flash (Impact) · Glow · Ring · Sparks · Dust | Trên không hay sát đất? Có hướng không? |
| Projectile | Thân · Đuôi/trail · Tia bắn theo · Quầng · Impact khi chạm · Khói | Quỹ đạo thẳng hay cong? Chạm đất hay trúng mục tiêu? |
| Beam / sét | Thân tia · Lõi · Đầu phát · Điểm trúng · Nhánh | Liên tục hay theo nhịp? |
| Aura / buff / shield | Vòng chân · Màn bao · Hạt bay lên · Viền sáng · Bật/tắt | Bám nhân vật hay đứng yên? |
| AoE / cảnh báo | Vùng đất · Viền · Đếm ngược · Kích hoạt | Tròn / quạt / chữ nhật? |
| Slash | Vệt chém · Mép sáng · Mảnh vụn · Flash điểm trúng | Theo vũ khí (mesh + UV) hay vệt cố định? |
| Lửa / khói loop | Thân · Lõi · Tàn lửa · Khói · Quầng | Hướng bốc? Tắt dần khi dừng? |

Đòn trúng / nổ: dùng **thành phần chuẩn + auto mix** (SKILL.md mục 9, `references/mix.md`). Một effect chỉ một ngữ cảnh và một chớp va chạm.

## 5. Phong cách và màu

- **Art Style** (bắt buộc có trạng thái rõ): Stylized · Anime/cel · Realistic · Hand-painted · Pixel art · Theo dự án/tham chiếu · "Tuỳ Claude" (thì ghi *đề xuất*).
- Bảng màu 3 ô: Core / Mid / Outer. Khói/bụi dùng ô Dust.

## 6. Cách hỏi

- Chỉ hỏi những gì **làm thay đổi thiết kế** và brief chưa trả lời. Mục đã có đáp án thì bỏ.
- Gom vào **tối đa 2 lượt**. Ưu tiên `AskUserQuestion`: ≤ 4 câu mỗi lượt, `multiSelect` cho các lớp độc lập. Có thể dùng bảng chọn `show_widget` (module `elicitation`).
- **Không gian còn mục "chưa rõ" thì phải hỏi, không tự đoán.** Mục nhỏ không ảnh hưởng hình (ví dụ nền khi mặc định tối) thì ghi *giả định* trong kế hoạch.
- Lựa chọn chưa gửi không phải là đáp án.

## 7. Kết quả đưa vào kế hoạch (mục 2 SKILL.md)

Thêm một dòng **Không gian** vào đầu kế hoạch, ví dụ:

`Không gian: ground · nằm đất + đứng (Billboard+Local / Billboard) · camera 3/4 40° · 4.4 m · neo điểm đất · nền lẫn (đã chốt: ground, 3/4; đề xuất: 4.4 m)`
