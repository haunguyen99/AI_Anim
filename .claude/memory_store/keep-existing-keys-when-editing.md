---
name: keep-existing-keys-when-editing
description: "In Frolvy, edits must keep the user's existing keys (frame, value) untouched; add new motion only on new inbetween frames"
metadata:
  node_type: memory
  type: feedback
  originSessionId: a81c2cb7-d80d-4705-a6fd-a5851ab16438
  modified: 2026-11-06T02:37:35.689Z
---

User 2026-11-06 (Hero_Blade_Attack_01_v1.fv): "các sửa đổi phải ưu tiên giữ frame gốc đã có sẵn". I had overwritten the user's keys at f8/f12 (hip ty, right-foot ty/tz) to add a hip dip + foot lift + overshoot; user objected, I undid it.

**Why:** the user's own keys (here f0, f8, f12 on the Base layer) are the approved poses; AI work is only the added inbetweens/breakdowns around them.

**How to apply:**
- Before editing, list the existing key frames and values and treat them as read-only. Never `set_attr` on a frame that already has a key.
- Put new motion (dip, lift, overshoot, anticipation) on NEW frames between the user's keys, e.g. a dip bottom at f6 that settles into the original f8 key, an overshoot at f10 before the original f12 key.
- If a request seems to need a change to an existing key (e.g. "reach X at frame 8"), say so and ask, or realise it with inbetweens only.
- Frolvy notes: `tween_keys` only keys channels that change, so for other channels use `select([node])` + `set_attr` + `set_key` per frame; `set_attr` on a non-keyed frame writes nothing. One execute_code = one undo step, so undo restores exact originals.

Related: [[polish-keeps-blocking-poses]], [[frolvy-layer-edit-additive]].
