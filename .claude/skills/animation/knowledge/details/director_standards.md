# Tiêu chuẩn duyệt của người dùng (Director tự học)
Director (`.claude/agents/animation-director.md`) đọc file này **trước khi chấm**. File tự lớn dần theo quyết định thật của người dùng, không cần người dùng viết tay (user 2026-10-30: "cứ tự học trong quá trình làm việc").

## Cách học (animator/phiên chính làm, không đợi nhắc)
Mỗi khi người dùng **duyệt** hoặc **trả** một bản đã có bài chấm trong `director_log.md`:
1. So kết luận người dùng với kết luận Director của bản đó.
2. Ghi một dòng vào mục `#calibration`: `<ngày> | <clip> <ver> <mốc> | Director: <kết luận, lỗi chính> | User: <kết luận + câu gốc> | Bài học`.
   - **User duyệt, Director chê** → lỗi đó KHÔNG chặn duyệt ở loại clip/game này: hạ mức (A→B, B→C) trong `#severity`.
   - **User trả, Director duyệt hoặc không thấy** → Director bỏ sót: thêm vào `#blockers` (cái user bắt, câu gốc, cách đo được).
   - **Hai bên trùng** → ghi "khớp", tăng độ tin cho luật liên quan.
3. Một luật lặp lại ≥ 2 lần (2 clip khác nhau) mới được ghi là **[đã xác nhận]**; trước đó là **[suy ra]**.
4. Thêm một dòng vào `director_log.md` của clip: `User: <kết luận> (<ngày>) – <câu gốc>`.
Không có bài chấm Director (clip làm trước 2026-10-30) thì vẫn học được từ git log (`approved`/`rejected` trong commit, tag `*-approved`).

## blockers
Lỗi người dùng **đã từng trả bài** (mức A mặc định):
- Pose không giống ref/key đã duyệt khi so cạnh nhau (Gaygor Attack v2 "không pose nào giống ref") [đã xác nhận]
- Tay/vai xoắn, khuỷu gập quá, khuỷu lật vào hông (Attack f13; SDR03 Shoot b2 F2/F4/F6/F7) [đã xác nhận]
- Chuyển động không đọc được ở camera game, quá nhỏ (SDR03 Shoot b1 "recoil too small to read at game cam") [suy ra]
- Bàn chân lún sàn (Gaygor Walk b3), đùi xoắn tụt giữa các frame (Walk b16 F23–F28) [đã xác nhận]
- Sai khác so với file blocking của team (Gaygor Attack 50 b50_v1, sai thứ tự xoay FBX) [suy ra]
- Hướng sửa mò nhiều vòng làm hỏng bản cũ (SDR Idle v16–v18 "quá tệ, quay lại v4") → đề xuất ảnh tĩnh để chọn [đã xác nhận]

Rig / skin:
- Khớp đặt "nằm giữa" thay vì theo giải phẫu mesh, dùng nguyên bộ khớp rig cũ cho thân khác (Zom2 Map3, user: "Các khớp chưa đúng vị trí") [suy ra]
- Skin khuỷu xấu ở góc gập thật của P0 (SDR01 2026-10-29, user khoanh khuỷu phải: "check lại skin") → kiểm ở góc hay dùng, ảnh cận 3 góc [suy ra]
- Skin chỉ đẹp một bên (Hammer chỉ sửa bên phải, quên `mirror_skin.py`) [suy ra]

## severity
Lỗi người dùng **đã bỏ qua khi duyệt** (hạ mức khi chấm loại tương tự):
- SDR01 Shoot s1 (side-view mobile, ném dao 30 F) được duyệt + xuất dù Director (chấm sau, 2026-10-30) ghi: đầu vặt 31° quanh lúc thả, găng che mặt F7–F8, tay ngắm co 119°, lấy đà yếu, chân sau không nhấc gót. [suy ra – chưa rõ user không thấy hay chấp nhận; hỏi khi có dịp]

## calibration
| Ngày | Clip / ver / mốc | Director | User | Bài học |
|---|---|---|---|---|
| 2026-10-30 | sdr01_shoot s1 pre-export | Cần sửa (A: đầu vặt 31° F6–F7; 5 lỗi B) | Đã duyệt + xuất 2026-10-29 (chấm sau) | Ngưỡng của user với clip nhỏ side-view thấp hơn Director → chưa đổi mức, chờ thêm 1 ca |
