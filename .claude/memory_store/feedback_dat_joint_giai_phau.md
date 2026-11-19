---
name: feedback-dat-joint-giai-phau
description: "Hậu chỉnh joint MeoTom (2026-11-19): joint phải là điểm xoay giải phẫu chứ không phải tâm mặt cắt; số đo + quy tắc cổ chân, gót, bàn chân xoè 40°, tai, hàm, cột sống, đuôi, hướng orient"
metadata:
  node_type: memory
  type: feedback
  originSessionId: a0845777-cfa4-4ed3-af2a-fdb53cacba75
  modified: 2026-11-19T04:38:07.848Z
---

Khi rig nhân vật thú/chibi, không đặt joint bằng tâm mặt cắt mesh. Hậu dời 18/33 joint của MeoTom hơn 2 cm (TB 2,5 cm, lớn nhất 8,4 cm).

**Why:** tôi dùng tâm bbox mặt cắt rồi báo "lệch ≤1,5 cm" trong khi vị trí vẫn sai giải phẫu; mesh bất đối xứng làm bbox lệch; cổ chân đặt ở chỗ thắt (y 0,115) thay vì trên gót (0,065); bàn chân xoè ~40° nhưng tôi đo 8° bằng PCA đáy bàn chân.

**How to apply:** đọc mục "Đặt joint cho nhân vật thú / chibi" trong `.claude/skills/frolvy_rig/SKILL.md` (số đo từng vùng). Tóm tắt: cổ chân thấp trên gót, gót dưới cổ chân, hướng bàn chân từ ảnh nhìn trên tới mút múi ngón (không PCA), hông gần đường giữa, cột sống chia đều, vai/scapula gần đường giữa, gốc tai sát đỉnh đầu vào trong (đặt từng bên), JawEnd ở mút môi dưới, đuôi thêm đốt ở chỗ cuộn, chuỗi đuôi/tai/hàm aim X dọc xương, thân/cổ/đầu giữ trục thế giới. Mỗi bước chụp nhìn trước/bên/trên gửi Hậu và chờ gật; người dùng đã sửa joint thì giữ nguyên, chỉ aim lại hướng. Xem [[feedback-le-tan-phan-hoi-ngay]] cho cách báo.
