---
name: reference-frolvy-unity-fbx-export
description: "Xuất FBX rig / anim từ Frolvy sang Unity cho hero Nova: 3 lỗi Unity (bind pose = identity, mất cha súng, node gốc bị đổi tên) + quy trình một lượt + công cụ work/runner_hybrid/rig/fbx_fix"
metadata:
  node_type: memory
  type: reference
  originSessionId: 3ad1cefd-84fd-4aa6-979c-4fe87a5030f2
  modified: 2026-11-18T09:41:46.824Z
---

Hero Nova (Runner_Hybrid), 2026-11-18. FBX do Frolvy xuất (ASCII 7.4, `export_scene(path,'fbx',include_mesh,start,end,fps)`) import vào Unity 2022.3.62 bị 3 lỗi, đều đã đo bằng Unity batchmode trên dự án tạm (`/tmp`, `Unity -batchmode -nographics -projectPath /tmp/x -executeMethod ...`, ~60 s mỗi lần; không dùng dự án team để thử).

**1. Skin kéo giãn / "nhảy tùm lum" (FBX có mesh).** Unity bỏ qua `TransformLink` của cluster, `bindpose[i]` = `Transform` của cluster i → toàn identity. Sửa chỉ cho Unity: ghi `Transform` mỗi cluster = nghịch đảo `TransformLink` (`fbx_fix/unity_bind_fix.py`). Đo lại: lệch bind 0, đỉnh lệch 0,0000 m. Thêm BindPose / bỏ `-0.000000` / bỏ anim / thêm RotationOrder đều KHÔNG sửa được. File đã sửa nhập lại Frolvy/Blender sẽ sai → luôn giữ bản `_Frolvy` gốc.
**2. Súng rơi về gốc toạ độ.** `export_scene` ghi nhóm vũ khí `vk_Hero_NOVA1` (Null) ở gốc thế giới, `tools/fbx_ascii_keep.py` còn bỏ hẳn Null. Mesh súng dựng theo toạ độ local của `DEF_Weapon_R` → gắn lại bằng `fbx_fix/attach_weapon.py raw keep out` (Null → DEF_Weapon_R, mesh → Null, Lcl = 0).
**3. Lỗi Rig tab "Cannot find root motion transform 'root'" (FBX anim chỉ-xương).** FBX chỉ có MỘT node gốc `root` → Unity đổi tên thành tên file, curve thành `DEF_Root_M/...` (khớp 10/510). Thêm một Null gốc thứ hai tên `Hero_NOVA_game1` (`fbx_fix/add_toplevel_dummy.py in out`) → 510/510, hết lỗi. Mọi FBX anim Nova xuất trước đó (Attack, Cast, Idle_Shop, Showcase) có cùng lỗi.

**Quy trình một clip anim (Frolvy → Unity):**
1. Mở BẢN SAO `.fv` bằng `tools/frolvy_open.sh /tmp/x/ten.fv` (không đụng file / cửa sổ của người dùng; cổng xem tiêu đề `[MCP 98xx]`). Kiểm `api.frame_range()`, layer (Idle_Game chỉ Base).
2. Scene đặt namespace `Hero_Nova_Rig_V1:`: thêm joint `root` ở (0,0,0) làm cha `DEF_Root_M` (`api.select([])`, `create_joint`, `rename('root')`, `set_transform('root',[0,0,0],[0,0,0],[1,1,1])`, `parent('<ns>DEF_Root_M','root')`; world không đổi).
3. `api.set_frame(0)`; `api.export_scene('/tmp/x/raw.fbx','fbx',False,0,<cuối>,30)`.
4. `python3 -I tools/fbx_ascii_keep.py raw.fbx keep.fbx --root root --no-meshes`, rồi bỏ tiền tố `Hero_Nova_Rig_V1:` (tên joint phải là `DEF_*` khớp FBX rig).
5. `fbx_fix/add_toplevel_dummy.py keep.fbx out.fbx`.
6. Ghi vào `tvc_source/.../Hero_Nova/EXP/` và `runner-hybrid/Assets/_Game/Animations/Hero_Nova/` (dự án Unity team: chỉ chép FBX / sửa `.meta` khi người dùng bảo; không commit).
7. `.meta` của FBX anim: `animationType: 2` (Generic), `avatarSetup: 2` (Copy From Other, nguồn `Hero_Nova_Game_RigAvatar`), `rootMotionBoneName: root`, `clipAnimations` có tên clip, `takeName: take1`, `firstFrame 0`, `lastFrame N`, `loopTime: 1` (idle / loop). Khối mẫu lấy từ `Hero_Ranger_Idle.fbx.meta`. Chỉ ghi đè file của chính mình để GUID / setting của người dùng giữ nguyên; file cũ đặt tên khác chứ không đè khi chưa hỏi.
**Quy trình rig (FBX có mesh):** mở bản sao `Hero_Nova_Rig_V3.fv`, thêm `root`, `export_scene(...,True,0,0)` → `fbx_ascii_keep --root root` → `attach_weapon.py raw keep W` → `unity_bind_fix.py W out`. Ra `Hero_Nova_Game_Rig.fbx` (Unity) + `Hero_Nova_Game_Rig_Frolvy.fbx` (gốc). FBX mesh shop `Hero_Nova_Shop_Base.fbx` có cùng lỗi 1, chưa sửa.

**Bẫy:** `pkill -f` khớp luôn lệnh của chính shell (tự giết) → dùng `ps aux | grep "[t]ên" | awk '{print $2}' | xargs kill`. Unity import chỉ chạy khi người dùng bấm vào cửa sổ Unity. Take đặt tên `take1` (theo các FBX trước), không phải `Take 001`.

Liên quan: [[reference-frolvy-linux-bridge]], [[reference-frolvy-open-linux]], [[project-runner-hybrid]].

**Một lệnh (từ 2026-11-18, đã chạy cho Attack):** `python3 -I work/runner_hybrid/rig/fbx_fix/export_clip.py "<.fv>" <TênFBX> [--loop] [--no-unity]` làm cả 6 bước + kiểm (curve = vị trí thật, số key = số frame, joint khớp rig) + ghi EXP, Unity và .meta (mẫu từ meta Idle_Game, tên clip = tên FBX); không ghi đè file Unity có sẵn. Cần thêm: anim layer đã bake đúng (Cast có layer Cast_RecoilLean, kiểm khớp); `set_active_layer` nhận SỐ (0 = Base), không nhận tên.

**Một lệnh cho RIG (đã chạy cho Shop_Rig_V2):** `python3 -I work/runner_hybrid/rig/fbx_fix/export_rig.py "<.fv>" <TênFBX> [--no-unity]` — mở bản sao, thêm root nếu chưa có, export có mesh, fbx_ascii_keep, bỏ namespace, attach_weapon, unity_bind_fix, kiểm (cluster, súng dưới DEF_Weapon_R, control = 0), ghi EXP/<Tên>_Frolvy.fbx + EXP/<Tên>.fbx + Unity/<Tên>.fbx + meta (mẫu Hero_Nova_Game_Rig). Shop_Rig_V2 đã có root nên không thêm; 29 cluster; gốc gồm root + Hero_NOVA_shop. Chưa đo bind trong Unity cho mesh shop (cùng cơ chế mesh game).

**Cập nhật 2026-11-20 (Frolvy 0.9.78, tên cửa sổ "Fovy"):** (1) `export_scene(path,'fbx')` nay ra FBX NHỊ PHÂN; muốn ASCII (cho fbx_ascii_keep / add_toplevel_dummy) dùng `'fbx_ascii'` (đã sửa export_clip.py / export_rig.py). (2) Tiêu đề cửa sổ là "Fovy 0.9.78 Beta - <file>.fv [MCP cổng]" nên mọi lệnh `grep -i frolvy` phải khớp cả `fovy` (đã sửa tools/frolvy_open.sh: `grep -iE 'frolvy|fovy'`). (3) Dữ liệu người dùng chuyển sang `/home/huongbtx/Desktop/DataHDD/Project/tvc_source/...` (thư mục `/DataHDD/tvc_source` cũ vẫn còn bản cũ): chạy `HERO_DIR="<.../Hero_Nova>" python3 -I work/runner_hybrid/rig/fbx_fix/export_clip.py "<.fv>" <Tên> --no-unity` (HERO_DIR đổi gốc, EXP = HERO_DIR/EXP; FBX rig so tên joint tự tìm trong EXP hoặc EXP/OLD). (4) Tên FBX clip theo quy ước EXP: `Hero_Nova_<Clip>_Game.fbx` (vd Hero_Nova_Cast_Game). Cast v1.3 (2026-11-19): 0-96, layer Base + Cast_Lean, đã khớp curve vị trí thật.
