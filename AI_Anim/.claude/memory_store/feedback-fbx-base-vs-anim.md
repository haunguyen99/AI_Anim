---
name: feedback-fbx-base-vs-anim
description: Xuất FBX cho Unity: file Base = xương + mesh (T-pose/bind), file anim = CHỈ xương + anim, không mesh (user 2026-11-12)
metadata:
  type: feedback
---

Mỗi nhân vật/Pet xuất 2 loại FBX: **Base** (xương + mesh, đứng tư thế bind) và **file anim** (chỉ xương + clip, không Geometry/Deformer/Material/mesh).

**Why:** user 2026-11-12: lắp anim vào Unity không bị lỗi (mesh/avatar trùng gây lỗi khi gắn clip). Trước đó SDR05 cũng bị trả vì file anim còn mesh ([[project-g-dieloop]]).
**How to apply:** Pet Infinite Defense: `Pet_<Tên>.fbx` (Base) + `Pet_<Tên>_Idle.fbx`, `_Attack.fbx` (anim-only). Xuất rồi kiểm: file anim 0 mesh / 0 Deformer, tên xương trùng Base; chạy `tools/pet_fbx_finalize.py` (UnitScale 100). Hướng dẫn chi tiết ở `.claude/skills/animation/knowledge/details/export.md` mục "Base + anim-only".

**Tên file (user 2026-11-12):** nối bằng dấu gạch dưới `_`, KHÔNG dùng `@`: `Pet_<Tên>_Idle.fbx`, `Pet_<Tên>_Attack.fbx` (cho gọn, nhanh).
