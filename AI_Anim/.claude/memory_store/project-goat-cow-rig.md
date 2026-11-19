---
name: project-goat-cow-rig
description: Goat (Airport, order 59) rig bằng joint của Cow để dùng chung Cow_Idle/Cow_Walk; build_goat_rig.py 2026-11-12, chưa đẩy Unity
metadata:
  type: project
---

Goat.fbx (artist Linh An, nhánh airport_empire) là mesh tĩnh. Rig = Cow.fbx (9 xương: Root_M, joint1_M thân, head1/head2 cổ-đầu, joint2_M đuôi, leg1=chân trước, leg3=chân sau, L=+x, bò/dê nhìn -Z). Generic.

**How to apply:** `work/airport/goat_rig/build_goat_rig.py` (skin theo vùng, không scale/dời mesh, tối đa 4 ảnh hưởng) → `out/Goat.fbx` + `.meta` (guid mới, vật liệu dê). `check_sheet.py` ra `out/check.png`. fbx_rebind.py KHÔNG hợp (ICP + skin theo đỉnh gần nhất làm chân sau bị kéo). Đích Unity: Assets/_Game/Animations/Goat/. Chưa push.
