---
name: feedback-push-knowledge
description: /push luôn gộp với GitHub main trước khi đẩy (tools/knowledge_merge.py, gốc chung từng file) và tự đẩy kiến thức; master và main KHÔNG chung lịch sử (user 2026-11-11)
metadata:
  type: feedback
---

Trước MỌI lần đẩy chạy `tools/knowledge_merge.py [--apply]`: gộp từng file giữa máy này, origin/main và gốc chung của file (tự tìm theo lịch sử). Kiến thức (skill, memory_store) còn được tự đẩy riêng cuối mỗi việc có bài học (`push_source.py --only … --committed`).

**Why:** user 2026-11-11. `push_source.py` ghi file máy này đè lên main và coi file máy khác vừa thêm là XOÁ: lần đầu thử ghi đè sẽ mất plugin Frolvy loop_seam/hero_textures/rig_pose_tools, bản mới animation-director, anim_kit, memory và 9 skill/memory chưa từng có ở máy này. master và main không chung lịch sử (main = chỉ mã nguồn), nên không merge/pull git được. `work/clips.json` gộp theo mục (id), không theo dòng.
**How to apply:** xem mục "Gộp với GitHub trước mỗi lần đẩy" trong `.claude/skills/push/SKILL.md`. Dry-run có XOÁ ngoài ý muốn thì dừng hỏi. Pushed 2610052 (2026-11-11). Liên quan [[feedback-update-knowledge]], [[reference-github-source]], [[reference-memory-backup]].

**Cập nhật 2026-11-11 (nhắc + lịch):** user chọn cả hai. Hook `tools/knowledge_sync.py hook` (SessionStart + UserPromptSubmit) nhắc hỏi người dùng khi có kiến thức mới chưa đẩy / GitHub có bản mới; lịch Windows `AIAnim_KnowledgePush` 17:10 (sau 17h) mỗi ngày chạy `knowledge_sync.py autopush` (gộp sạch + đẩy, gặp xung đột thì dừng, ghi needs_merge). Gỡ/đổi giờ: `tools/knowledge_sync_install.ps1 -Remove | -Time`. Xem `.claude/skills/push/SKILL.md` mục "Nhắc và tự đẩy kiến thức theo lịch".
