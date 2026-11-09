---
name: frolvy-loop-seam-smooth
description: Looping anims (idle / run / walk) in Frolvy - after every finished edit round run loop_seam.smooth(api) so F-last joins F1 smoothly; it works per layer
metadata:
  node_type: memory
  type: feedback
  originSessionId: d1ba2fc2-259c-450d-a79c-ac6f7bc1b378
  modified: 2026-11-05T07:19:34.921Z
---

Rule for every looping clip (idle, run, walk) made in Frolvy, user 2026-11-05: "smooth frame đầu cuối để anim chuyển động mượt hơn … ghi lệnh tự động smooth đầu cuối sau khi sửa xong 1 lệnh cho các anim idle run walk" (after "tay vẫn bị giựt đầu cuối").

**Why:** F-last == F1 by value is not enough. RPG2 Hero Idle: the additive layer `fix_r1_tay_xoay_it_dich_nhieu` held wrist / blade rotation that drifted (wrist rx 0 → -1.3 deg, blade rz 0 → -0.5 deg) so the last key never met the first, and the 40 cm blade turned it into a 16 mm/frame spike at the seam. The end keys also get one-sided auto tangents.

**How to apply:** at the end of EVERY finished edit round on a loop clip (one round, not every execute_code call), BEFORE the reply (and before a playblast if one was asked), run in Frolvy via execute_code:
`exec(open(r'D:\Project\AI_Anim\tools\frolvy_plugins\loop_seam\loop_seam.py', encoding='utf-8').read()); smooth(api)`
It soloes each layer in turn, de-trends any channel whose last key differs from its first, gives both end keys one shared tangent, sets cycle infinity, restores solo / active layer, then prints `seam OK` or the probes that still jump. Fix and re-run if it lists problems or `NOT closed`. Say in the reply that the seam was smoothed (one line). Idempotent. Also in Frolvy Plugins menu: Smooth Loop Seam.
Never use `set_attr` / `set_key` inside an additive layer to fix values (they write Base + layer and compound on every call), and `api.move_key(path, f, f, value)` takes the layer's OWN value (read it with `set_layer_solo`). Frolvy is restarted from the saved .fv sometimes: check `api.layers()` before trusting key values. Related: [[rpg2-hero-playblast-after-edit]].
