# Việc: GEK-2358 — Pet 14 Lucky Neko (Mèo Thần Tài): CHỈ LẬP FILE RIG (chưa làm anim) (game Infinite Defense, việc cha GEK-2273)

Bạn làm MỘT Pet này trong Frolvy riêng, cổng **9891** (đã mở sẵn, trống). Các cổng khác là của phiên khác (9877 phiên chính, 9879–9899): đừng đụng.

## Đọc trước (đã có 5 Pet làm xong, học từ đó, đừng làm lại từ đầu)
- work/infinite_defense/pets/*/report.md (mecha_pup, tiny_chick, pebble_turtle, night_bat, wind_chameleon): quy trình rig + skin + bẫy Frolvy. Script dựng lại: work/infinite_defense/pets/mecha_pup/rig/ và anim/, night_bat/rig_skin.py. Mesh có thể nằm nghiêng (xem báo cáo Pebble Turtle).
- Luật rig game: .claude/skills/frolvy_auto_rig/ và frolvy_rig/ (chỉ joint DEF, tối đa 4 influence, Root_M là hông). Luật anim: .claude/skills/animation/knowledge/CORE.md. Sửa bằng layer cộng, không key thẳng Base; không đổi key đã có.
- **Bài học Frolvy (memory_store): frolvy-bind-pose-and-empty-curve.md** (bind skin khi MỌI control = 0, rồi `set_frame(3); set_frame(0)`; xóa hết key một channel làm channel chết: key 0 mọi frame trước; không dựng lại rig trong cùng scene để khỏi joint ma; mesh hàn liền thì tách bằng extract_faces), loop_seam.smooth cho idle lặp, tự dò xoắn (góc xoay thế giới/frame) và tự sửa.
- **Xuất FBX: đọc kỹ .claude/skills/animation/knowledge/details/export.md (mục Base + anim-only) và .claude/memory_store/reference-pet-fbx-unity-fixes.md.**

## LUẬT PET
- **BAY LƠ LỬNG** (người dùng 2026-11-11): không tiếp đất, không khóa chân xuống đất, thân hover ~12 cm, chân/tay/phụ kiện thả và trễ theo thân. "Nhún / đổi chân / thủ thế" trong GDD = bồng bềnh trên không.
- **KHI NÀO XUẤT FBX (người dùng 2026-11-13): CHỈ xuất khi người dùng nói "chốt".** Các vòng làm, sửa, feedback: chỉ làm trong Frolvy + lưu .fv, KHÔNG xuất FBX, KHÔNG chạy các bước sửa FBX. Phần quy trình xuất bên dưới chỉ chạy khi có lệnh chốt.
- **FBX (người dùng 2026-11-12), tên nối bằng GẠCH DƯỚI, không dùng @:**
  (lần này KHÔNG xuất; chỉ dùng khi được bảo) 1. `Pet_Lucky_Neko.fbx` = Base: xương + mesh + skin, **xuất ở đúng tư thế bind** (mọi control về 0, không key, xương không xoay), 0 AnimationStack.
  2. `Pet_Lucky_Neko_Idle.fbx`, `Pet_Lucky_Neko_Attack.fbx` = CHỈ xương + clip, KHÔNG mesh.
  - Quy trình: fbx_ascii_keep --root DEF_Root_M → tools/pet_fbx_finalize.py (UnitScale 100, take Idle/Attack) → Base: tools/fbx_unity_bind.py rồi tools/fbx_strip_anim.py; file anim: tools/fbx_add_sibling.py. Socket đạn là joint `DEF_Muzzle_M`.
  - Kiểm: Base có BindPose + mesh + deformer, 0 AnimationStack; file anim 0 mesh, có Dummy cùng cấp, tên xương trùng Base. Chưa chép vào Unity (người dùng duyệt trước).

## Đầu vào
- Mesh: C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_14_Lucky_Neko\Pet_Lucky_Neko.fbx (chưa biết có xương/skin chưa: kiểm trước; kiểm mesh có tách bộ phận đủ để skin sạch không).
- GDD: work/infinite_defense/gdd/tab.csv, dòng ID 14. Tóm tắt:
  - Hình khối: Mềm mại, phong cách Chibi Mascot. Chi tiết nhận diện: Đeo kính râm đen cool ngầu, chuông vàng cổ, hũ tiền lưng
  - Socket bắn đạn (Muzzle): Đồng xu trên tay vẫy. Đạn: Đồng tiền vàng xoay tít tạo vệt ánh kim (VFX, không nằm trong anim).
  - Idle (LẶP liền mạch): Tay phải vẫy đều liên tục, đuôi hình dấu hỏi.
  - Attack: Búng đồng tiền vàng bay vút đi như phi tiêu (có key rõ tại frame bắn để gắn event; cuối attack về đúng tư thế idle frame 0).
- Không có clip di chuyển.

## Cách làm
- Điều khiển Frolvy: `.venv/Scripts/python.exe -I tools/frolvy_port.py 9891 <file.py>` (lệnh nhanh: `... 9891 scene`). KHÔNG dùng công cụ MCP frolvy có sẵn (nối vào cổng 9877).
- **PHẠM VI LẦN NÀY (người dùng 2026-11-13): chỉ tới bước lập file rig để người dùng check. KHÔNG làm anim idle/attack, KHÔNG xuất FBX.** Làm: kiểm mesh, đặt joint fit, build rig, fit controls, bind skin (mọi control = 0 lúc bind), chỉnh weight, thử xoay các khớp chính + skin_check.py. Gợi ý bộ phận: thân chibi, đầu + 2 tai + mắt, tay phải vẫy liên tục (chuỗi vai-khuỷu-cổ tay-bàn tay) cầm đồng xu (xương riêng tại đồng xu = socket Muzzle), tay trái, đuôi hình dấu hỏi (chuỗi xương overlap), 2 chân. Socket Muzzle theo GDD. Lưu file rig `<tên>_rig.fv`.
- Lưu mọi file làm việc (.fv, FBX, playblast) ở C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_14_Lucky_Neko\. Script đặt ở work/infinite_defense/pets/lucky_neko/.

## Xong là gì
- File rig đã lưu, mở được, check_rig sạch. work/infinite_defense/pets/lucky_neko/report.md: rig có những joint/control gì, vị trí socket, chỗ skin còn yếu hoặc chưa chắc (nếu có), đường dẫn file rig. Lời thường, không dán code dài. Xong thì dừng, đợi người dùng check rồi mới làm tiếp.
- Mesh không dùng được hoặc Frolvy không điều khiển được: dừng, ghi `CHẶN: <câu hỏi>` kèm lý do cụ thể, đừng đoán.
- Không commit, không đổi nhánh, không đẩy GitHub, không chép vào Unity. Trả lời tiếng Việt.
