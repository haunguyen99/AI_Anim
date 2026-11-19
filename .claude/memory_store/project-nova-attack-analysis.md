---
name: project-nova-attack-analysis
description: "NovaAttack (Nova_Attack_v1.2.fv, 63F): nhịp, quy ước rig, công thức overlap/tay/chân, bẫy script Frolvy Linux"
metadata:
  node_type: memory
  type: project
  originSessionId: 171f567e-8034-4b41-bb87-8fe06fecb9c1
  modified: 2026-11-17T08:15:00.910Z
---

Phân tích đầy đủ ở `work/runner_hybrid/NOVA_ATTACK_REFERENCE.md` (đọc trước khi làm Cast / anim Nova khác). Script ở `work/runner_hybrid/anim/` (atk_lib, nova_attack_polish / loop2 / lefthand / legs, fvc.py).

Điểm chính: clip 0-62, loop F62 = F0; bắn ở F21-22 (tay phải lùi 26,5 cm trong 1F); root hover 2,4-31,9 cm (idle 12,2); fps trong cảnh = 30 (GDD ghi 24, chưa chốt); tay dài 42 cm, súng 133 cm nên tay trái phải "khối cứng với súng" + key vai; chân dài 66 cm, duỗi thẳng thì không trễ được.

**Why:** người dùng chỉnh nhịp/pose thân nhiều vòng (nhịp đều quá, hồi nhanh/chậm, hold thân ngả sau), các bước làm tay trái và chân đã chốt "oke" nên là chuẩn cho anim sau.
**How to apply:** Cast/Showcase dùng lại công thức trễ thời gian (chuỗi hông → Spine → Ngực → Cổ → Đầu, vai/tay/khuỷu trễ 1-1,7F, chân lệch nhịp 1/1,5-3F); `set_attr` không tự key (phải select + set_key); đừng đọc key hiện có làm key gốc khi chạy lại; đóng cửa sổ chưa lưu không được, dùng `undo`. Liên quan [[reference-frolvy-linux-bridge]], [[feedback-hand-overlap-recipe]], [[project-nova-idle-workflow]].
