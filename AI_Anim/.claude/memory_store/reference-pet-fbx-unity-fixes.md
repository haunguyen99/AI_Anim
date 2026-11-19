---
name: reference-pet-fbx-unity-fixes
description: FBX Pet từ Frolvy vào Unity bị vỡ mesh / lỗi Copy Avatar: 3 lỗi + công cụ sửa đã kiểm bằng Unity batchmode (Pebble Turtle 2026-11-12)
metadata:
  type: reference
---

FBX ASCII của Frolvy (Base + anim-only) cần 4 bước sau `fbx_ascii_keep.py --root DEF_Root_M` trước khi vào Unity:
1. **Đơn vị**: `pet_fbx_finalize.py` (UnitScaleFactor 100, tên take = Idle/Attack).
2. **Base vỡ skin** (đầu/chân bay khỏi thân): Unity lấy `Transform` của Cluster làm bindpose, bỏ `TransformLink`, và Frolvy không ghi BindPose → `tools/fbx_unity_bind.py in out` (thêm BindPose + Transform = nghịch đảo TransformLink). Base không giữ clip tĩnh: `tools/fbx_strip_anim.py`.
3. **File anim lỗi "Cannot find root motion transform 'DEF_Root_M'" khi Copy From Other Avatar**: anim-only chỉ có một nút gốc nên Unity coi nó là gốc file; Base có mesh cùng cấp → `tools/fbx_add_sibling.py in out` (thêm Null `Dummy` cùng cấp, chỉ file anim).
4. Kiểm bằng Unity batchmode (Unity 2022.3.62f2 có trên máy, project tạm ở %TEMP%): Editor script in `BakeMesh().bounds` so `sharedMesh.bounds` ở bind (phải bằng), ImportAsset rồi đọc log "Import Messages", SampleAnimation kiểm đường dẫn xương.

**Why:** Pebble Turtle 2026-11-12, user báo mesh vỡ rồi file anim đỏ lỗi, sửa 3 vòng. Mecha Pup / Tiny Chick xuất cùng đường Frolvy nên có thể dính cùng lỗi.
**How to apply:** chạy 3 tool trên mọi Pet mới trước khi chép vào Unity; thấy lỗi mới thì đọc log Unity batchmode thay vì đoán. Chi tiết: `.claude/skills/animation/knowledge/details/export.md`, [[feedback-fbx-base-vs-anim]], [[reference-pets-unity-folder]].
