---
name: feedback-self-fix-twist
description: "Khi sửa anim trong Frolvy mà gây xoắn bộ phận (cổ tay, tay, thân…), tự dò và sửa luôn, không đợi user báo"
metadata:
  node_type: memory
  type: feedback
  originSessionId: bd14d77e-27b2-4afa-bc35-21c26b672d82
  modified: 2026-11-11T10:04:41.852Z
---

Nếu trong lúc sửa anim làm xoắn bộ phận nào (xoay một vòng giữa hai key, lật 180°), tự sửa luôn trước khi báo xong. User 2026-11-11: "nếu trong quá trình sửa có gây ra xoắn các bộ phận, hãy tự sửa luôn".

**Why:** user đã phải hỏi hai lần (tay phải F22-25, tay trái F20-35) vì các key mình ghi lại bị lệch nhánh euler.

**How to apply:** sau mỗi lượt sửa, đo góc xoay thế giới giữa các frame liền nhau của các control đã đụng tới (cổ tay, pole, thân) trên cả đoạn sửa và vài frame sau; chỗ nào ≥ ~90°/frame thì đổi key sang biểu diễn euler tương đương gần key trước, đặt lại tangent, đo lại. Cách làm chi tiết ở knowledge/details/user_blocking.md (mục "Cổ tay bị xoắn"). Liên quan [[keep-existing-keys-when-editing]].
