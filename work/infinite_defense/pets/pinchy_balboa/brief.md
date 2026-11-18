# Việc: GEK-2361 — Pet 17 Pinchy Balboa (Cua Quyền Vương): rig + anim idle + attack (game Infinite Defense, việc cha GEK-2273)

Bạn làm MỘT Pet này trong Frolvy riêng, cổng **9885** (đã mở sẵn, trống). Các cổng khác là của phiên khác (9877 phiên chính, 9879–9899): đừng đụng.

## Đọc trước (đã có 5 Pet làm xong, học từ đó, đừng làm lại từ đầu)
- work/infinite_defense/pets/*/report.md (mecha_pup, tiny_chick, pebble_turtle, night_bat, wind_chameleon): quy trình rig + skin + bẫy Frolvy. Script dựng lại: work/infinite_defense/pets/mecha_pup/rig/ và anim/, night_bat/rig_skin.py. Mesh có thể nằm nghiêng (xem báo cáo Pebble Turtle).
- Luật rig game: .claude/skills/frolvy_auto_rig/ và frolvy_rig/ (chỉ joint DEF, tối đa 4 influence, Root_M là hông). Luật anim: .claude/skills/animation/knowledge/CORE.md. Sửa bằng layer cộng, không key thẳng Base; không đổi key đã có.
- **Bài học Frolvy (memory_store): frolvy-bind-pose-and-empty-curve.md** (bind skin khi MỌI control = 0, rồi `set_frame(3); set_frame(0)`; xóa hết key một channel làm channel chết: key 0 mọi frame trước; không dựng lại rig trong cùng scene để khỏi joint ma; mesh hàn liền thì tách bằng extract_faces), loop_seam.smooth cho idle lặp, tự dò xoắn (góc xoay thế giới/frame) và tự sửa.
- **Xuất FBX: đọc kỹ .claude/skills/animation/knowledge/details/export.md (mục Base + anim-only) và .claude/memory_store/reference-pet-fbx-unity-fixes.md.**

## LUẬT PET
- **BAY LƠ LỬNG** (người dùng 2026-11-11): không tiếp đất, không khóa chân xuống đất, thân hover ~12 cm, chân/tay/phụ kiện thả và trễ theo thân. "Nhún / đổi chân / thủ thế" trong GDD = bồng bềnh trên không.
- **KHI NÀO XUẤT FBX (người dùng 2026-11-13): CHỈ xuất khi người dùng nói "chốt".** Các vòng làm, sửa, feedback: chỉ làm trong Frolvy + lưu .fv, KHÔNG xuất FBX, KHÔNG chạy các bước sửa FBX. Phần quy trình xuất bên dưới chỉ chạy khi có lệnh chốt.
- **FBX (người dùng 2026-11-12), tên nối bằng GẠCH DƯỚI, không dùng @:**
  1. `Pet_Pinchy_Balboa.fbx` = Base: xương + mesh + skin, **xuất ở đúng tư thế bind** (mọi control về 0, không key, xương không xoay), 0 AnimationStack.
  2. `Pet_Pinchy_Balboa_Idle.fbx`, `Pet_Pinchy_Balboa_Attack.fbx` = CHỈ xương + clip, KHÔNG mesh.
  - Quy trình: fbx_ascii_keep --root DEF_Root_M → tools/pet_fbx_finalize.py (UnitScale 100, take Idle/Attack) → Base: tools/fbx_unity_bind.py rồi tools/fbx_strip_anim.py; file anim: tools/fbx_add_sibling.py. Socket đạn là joint `DEF_Muzzle_M`.
  - Kiểm: Base có BindPose + mesh + deformer, 0 AnimationStack; file anim 0 mesh, có Dummy cùng cấp, tên xương trùng Base. Chưa chép vào Unity (người dùng duyệt trước).

## Đầu vào
- Mesh: C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_17_Pinchy_Balboa\Pet_Pinchy_Balboa.fbx (chưa biết có xương/skin chưa: kiểm trước; kiểm mesh có tách bộ phận đủ để skin sạch không).
- GDD: work/infinite_defense/gdd/tab.csv, dòng ID 17. Tóm tắt:
  - Hình khối: Thủ thế võ đài đấm bốc (Boxer Stance). Chi tiết nhận diện: 2 càng mang găng đấm bốc đỏ rực, băng đô đỏ, thủ thế nhấp nhô
  - Socket bắn đạn (Muzzle): Đầu găng đấm bốc phải. Đạn: Cú đấm móc sấm sét giải phóng sóng xung kích ngang (VFX, không nằm trong anim).
  - Idle (LẶP liền mạch): Nhấp nhô đổi chân theo nhịp quyền anh Mike Tyson.
  - Attack: Lắc người né đòn rồi vung cú móc hàm sấm sét về bên phải (có key rõ tại frame bắn để gắn event; cuối attack về đúng tư thế idle frame 0).
- Không có clip di chuyển.

## Cách làm
- Điều khiển Frolvy: `.venv/Scripts/python.exe -I tools/frolvy_port.py 9885 <file.py>` (lệnh nhanh: `... 9885 scene`). KHÔNG dùng công cụ MCP frolvy có sẵn (nối vào cổng 9877).
- Thứ tự: (1) rig. Gợi ý bộ phận: thân, 2 chân (bồng bềnh đổi chân), 2 tay + 2 găng đấm (găng phải là socket Muzzle), 2 càng/mắt cua trên cuống, miệng. Socket Muzzle theo GDD; build rig; kiểm skin bằng xoay thử các khớp chính và `skin_check.py`. (2) idle ~48 frame lặp, (3) attack ~24–30 frame, ghi frame bắn.
- Lưu mọi file làm việc (.fv, FBX, playblast) ở C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_17_Pinchy_Balboa\. Script đặt ở work/infinite_defense/pets/pinchy_balboa/.

## Xong là gì
- work/infinite_defense/pets/pinchy_balboa/report.md: rig có gì, số frame idle/attack, frame bắn, đường dẫn file đã lưu, kết quả kiểm FBX, chỗ vướng hoặc chưa chắc. Lời thường, không dán code dài.
- Mesh không dùng được hoặc Frolvy không điều khiển được: dừng, ghi `CHẶN: <câu hỏi>` kèm lý do cụ thể, đừng đoán.
- Không commit, không đổi nhánh, không đẩy GitHub, không chép vào Unity. Trả lời tiếng Việt.
