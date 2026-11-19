---
name: frolvy-skin-arm-sleeve-rigid
description: "Skin vai/tay trong Frolvy — ống tay trên 100% Shoulder (không xương thân), kiểm bằng camera cận chứ không chỉ độ dài cạnh; tính ngược trọng số bằng solve_shoulder_skin.py"
metadata:
  node_type: memory
  type: feedback
  originSessionId: c79b5cd8-2885-4196-aeaa-9b66b9730c02
  modified: 2026-11-13T08:22:10.260Z
---

Nova (Runner_Hybrid) 2026-11-13: xoay CTL_Shoulder bị móp. Sửa đúng khi: các vertex phần tay (ống tay trên, kể cả vòng sát nách) chỉ bám Shoulder (+Elbow gần khuỷu), **không** Chest/Spine1/Neck/Scapula (user: "các vertex phần tay sẽ không bị ảnh hưởng bởi các joint thân").

**Why:** đo độ giãn cạnh (edge_stretch) nhìn đẹp nhưng mắt vẫn thấy ống tay thót hình nêm vì mép dưới còn bám thân. Phải xem hình.
**How to apply:** test bằng CTL_Shoulder ở góc user hay dùng (T-pose gốc, hạ tay 50–70°), cả hai bên; xem bằng api.create_camera + set_transform [x,y,z] rot 0 (nhìn -Z) + look_through, xong `look_through("")` và delete_node. edge_stretch đo so với pose CTL hiện tại, nên reset CTL về 0 trước. Công cụ: work/runner_hybrid/rig/solve_shoulder_skin.py (tính ngược trọng số vùng vai bằng numpy trong .venv, dữ liệu qua %TEMP%/nova_skin_in/out.json), kết quả shoulder_weights_solved.json. Xem [[frolvy-game-rig-base-joints-only]], [[project-runner-hybrid]].
