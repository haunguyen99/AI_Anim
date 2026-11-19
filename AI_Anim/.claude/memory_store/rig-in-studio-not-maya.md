---
name: rig-in-studio-not-maya
description: "rig một model theo rig mẫu của team (.ma AdvancedSkeleton) thì làm trong Studio (Rig workspace), không dựng trong Maya"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 57479d6c-878f-4c9c-87f3-a773d2de78cc
  modified: 2026-11-09T06:57:31.107Z
---

Khi người dùng đưa model FBX + một rig mẫu Maya (.ma) và bảo "rig theo file mẫu": làm trong Studio, không mở Maya / AdvancedSkeleton.

**Why:** 2026-11-09 Hero_Axe (Mob Era) mình mở Maya thứ hai, refit FitSkeleton + rebuild AS + geodesic bind; user ngắt: "làm trên studio chứ không phải ngay trên maya".

**How to apply:** đọc .ma chỉ để lấy tên + cây khớp + vị trí (tham khảo). Nhập FBX bằng `/api/fbx/new-char`, viết `work/rig_lab/ref_<id>_<mẫu>/ref_skeleton.json` (tên khớp mẫu, vị trí đo trên model mới), `chars/<id>.json` names_from + auto_from_ref + cfg.extra cho khớp ngoài template (ngón cái đốt 4, chuỗi tóc/nơ, WeaponCtrl), rồi `/api/rig/build` → Studio Rig: Tính skin → Hammer tự động ×2 → `mirror_skin.py` → `lbs_test.py`. Xem [[reference-studio-bridge]].
