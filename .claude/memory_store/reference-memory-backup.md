---
name: reference-memory-backup
description: memory is mirrored in repo .claude/memory_store via tools/claude_memory.py; run backup after writing memory
metadata:
  node_type: memory
  type: reference
  originSessionId: 705122b7-1507-4538-9549-6caf635810a2
  modified: 2026-11-03T05:47:30.133Z
---

User is switching to another AI account (2026-11-03). Memory is mirrored into `.claude/memory_store/` (local git) by `tools/claude_memory.py backup`; `restore` puts it back into `~/.claude/projects/<slug>/memory` on a new machine / Windows user. Run `backup` after every memory write.
