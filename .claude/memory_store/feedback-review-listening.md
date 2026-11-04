---
name: feedback-review-listening
description: No token-burning polling; Studio drawn notes: keep tools/notes_watch.py running in background (free file watch) so 'Gửi cho AI' wakes Claude; /check_fb still works
metadata:
  node_type: memory
  type: feedback
  originSessionId: 5777a8b4-d319-4595-b272-c4de7037baa5
  modified: 2026-10-22T01:12:39.370Z
---

2026-10-22 the user replaced the 10-minute polling loop (CronCreate on `rounds`) with the project skill `/check_fb` (`.claude/skills/check_fb/SKILL.md`): never start a polling cron after posting a version; end the turn and wait for `/check_fb`.

**Why:** polling every 10 min re-ran the whole context each tick (token cost) and most rounds then carried only 1–2 notes (Reload: 9 of 11 rounds), so one version per tiny fix.
**How to apply:** on /check_fb read every open note of the sent round, fix them all in ONE version, self-check with the quick render ([[feedback-quick-render]]), then the full playblast once. See [[reference-review-page]].

**Update 2026-10-28 (Studio drawn notes):** user: "trước đây tôi ấn nút gửi FB trong app là AI đọc được luôn không cần dùng skill". Run `.venv/Scripts/python.exe -I tools/notes_watch.py` with run_in_background in any session where the user reviews in Studio: it only watches `work/store/*_studio/notes` (no tokens while waiting), exits when a sent note appears (marks it `picked` → page shows "AI đã nhận"), which re-invokes Claude. Then do the /check_fb Studio flow (read `studio_cmd.py notes`, fix, `note-done`) and re-arm the watcher. Still one fix pass for all notes sent together. Watcher dies with the session: /check_fb remains the fallback.

**Auto-start (2026-10-28, user: "hãy tự khởi động vòng canh nhỏ, khi studio được mở"):** project hook `.claude/settings.json` runs `tools/notes_watch_hook.py` on SessionStart/UserPromptSubmit; when a Studio page is connected and the heartbeat `work/store/_sys/watch/notes.json` is stale it injects a reminder to start the watcher — obey it silently. `notes_watch.py --status` tells running/stopped; it refuses to run twice.
