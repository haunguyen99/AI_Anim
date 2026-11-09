# RPG2 Hero: môi trường làm anim (tạo 2026-11-09)

- Nhân vật: Char_Main_T2 (Assassin), song đao `Vk_t1_Dualblades_lv1`, camera game top-down
- Chuẩn: 30 fps; Idle 30F loop; mỗi đòn 30F (S10 · A5 · R15), F30 nối về tư thế Idle
- Quy tắc: làm MỚI hoàn toàn, không đụng `D:\rpg-game1\Assets\_Game\Animation\Hero_RPG2\` và controller cũ; đưa gì vào repo phải hỏi trước

## Đường dẫn
| Việc | Chỗ |
|---|---|
| File làm việc Frolvy (.fv) | `C:\Project\RPG_2\Hero\Hero_Blade\` |
| Rig | `C:\Project\RPG_2\Hero\Rig\Hero_Blade_Rig.fv` (+ `Hero_Simple.fvpicker`) |
| Model + texture gốc | `C:\Project\RPG_2\Hero\` (`Char_Main_T2.fbx`, `T_Char_Main_T2.tga`, `T_Colorpalette.tga`, `Vk_t1_Dualblades_lv1.fbx`) |
| Playblast (chỉ khi user ra lệnh) | `C:\Project\RPG_2\Hero\Hero_Blade\Blast_Test\` (camera1, ẩn control, có texture, tên mới mỗi lần) |
| GDD + danh sách anim | `work/rpg2_hero/gdd/anim_list.md` |
| Thư mục từng clip | `work/rpg2_hero/blade_idle`, `blade_attack_1`, `blade_attack_2`, `blade_deadly_strike` (mỗi clip: `brief.md`, `director_log.md`) |
| Script rig | `work/rpg2_hero/rig/` |

## Frolvy
- Plugin `hero_textures` tự gắn texture khi mở scene (cần khởi động lại Frolvy một lần nếu mở từ trước khi cài). Thủ công: `exec` file plugin rồi `apply(api, force=True)`.
- Sửa anim: mỗi vòng một layer additive (`frolvy_layers.py`), không key đè Base; `bake_for_export` trước khi xuất FBX.
- Vòng lặp: sau mỗi vòng sửa xong chạy `loop_seam.smooth(api)`.
- Không đổi key đã duyệt (blocking); chỉ thêm trên frame inbetween mới.

## Tình trạng clip (2026-11-09)
| Clip | File Frolvy mới nhất | Trạng thái |
|---|---|---|
| Idle | `Hero_Blade_Idle_v2.fv` | đang làm |
| Attack 1 | `Hero_Blade_Attack_01_v3.fv` | đang làm |
| Attack 2 | `Hero_Blade_Attack_02_v1.fv` | đang làm (đang mở trong Frolvy) |
| Deadly Strike | — | chưa bắt đầu |
