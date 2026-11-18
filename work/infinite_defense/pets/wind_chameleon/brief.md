# Việc: GEK-2360 — Pet 16 Wind Chameleon (Tắc Kè Gió): rig + anim idle + attack (game Infinite Defense, việc cha GEK-2273)

Bạn làm MỘT Pet này trong Frolvy riêng, cổng **9884** (đã mở sẵn, trống). Cổng khác (9877 phiên chính, 9879/9881/9882/9883 Pet 11/12/13/15): đừng đụng.

## Đọc trước (đã có 3 Pet làm xong, học từ đó, đừng làm lại từ đầu)
- work/infinite_defense/pets/mecha_pup/report.md, tiny_chick/report.md, pebble_turtle/report.md: quy trình rig + skin + bẫy Frolvy. Script dựng lại: work/infinite_defense/pets/mecha_pup/rig/ (make_fit.py, skin.py) và anim/ (idle.py, attack.py, make_clips.py). Mesh có thể nằm nghiêng (xem báo cáo Pebble Turtle).
- Luật rig game: .claude/skills/frolvy_auto_rig/ và frolvy_rig/ (chỉ joint DEF, tối đa 4 influence, Root_M là hông). Luật anim: .claude/skills/animation/knowledge/CORE.md. Sửa bằng layer cộng, không key thẳng Base.
- **Xuất FBX: đọc kỹ .claude/skills/animation/knowledge/details/export.md (mục Base + anim-only) và .claude/memory_store/reference-pet-fbx-unity-fixes.md.**

## LUẬT PET
- **BAY LƠ LỬNG** (người dùng 2026-11-11): không tiếp đất, thân hover ~12 cm, các bộ phận thả/trễ theo thân. Tắc kè gió bám lơ lửng trên không, không bò trên đất.
- **KHI NÀO XUẤT FBX (người dùng 2026-11-13): CHỈ xuất khi người dùng nói "chốt".** Các vòng làm, sửa, feedback: chỉ làm trong Frolvy + lưu .fv, KHÔNG xuất FBX, KHÔNG chạy các bước sửa FBX. Phần quy trình xuất bên dưới chỉ chạy khi có lệnh chốt.
- **FBX (người dùng 2026-11-12):** 3 file, tên nối bằng GẠCH DƯỚI, không dùng @:
  1. `Pet_Wind_Chameleon.fbx` = Base: xương + mesh + skin, **xuất ở đúng tư thế bind** (mọi control về 0, không key, xương không xoay: các Pet trước xuất Base lệch tư thế nên tool fbx_unity_bind từ chối), 0 AnimationStack.
  2. `Pet_Wind_Chameleon_Idle.fbx`, `Pet_Wind_Chameleon_Attack.fbx` = CHỈ xương + clip, KHÔNG mesh.
  - Quy trình xuất: fbx_ascii_keep --root DEF_Root_M → tools/pet_fbx_finalize.py (UnitScale 100, tên take Idle/Attack) → Base: tools/fbx_unity_bind.py rồi tools/fbx_strip_anim.py; file anim: tools/fbx_add_sibling.py. Socket đạn là joint `DEF_Muzzle_M`.
  - Kiểm: Base có BindPose + mesh + deformer, 0 AnimationStack; file anim 0 mesh, có Dummy cùng cấp, tên xương trùng Base. Chưa chép vào Unity, người dùng sẽ duyệt.

## Đầu vào
- Mesh: C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_16_Wind_Chameleon\Pet_Wind_Chameleon.fbx (chưa biết có xương/skin chưa: kiểm trước).
- GDD: work/infinite_defense/gdd/tab.csv, dòng ID 16. Tóm tắt:
  - Hình khối uốn lượn thon gọn (Curved S-shape).
  - Socket bắn đạn (Muzzle): miệng / lưỡi.
  - Idle: bám lơ lửng trên không, thân đổi sắc nhẹ (đổi màu là shader/VFX, không có trong anim), đuôi nhấp nhô (LẶP liền mạch).
  - Attack: má phồng cực đại, bắn vụt lưỡi giải phóng lốc xoáy (có key rõ tại frame bắn để gắn event). Cuối attack về đúng tư thế idle frame 0.
- Không có clip di chuyển.

## Cách làm
- Điều khiển Frolvy: `.venv/Scripts/python.exe -I tools/frolvy_port.py 9884 <file.py>` (lệnh nhanh: `... 9884 scene`). KHÔNG dùng công cụ MCP frolvy có sẵn (nối vào cổng 9877).
- Thứ tự: (1) rig: thân S-shape (chuỗi xương sống), đuôi cuộn (chuỗi), đầu, hàm, má (phồng được), lưỡi (chuỗi xương dài, bắn vụt ra), 4 chân thả lủng lẳng, mắt, Muzzle ở miệng/đầu lưỡi; build rig; xoay thử kiểm skin. (2) idle ~48 frame lặp, (3) attack ~24–30 frame, ghi frame bắn.
- Lưu mọi file làm việc (.fv, FBX, playblast) ở C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_16_Wind_Chameleon\. Script đặt ở work/infinite_defense/pets/wind_chameleon/.

## Xong là gì
- work/infinite_defense/pets/wind_chameleon/report.md: rig có gì, số frame idle/attack, frame bắn, đường dẫn file đã lưu, kết quả kiểm FBX, chỗ vướng hoặc chưa chắc. Lời thường, không dán code dài.
- Mesh không dùng được hoặc Frolvy không điều khiển được: dừng, ghi `CHẶN: <câu hỏi>` kèm lý do cụ thể, đừng đoán.
- Không commit, không đổi nhánh, không đẩy GitHub, không chép vào Unity. Trả lời tiếng Việt.
