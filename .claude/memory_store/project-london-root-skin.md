---
name: project-london-root-skin
description: London MC rig có joint root dính skin (277 đỉnh) → đã chuyển sang Root_M, đẩy TungNV_Dev 7a7609b5 (2026-11-06)
metadata:
  type: project
---

Việt Tùng báo (G-DieLoop, thread Khải "3D - 0511") nhân vật London méo giống map Roma ngày trước; user chẩn đoán root có skin. Đo: `root` skin 277/1199 đỉnh mesh `MC_char_map8` trong `London/MC_char_map6_Rig.fbx`. Sửa bằng `work/shoot_die_repeat/sdr06/rebind/root_to_rootm.py` (cộng weight root vào Root_M, cluster root rỗng); đo bằng `root_weight.py`. Đẩy TungNV_Dev 7a7609b5 (checkout local đang TungNV_Dev, commit thẳng). Chưa render kiểm hình, chưa trả lời Tùng trong thread; Roma (`MC_char_map2_Rig`), Jungle (4 đỉnh, weight 0), Pirate chưa/không cần sửa — Roma chưa đo.

**Why:** root di chuyển thì kéo đỉnh skin theo → méo thân.
**How to apply:** rig nhân vật mới nào cũng chạy root_weight.py kiểm root = 0 đỉnh trước khi đẩy. Liên quan [[project-sdr-map06]], [[project-sdr06-reload-gun-f1]].
Quét Unity 2026-11-06 còn root có skin: SDR06_MC_Base (277), EN_zom2_map6 (133), EN_zom1/zom2_map2_Rig (32), map1 Rig/Base Rau1 (4). Chưa sửa.
