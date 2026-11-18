"""Tao brief + thu muc + mesh cho 1 Pet. usage: py -I make_brief.py <ID> <mesh_file_stem> <GEK> <port> "<rig hint>" """
import sys, csv, os, shutil
sys.stdout.reconfigure(encoding='utf-8')
pid, stem, gek, port, rig = sys.argv[1:6]
rigonly = len(sys.argv) > 6 and sys.argv[6] == 'rigonly'
R = r'C:\Users\Admin\Documents\AI_animation'
rows = {r['ID']: r for r in csv.DictReader(open(R + r'\work\infinite_defense\gdd\tab.csv', encoding='utf-8-sig')) if r['ID']}
r = rows[pid]
name = r['Tên Pet Concept']; asset = r['Asset Key']            # Pet_mecha_pup
title = ''.join(w.capitalize() for w in asset.replace('Pet_', '').split('_'))  # not used
tit = '_'.join(w.capitalize() for w in asset.split('_')[1:])    # Mecha_Pup
workdir = r'C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_%s_%s' % (pid, tit)
folder = asset.replace('Pet_', '')                                # mecha_pup
wk = R + r'\work\infinite_defense\pets\%s' % folder
src = r'C:\Users\Admin\Documents\Horus\endless-kicker\Assets\Kho\Skin\mesh\Pet_new\mesh\%s.fbx' % stem
os.makedirs(workdir, exist_ok=True); os.makedirs(wk, exist_ok=True)
shutil.copy(src, workdir + r'\Pet_%s.fbx' % tit); shutil.copy(src, wk + r'\Pet_%s.fbx' % tit)
B = 'Pet_' + tit
txt = f"""# Việc: {gek} — Pet {pid} {name}: rig + anim idle + attack (game Infinite Defense, việc cha GEK-2273)

Bạn làm MỘT Pet này trong Frolvy riêng, cổng **{port}** (đã mở sẵn, trống). Các cổng khác là của phiên khác (9877 phiên chính, 9879–9899): đừng đụng.

## Đọc trước (đã có 5 Pet làm xong, học từ đó, đừng làm lại từ đầu)
- work/infinite_defense/pets/*/report.md (mecha_pup, tiny_chick, pebble_turtle, night_bat, wind_chameleon): quy trình rig + skin + bẫy Frolvy. Script dựng lại: work/infinite_defense/pets/mecha_pup/rig/ và anim/, night_bat/rig_skin.py. Mesh có thể nằm nghiêng (xem báo cáo Pebble Turtle).
- Luật rig game: .claude/skills/frolvy_auto_rig/ và frolvy_rig/ (chỉ joint DEF, tối đa 4 influence, Root_M là hông). Luật anim: .claude/skills/animation/knowledge/CORE.md. Sửa bằng layer cộng, không key thẳng Base; không đổi key đã có.
- **Bài học Frolvy (memory_store): frolvy-bind-pose-and-empty-curve.md** (bind skin khi MỌI control = 0, rồi `set_frame(3); set_frame(0)`; xóa hết key một channel làm channel chết: key 0 mọi frame trước; không dựng lại rig trong cùng scene để khỏi joint ma; mesh hàn liền thì tách bằng extract_faces), loop_seam.smooth cho idle lặp, tự dò xoắn (góc xoay thế giới/frame) và tự sửa.
- **Xuất FBX: đọc kỹ .claude/skills/animation/knowledge/details/export.md (mục Base + anim-only) và .claude/memory_store/reference-pet-fbx-unity-fixes.md.**

## LUẬT PET
- **BAY LƠ LỬNG** (người dùng 2026-11-11): không tiếp đất, không khóa chân xuống đất, thân hover ~12 cm, chân/tay/phụ kiện thả và trễ theo thân. "Nhún / đổi chân / thủ thế" trong GDD = bồng bềnh trên không.
- **KHI NÀO XUẤT FBX (người dùng 2026-11-13): CHỈ xuất khi người dùng nói "chốt".** Các vòng làm, sửa, feedback: chỉ làm trong Frolvy + lưu .fv, KHÔNG xuất FBX, KHÔNG chạy các bước sửa FBX. Phần quy trình xuất bên dưới chỉ chạy khi có lệnh chốt.
- **FBX (người dùng 2026-11-12), tên nối bằng GẠCH DƯỚI, không dùng @:**
  1. `{B}.fbx` = Base: xương + mesh + skin, **xuất ở đúng tư thế bind** (mọi control về 0, không key, xương không xoay), 0 AnimationStack.
  2. `{B}_Idle.fbx`, `{B}_Attack.fbx` = CHỈ xương + clip, KHÔNG mesh.
  - Quy trình: fbx_ascii_keep --root DEF_Root_M → tools/pet_fbx_finalize.py (UnitScale 100, take Idle/Attack) → Base: tools/fbx_unity_bind.py rồi tools/fbx_strip_anim.py; file anim: tools/fbx_add_sibling.py. Socket đạn là joint `DEF_Muzzle_M`.
  - Kiểm: Base có BindPose + mesh + deformer, 0 AnimationStack; file anim 0 mesh, có Dummy cùng cấp, tên xương trùng Base. Chưa chép vào Unity (người dùng duyệt trước).

## Đầu vào
- Mesh: {workdir}\{B}.fbx (chưa biết có xương/skin chưa: kiểm trước; kiểm mesh có tách bộ phận đủ để skin sạch không).
- GDD: work/infinite_defense/gdd/tab.csv, dòng ID {pid}. Tóm tắt:
  - Hình khối: {r['Ngôn ngữ Hình khối']}. Chi tiết nhận diện: {r['Chi Tiết Nhận Diện Đặc Trưng']}
  - Socket bắn đạn (Muzzle): {r['Vị trí Socket Muzzle']}. Đạn: {r['Hiệu ứng Đạn (VFX Type)']} (VFX, không nằm trong anim).
  - Idle (LẶP liền mạch): {r['Mô tả Hoạt ảnh _idle']}.
  - Attack: {r['Mô tả Hoạt ảnh _attack (Gắn Event)']} (có key rõ tại frame bắn để gắn event; cuối attack về đúng tư thế idle frame 0).
- Không có clip di chuyển.

## Cách làm
- Điều khiển Frolvy: `.venv/Scripts/python.exe -I tools/frolvy_port.py {port} <file.py>` (lệnh nhanh: `... {port} scene`). KHÔNG dùng công cụ MCP frolvy có sẵn (nối vào cổng 9877).
- Thứ tự: (1) rig. Gợi ý bộ phận: {rig}. Socket Muzzle theo GDD; build rig; kiểm skin bằng xoay thử các khớp chính và `skin_check.py`. (2) idle ~48 frame lặp, (3) attack ~24–30 frame, ghi frame bắn.
- Lưu mọi file làm việc (.fv, FBX, playblast) ở {workdir}\. Script đặt ở work/infinite_defense/pets/{folder}/.

## Xong là gì
- work/infinite_defense/pets/{folder}/report.md: rig có gì, số frame idle/attack, frame bắn, đường dẫn file đã lưu, kết quả kiểm FBX, chỗ vướng hoặc chưa chắc. Lời thường, không dán code dài.
- Mesh không dùng được hoặc Frolvy không điều khiển được: dừng, ghi `CHẶN: <câu hỏi>` kèm lý do cụ thể, đừng đoán.
- Không commit, không đổi nhánh, không đẩy GitHub, không chép vào Unity. Trả lời tiếng Việt.
"""
if rigonly:
    txt = txt.replace("rig + anim idle + attack", "CHỈ LẬP FILE RIG (chưa làm anim)")
    a = txt.index("- Thứ tự: (1) rig."); b = txt.index("- Lưu mọi file làm việc")
    scope = ("- **PHẠM VI LẦN NÀY (người dùng 2026-11-13): chỉ tới bước lập file rig để người dùng check. KHÔNG làm anim idle/attack, KHÔNG xuất FBX.** "
             "Làm: kiểm mesh, đặt joint fit, build rig, fit controls, bind skin (mọi control = 0 lúc bind), chỉnh weight, thử xoay các khớp chính + skin_check.py. Gợi ý bộ phận: " + rig + ". Socket Muzzle theo GDD. Lưu file rig `<tên>_rig.fv`." + chr(10))
    txt = txt[:a] + scope + txt[b:]
    a = txt.index("## Xong là gì"); b = txt.index("- Mesh không dùng được")
    done = ("## Xong là gì" + chr(10) + "- File rig đã lưu, mở được, check_rig sạch. work/infinite_defense/pets/" + folder + "/report.md: rig có những joint/control gì, vị trí socket, chỗ skin còn yếu hoặc chưa chắc (nếu có), đường dẫn file rig. Lời thường, không dán code dài. Xong thì dừng, đợi người dùng check rồi mới làm tiếp." + chr(10))
    txt = txt[:a] + done + txt[b:]
    txt = txt.replace("  1. `", "  (lần này KHÔNG xuất; chỉ dùng khi được bảo) 1. `", 1)
open(wk + r'\brief.md', 'w', encoding='utf-8').write(txt)
print(wk + r'\brief.md')
