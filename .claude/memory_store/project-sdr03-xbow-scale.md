---
name: project-sdr03-xbow-scale
description: "Map3 crossbow 1.25× + arrow 1.3× thicker, 12 cm longer, pushed to Unity TungNV_Dev 90a6e31f (2026-11-03); the aim line is code and on hold"
metadata:
  type: project
---

On 2026-11-03 Thịnh sent feedback via Khải about the green-skinned crossbow character. That is `MC_char_map3`, in the Mayah folder, not Jungle. The changes were made in `work/shoot_die_repeat/xbow_scale/scale_props.py`:
- Crossbow 1.25×. The grip zone between the two hands is unchanged, so no anims needed edits.
- Arrow 1.3× thicker and 12 cm longer.

The user approved v2, and it was pushed to TungNV_Dev as 90a6e31f, rig file only.

The aim line is drawn by code (`SGameplayTouchAimController`), so it is a dev task. The user is asking Thịnh whether it needs a change, and it is on hold.

The flying arrow (`Projectile Arrow`) uses the same arrow mesh. Its head now travels about 0.28 m further ahead; this has not been checked in Unity.

**Why:** the next request is likely a Unity check, the aim-line follow-up, or a further size tweak.
**How to apply:** rerun scale_props.py with S/SA/DA arguments on `orig/`, see [[feedback-sdr-git-branch]] and [[project-shoot-die-repeat]].
