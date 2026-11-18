---
name: reference-pets-unity-folder
description: Nơi đẩy FBX Pet Infinite Defense vào Unity (endless-kicker) và thư mục làm việc New_PET
metadata:
  type: reference
---

- **Đích Unity:** `C:\Users\Admin\Documents\Horus\endless-kicker\Assets\_Game\Animation\New_Pet` (user 2026-11-12; thư mục trống, repo nhánh v1). Các thư mục anim khác trong `Assets\_Game\Animation` (Hero/Boss/Elite/Normal/Weapon) chia mỗi nhân vật một thư mục con → Pet theo `New_Pet\Pet_<Tên>\` với Base + `_Idle` + `_Attack`.
- **Mesh gốc Pet:** `...\endless-kicker\Assets\Kho\Skin\mesh\Pet_new\mesh` (mới có 5 con: Mecha Pup, Pebble Turtle, Tiny Chick, Night Bat, Wind Chameleon).
- **File làm việc Pet:** `C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_<ID>_<Tên>\` (.fv, FBX, playblast).
- Chỉ chép vào Unity khi FBX đã qua kiểm (xem [[feedback-fbx-base-vs-anim]]); không commit/đẩy git của repo Unity khi chưa được bảo.

**Máy Linux (user 2026-11-17):** repo Unity ở `/home/ngocvb/Projects/endless-kicker`; mesh Pet mới (FBX cập nhật) ở `/home/ngocvb/Projects/endless-kicker/Assets/Kho/Skin/mesh/Pet_new/mesh/` (Pet_chrono_ouroboros, kabuto_striker, kitsune_nine_mist, lucky_neko, pinchy_balboa, steam_pug_turbo, tengu_swift + 5 con cũ). Lấy model mới từ đây, thay đường dẫn `C:\Users\Admin\Documents\Horus\endless-kicker\...`. File chốt nằm ở `/home/ngocvb/Desktop/DataHDD/Horus/tvc_source/3D ANIM/EndlessKicker/Pet_<ID>_<Tên>/`.
