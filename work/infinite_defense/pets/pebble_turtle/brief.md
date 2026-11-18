# Việc: GEK-2356 — Pet 12 Pebble Turtle (Rùa Đá): rig + anim idle + attack (game Infinite Defense, việc cha GEK-2273)

Bạn làm MỘT Pet này trong Frolvy riêng, cổng **9881** (đã mở sẵn, trống). Có một agent khác đang làm Pet 11 Mecha Pup ở cổng 9879: đừng đụng cổng đó, cũng đừng đụng 9877/9878/9880.
Nếu xong rồi mà muốn học cách làm, đọc work/infinite_defense/pets/mecha_pup/report.md (nếu đã có) để dùng chung mẹo.

## Đầu vào
- Mesh: C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_12_Pebble_Turtle\Pet_Pebble_Turtle.fbx (bản gốc ở Unity: ...\endless-kicker\Assets\Kho\Skin\mesh\Pet_new\mesh). Chưa biết FBX có xương/skin chưa: kiểm trước, rồi nhập vào Frolvy.
- GDD: work/infinite_defense/gdd/tab.csv, dòng ID 12. Tóm tắt:
  - Hình khối bầu tròn mập mạp, rùa đá.
  - Socket bắn đạn (Muzzle): miệng rùa.
  - Idle: đung đưa thân tròn, thỉnh thoảng rụt đầu nhẹ (LẶP liền mạch).
  - Attack: rụt đầu vào mai lấy đà, bật mạnh đầu ra khạc sỏi (key rõ tại frame khạc để gắn event).
- Không có clip di chuyển (GDD không mô tả).

## Cách làm
- Điều khiển Frolvy: `.venv/Scripts/python.exe -I tools/frolvy_port.py 9881 <file.py>` (xem đầu file đó; lệnh nhanh: `... 9881 scene`). KHÔNG dùng công cụ MCP frolvy có sẵn (nó nối vào cổng 9877 của phiên khác).
- Đọc skill rig: .claude/skills/frolvy_auto_rig/ và frolvy_rig/ (luật rig game: chỉ joint DEF, tối đa 4 influence, Root là hip...). Luật anim: .claude/skills/animation/knowledge/CORE.md. Sửa bằng layer cộng, không key thẳng Base (memory feedback-edit-on-layer trong .claude/memory_store).
- Thứ tự: (1) rig: 4 chân, thân/mai, đầu + cổ (rụt được vào mai, chú ý skin để đầu không xuyên mai), socket Muzzle ở miệng; build rig; xoay thử vài khớp kiểm skin. (2) idle ~40–60 frame lặp, (3) attack ~30–40 frame, ghi frame khạc.
- Lưu mọi file làm việc (.fv, bản lưu, FBX xuất, playblast) ở C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_12_Pebble_Turtle\.

## Xong là gì
- File báo cáo work/infinite_defense/pets/pebble_turtle/report.md: rig có gì, số frame idle/attack, frame khạc, đường dẫn các file đã lưu, chỗ vướng hoặc chưa chắc, lệnh nào lỗi. Lời thường, không dán code dài.
- Mesh không dùng được hoặc Frolvy không điều khiển được: dừng, ghi `CHẶN: <câu hỏi>` kèm lý do cụ thể, đừng đoán.
- Không commit, không đổi nhánh, không đẩy GitHub. Trả lời tiếng Việt.
