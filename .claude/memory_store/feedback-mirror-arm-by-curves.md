---
name: feedback-mirror-arm-by-curves
description: Khi cần đối xứng tay trái/phải (run, walk, idle): copy theo đường cong, cùng nhịp, cùng quỹ đạo thế giới; đọc FK/IK nguồn trước; lệnh mirror_limb
metadata:
  type: feedback
---

Người dùng chốt 2026-11-26 (Hero Blade/Staff run): "khi tôi cần đối xứng thì ưu tiên cách làm như này" cho run, walk, idle. Cách: hai tay **cùng đường cong, cùng frame, cùng quỹ đạo cổ tay trong thế giới**. Quy tắc kênh (rig Rig Builder, trái/phải là gương): tx ×-1, ty/tz giữ, rx giữ, ry/rz ×-1. Lệnh: `tools/frolvy_plugins/mirror_limb` → `mirror_arm(api,'L')` (qua `tools/frolvy_call.py <cổng> -`).

**Why:** 3 lần làm sai trước khi đúng. (1) Chép các control FK của tay trái nhưng tay trái đang IK (`CTL_ArmSwitch_L.fkIk`=1) nên FK chỉ là số cũ, anim thật ở `CTL_IKWrist_L` + `CTL_PoleArm_L`. (2) Lật theo mặt phẳng ngực: ngực xoắn 3–16° khi chạy nên cổ tay phải thấp hơn 24 cm, đường cong lệch; số đo "đối xứng theo thân = 0" không phải điều người dùng cần. (3) Tự thêm độ lệch nửa nhịp khi người dùng không yêu cầu (người dùng: "sao lại làm lệch nhịp"). Người dùng muốn nhịp y hệt, trừ khi nói lệch.

**How to apply:** đọc switch FK/IK của tay nguồn trước; đo kết quả bằng đường cong + vị trí cổ tay thế giới, không chỉ theo thân; báo thẳng góc khuỷu khác nhau (thân xoắn làm vai bất đối xứng, ~47° ở F3–F5 của run) và đề nghị hạ pole nếu xấu. Bẫy Frolvy: `set_attr` trên kênh chưa có key không dính → tạo key mọi frame trước (set_key) rồi mới ghi; `delete_key` cần frame kiểu int; mỗi lần chạy script có thể tốn nhiều bước undo (phải undo 3–4 lần), kiểm lại bằng số đo sau undo. Chân chưa có lệnh (cùng ý với IKAnkle / PoleLeg). Liên quan: [[reference-frolvy-linux-bridge]].

**Bản đối pha (2026-11-26, Hero Gun run):** người dùng cũng cần tay phải lệch nửa chu kỳ để hai tay vung ngược nhau → skill `mirror_arm_run_walk`, lệnh `mirror_arm(api,'L',shift=N/2)` (Catmull-Rom tuần hoàn, áp cho IKWrist + PoleArm + Scapula cùng độ lệch). Phép kiểm gương của Scapula phải lấy nhóm cha `CTL_Chest_M_follow`, không phải `CTL_Chest_M`.
