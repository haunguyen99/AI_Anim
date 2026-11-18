# Việc: GEK-2359 — Pet 15 Night Bat (Dơi Sóng Âm): rig + anim idle + attack (game Infinite Defense, việc cha GEK-2273)

Bạn làm MỘT Pet này trong Frolvy riêng, cổng **9883** (đã mở sẵn, trống). Cổng khác (9877 phiên chính, 9879/9881/9882 Pet 11/12/13): đừng đụng.

## Đọc trước (đã có 3 Pet làm xong, học từ đó, đừng làm lại từ đầu)
- work/infinite_defense/pets/mecha_pup/report.md, tiny_chick/report.md, pebble_turtle/report.md: quy trình rig + skin + bẫy Frolvy. Script dựng lại: work/infinite_defense/pets/mecha_pup/rig/ (make_fit.py, skin.py) và anim/ (idle.py, attack.py, make_clips.py). Mesh có thể nằm nghiêng (xem báo cáo Pebble Turtle).
- Luật rig game: .claude/skills/frolvy_auto_rig/ và frolvy_rig/ (chỉ joint DEF, tối đa 4 influence, Root_M là hông). Luật anim: .claude/skills/animation/knowledge/CORE.md. Sửa bằng layer cộng, không key thẳng Base.
- **Xuất FBX: đọc kỹ .claude/skills/animation/knowledge/details/export.md (mục Base + anim-only) và .claude/memory_store/reference-pet-fbx-unity-fixes.md.**

## LUẬT PET
- **BAY LƠ LỬNG** (người dùng 2026-11-11): không tiếp đất, thân hover ~12 cm, các bộ phận thả/trễ theo thân. Con dơi vốn bay: idle bay lơ lửng vỗ cánh, đừng cho đứng đất.
- **KHI NÀO XUẤT FBX (người dùng 2026-11-13): CHỈ xuất khi người dùng nói "chốt".** Các vòng làm, sửa, feedback: chỉ làm trong Frolvy + lưu .fv, KHÔNG xuất FBX, KHÔNG chạy các bước sửa FBX. Phần quy trình xuất bên dưới chỉ chạy khi có lệnh chốt.
- **FBX (người dùng 2026-11-12):** 3 file, tên nối bằng GẠCH DƯỚI, không dùng @:
  1. `Pet_Night_Bat.fbx` = Base: xương + mesh + skin, **xuất ở đúng tư thế bind** (mọi control về 0, không key, xương không xoay: các Pet trước xuất Base lệch tư thế nên tool fbx_unity_bind từ chối), 0 AnimationStack.
  2. `Pet_Night_Bat_Idle.fbx`, `Pet_Night_Bat_Attack.fbx` = CHỈ xương + clip, KHÔNG mesh.
  - Quy trình xuất: fbx_ascii_keep --root DEF_Root_M → tools/pet_fbx_finalize.py (UnitScale 100, tên take Idle/Attack) → Base: tools/fbx_unity_bind.py rồi tools/fbx_strip_anim.py; file anim: tools/fbx_add_sibling.py. Socket đạn là joint `DEF_Muzzle_M`.
  - Kiểm: Base có BindPose + mesh + deformer, 0 AnimationStack; file anim 0 mesh, có Dummy cùng cấp, tên xương trùng Base. Chưa chép vào Unity, người dùng sẽ duyệt.

## Đầu vào
- Mesh: C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_15_Night_Bat\Pet_Night_Bat.fbx (chưa biết có xương/skin chưa: kiểm trước).
- GDD: work/infinite_defense/gdd/tab.csv, dòng ID 15. Tóm tắt:
  - Hình khối tam giác ngược (Inverted Triangle).
  - Socket bắn đạn (Muzzle): miệng dơi.
  - Idle: bay lơ lửng vỗ cánh nhanh, tai xoay dò sóng âm (LẶP liền mạch).
  - Attack: gập cánh ngửa cổ tụ lực, bung mạnh cánh há miệng phát sóng radar (có key rõ tại frame bắn để gắn event). Cuối attack về đúng tư thế idle frame 0.
- Không có clip di chuyển.

## Cách làm
- Điều khiển Frolvy: `.venv/Scripts/python.exe -I tools/frolvy_port.py 9883 <file.py>` (lệnh nhanh: `... 9883 scene`). KHÔNG dùng công cụ MCP frolvy có sẵn (nối vào cổng 9877).
- Thứ tự: (1) rig: thân, đầu, tai (xoay được), hàm, 2 cánh (mỗi cánh 2–3 xương để gập/bung), Muzzle ở miệng; build rig; xoay thử kiểm skin. (2) idle ~48 frame lặp (vỗ cánh nhanh: chọn chu kỳ lặp khớp 48 frame), (3) attack ~24–30 frame, ghi frame bắn.
- Lưu mọi file làm việc (.fv, FBX, playblast) ở C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_15_Night_Bat\. Script đặt ở work/infinite_defense/pets/night_bat/.

## Xong là gì
- work/infinite_defense/pets/night_bat/report.md: rig có gì, số frame idle/attack, frame bắn, đường dẫn file đã lưu, kết quả kiểm FBX, chỗ vướng hoặc chưa chắc. Lời thường, không dán code dài.
- Mesh không dùng được hoặc Frolvy không điều khiển được: dừng, ghi `CHẶN: <câu hỏi>` kèm lý do cụ thể, đừng đoán.
- Không commit, không đổi nhánh, không đẩy GitHub, không chép vào Unity. Trả lời tiếng Việt.
