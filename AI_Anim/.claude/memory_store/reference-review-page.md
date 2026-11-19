---
name: reference-review-page
description: "Review Lab (renamed 2026-10-23 from \"review page\"; claude.ai artifact per anim) - where reviewers leave per-frame notes; read them with ArtifactData"
metadata:
  node_type: memory
  type: reference
  originSessionId: 7d2b80c9-f2b6-4906-8dd7-0a234b58ddaf
  modified: 2026-10-20T02:35:00.019Z
---

Review Lab (formerly review page; page titles are now "<anim> Review Lab") for playblasts: https://claude.ai/artifact/WN7idSA1JwaNimebZgQBHP (source work/review_page/index.html, clips in work/review_page/clips/*.webm).
SyncSketch-style layout the user asked for (playlist | viewer | notes, timeline fixed at the bottom, drag-scrub, wheel zoom, H/middle-mouse pan, A reset), notes in its db collection `notes` (clip, version, frame, part, text, strokes, author, status).
The user prefers WebM playblasts (lighter). Clips may set w/h (frame size) and views in CLIPS - Attack uses REF|ANIM 1454x660 from tools/playblast_ref.py; Attack listener cron polls rounds/Attack-<version>. When they say "đọc feedback trên trang review", list `notes`, fix in Blender, mark status done, add the new version to CLIPS and republish the same file.
Related: [[feedback-eye-first]], [[project-gaygor-idle-approved]].
**One page (artifact, own db) per animation** (user 2026-10-20 "tách trang review ra thành mỗi anim một trang riêng"):
master work/review_page/index.html keeps ALL CLIPS; `work/review_page/split_pages.py` writes pages/<key>/index.html filtered to one clip
(PAGES map: add a key for each new animation). Publish each page file to its own URL with files {"clips/<x>.webm|.jpg"}:
- Gaygor Attack: https://claude.ai/artifact/WN7idSA1JwaNimebZgQBHP (pages/gaygor_attack; old db still holds every older note)
- Gaygor Idle_Front: https://claude.ai/artifact/DyBMx8JhT8mHRKZaXEdqYC (pages/gaygor_idle_front; notes/rounds copied)
- SDR Attack: https://claude.ai/artifact/GifbYzqPZfPRFG3X9JFXbx (pages/sdr_attack; listeners poll this URL)
New pages start private: the user shares them from the Share menu. The note composer part list must match the character/props of that anim (PARTS in split_pages.py; user flagged Gaygor "khiên/Chùy" showing on the SDR page).
- SDR map06 Shoot: https://claude.ai/artifact/6ejD7yXjMakstHWF8i2n33 (pages/sdr06_shoot, clip SDR06_Shoot)
- SDR map06 Reload: https://claude.ai/artifact/9d5PshiRSA71PKi5gquNC9 (pages/sdr06_reload, clip SDR06_Reload)
- Gaygor Idle 133F (xoay trái phải, polish v1–v5, v5 đã duyệt): https://claude.ai/artifact/JK2CCuwPktgUCsD6k5fe6s (pages/gaygor_idle, clip Idle; tạo 2026-10-23 vì clip này duyệt trước khi có trang review)
- SDR03 Shoot (map3 nỏ, polish p1 = pb1, đã xuất FBX): https://claude.ai/artifact/ST9QK2GXM28jxEhQbqZ62Y (pages/sdr03_shoot, clip SDR03_Shoot; capabilities db + user profile + comments). Playblast gửi bằng `studio_cmd.py anim playblast right,front,top --label … --note …` (tắt hình nộm trước khi quay: chắn góc front).
