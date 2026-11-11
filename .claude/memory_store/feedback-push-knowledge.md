---
name: feedback-push-knowledge
description: skill /push tự đẩy kiến thức (knowledge, skill, memory_store) lên git, mỗi /push và cuối mỗi việc có bài học mới (user 2026-11-11)
metadata:
  type: feedback
---

Kiến thức không để nằm lại chỉ trên máy: /push commit file kiến thức đang sửa dở rồi đẩy; cuối việc có ghi bài học thì tự đẩy riêng phần kiến thức bằng `push_source.py --only .claude/skills .claude/memory_store --committed`.

**Why:** user 2026-11-11 yêu cầu thêm nhiệm vụ tự đẩy kiến thức vào skill push, vì kiến thức là phần quý nhất của repo.
**How to apply:** xem mục "Kiến thức: tự đẩy lên git" trong `.claude/skills/push/SKILL.md`; dry-run có XOÁ/file lạ thì dừng hỏi. Liên quan [[feedback-update-knowledge]], [[reference-github-source]], [[reference-memory-backup]].
