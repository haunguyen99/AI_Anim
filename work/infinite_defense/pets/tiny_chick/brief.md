# Việc: GEK-2357 — Pet 13 Tiny Chick (Gà Con Vỏ Trứng): rig + anim idle + attack (game Infinite Defense, việc cha GEK-2273)

Bạn làm MỘT Pet này trong Frolvy riêng, cổng **9882** (đã mở sẵn, trống). Các agent khác đang dùng cổng khác (9877 của phiên chính, 9879/9881 của Pet 11/12): đừng đụng.

## Đọc trước (đã có người làm 2 con, học từ đó, đừng làm lại từ đầu)
- work/infinite_defense/pets/mecha_pup/report.md: quy trình rig + skin + bẫy Frolvy đã gặp. Script dựng lại: work/infinite_defense/pets/mecha_pup/rig/ (make_fit.py, skin.py) và anim/ (idle.py, attack.py, make_clips.py): copy ý tưởng, sửa cho gà.
- work/infinite_defense/pets/pebble_turtle/report.md (cách xử lý mesh nằm nghiêng, rig FK).
- Luật rig game: .claude/skills/frolvy_auto_rig/ và frolvy_rig/ (chỉ joint DEF, tối đa 4 influence, Root_M là hông). Luật anim: .claude/skills/animation/knowledge/CORE.md. Sửa bằng layer cộng, không key thẳng Base (memory feedback-edit-on-layer).

## LUẬT RIÊNG CỦA PET (người dùng, 2026-11-11): MỌI PET BAY LƠ LỬNG
- Không tiếp xúc đất: không khoá chân xuống đất, không tiếp đất. Thân hover ~12 cm, chân/cánh thả lủng lẳng và trễ theo thân. "Nhún nhảy" trong GDD = bồng bềnh.

## Đầu vào
- Mesh: C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_13_Tiny_Chick\Pet_Tiny_Chick.fbx. Chưa biết có xương/skin chưa: kiểm trước, rồi nhập vào Frolvy; mesh có thể nằm nghiêng (xem báo cáo Pebble Turtle).
- GDD: work/infinite_defense/gdd/tab.csv, dòng ID 13. Tóm tắt:
  - Hình khối bông xù tròn xoe, gà con trong vỏ trứng.
  - Socket bắn đạn (Muzzle): đầu mỏ nhọn.
  - Idle: lắc mông khiến vỏ trứng va chạm lách cách (LẶP liền mạch, theo hướng bay lơ lửng).
  - Attack: nhảy cẫng lên, rướn người mổ mạnh phóng đạn (có key rõ tại frame bắn để gắn event; "nhảy" = vút lên khi lơ lửng, không tiếp đất).
- Không có clip di chuyển.

## Cách làm
- Điều khiển Frolvy: `.venv/Scripts/python.exe -I tools/frolvy_port.py 9882 <file.py>` (xem đầu file đó; lệnh nhanh: `... 9882 scene`). KHÔNG dùng công cụ MCP frolvy có sẵn (nó nối vào cổng 9877 của phiên khác).
- Thứ tự: (1) rig: thân, đầu, mỏ (+ socket Muzzle ở đầu mỏ), cánh/chân, vỏ trứng (xương riêng để va lách cách); build rig; xoay thử kiểm skin. (2) idle ~48 frame lặp, (3) attack ~24–30 frame, ghi frame bắn. Cuối attack về đúng tư thế idle frame 0.
- Lưu mọi file làm việc (.fv, bản lưu, FBX xuất `Pet_Tiny_Chick@Idle.fbx` / `@Attack.fbx`, playblast) ở C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_13_Tiny_Chick\. Script đặt ở work/infinite_defense/pets/tiny_chick/.

## Xong là gì
- work/infinite_defense/pets/tiny_chick/report.md: rig có gì, số frame idle/attack, frame bắn, đường dẫn file đã lưu, chỗ vướng hoặc chưa chắc. Lời thường, không dán code dài.
- Mesh không dùng được hoặc Frolvy không điều khiển được: dừng, ghi `CHẶN: <câu hỏi>` kèm lý do cụ thể, đừng đoán.
- Không commit, không đổi nhánh, không đẩy GitHub. Trả lời tiếng Việt.
