# Việc: GEK-2355 — Pet 11 Mecha Pup (Cún Cơ Giáp): rig + anim idle + attack (game Infinite Defense, việc cha GEK-2273)

Bạn làm MỘT Pet này trong Frolvy riêng (cổng 9879, đã mở sẵn, trống). Đây là Pet thử đầu tiên: làm cẩn thận và ghi lại cái gì vướng để các Pet sau làm theo.

## Đầu vào
- Mesh: work/infinite_defense/pets/mecha_pup/Pet_Mecha_Pup.fbx (bản gốc ở Unity: C:\Users\Admin\Documents\Horus\endless-kicker\Assets\Kho\Skin\mesh\Pet_new\mesh). Chưa biết FBX có xương/skin chưa: kiểm trước, rồi nhập vào Frolvy.
- GDD (tab Pet): work/infinite_defense/gdd/tab.csv, dòng ID 11. Tóm tắt:
  - Hình khối tròn trịa ngộ nghĩnh, vàng Shiba + ngọc cơ giáp, mũ phi hành gia, ăng-ten trên balo.
  - Socket bắn đạn (Muzzle): đầu ăng-ten balo.
  - Idle: nhún nhảy 4 chân, ngoáy đuôi, ăng-ten lúc lắc (LẶP liền mạch).
  - Attack: chồm 2 chân trước, ăng-ten chớp điện phóng đạn (có key rõ tại frame bắn để gắn event).
- Không có clip di chuyển (GDD không mô tả).

## Cách làm
- Điều khiển Frolvy bằng: `.venv/Scripts/python.exe -I tools/frolvy_port.py 9879 <file.py>` (xem đầu file đó). Chỉ dùng cổng 9879. KHÔNG đụng cổng 9877/9878 và KHÔNG gọi công cụ MCP frolvy (không có trong phiên này).
- Đọc skill rig: .claude/skills/frolvy_auto_rig/ và frolvy_rig/ (luật rig game: chỉ joint DEF, tối đa 4 influence, Root là hip...). Luật anim: .claude/skills/animation/knowledge/CORE.md. Cách làm lớp sửa: không key thẳng Base, dùng layer cộng (xem memory feedback-edit-on-layer nếu có trong .claude/memory_store).
- Thứ tự: (1) rig: joint 4 chân, thân, đuôi, ăng-ten (chuỗi, để overlap), thêm socket Muzzle ở đầu ăng-ten; build rig; kiểm skin bằng xoay thử vài khớp. (2) Anim idle (khoảng 40–60 frame, lặp), (3) Anim attack (lấy đà – bắn – hồi, khoảng 30–40 frame, ghi frame bắn).
- Lưu scene Frolvy ở work/infinite_defense/pets/mecha_pup/mecha_pup.fv (nếu lưu được).

## Xong là gì
- File báo cáo work/infinite_defense/pets/mecha_pup/report.md: rig có gì, số frame idle/attack, frame bắn, những chỗ vướng hoặc chưa chắc, tool/lệnh nào lỗi khi chạy Frolvy trong phiên con. Viết bằng lời thường, không dán code dài.
- Nếu mesh không dùng được (không tách bộ phận, scale sai...) hoặc Frolvy không điều khiển được từ phiên này: dừng, ghi `CHẶN: <câu hỏi>` kèm lý do cụ thể; đừng đoán.

## Cập nhật (người dùng, 2026-11-11)
- Mọi file làm việc (file Frolvy .fv, bản lưu, FBX xuất, playblast) lưu ở C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_11_Mecha_Pup\ (đã có Pet_Mecha_Pup.fbx). Quy ước các Pet sau: New_PET\Pet_<ID>_<Tên>\.
- Frolvy 9879 đã nhập sẵn mesh Pet_Mecha_Pup (chưa có joint): chạy `.venv/Scripts/python.exe -I tools/frolvy_port.py 9879 scene` xem hiện trạng rồi làm tiếp, đừng nhập lại.
- Bạn chạy trong Paseo (người dùng xem trực tiếp). CHỈ dùng Frolvy cổng 9879 (qua tools/frolvy_port.py); KHÔNG dùng công cụ MCP frolvy có sẵn (nó nối vào cổng 9877 của phiên khác). Không commit, không đổi nhánh, không đẩy GitHub.
- Xong thì ghi report.md như trên, rồi báo ngắn bằng tiếng Việt.
