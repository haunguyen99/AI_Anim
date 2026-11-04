---
name: project-sdr01
description: "SDR map1 (Roman legionary, dagger throw) — Idle + Shoot done and copied into Unity Map02 on 2026-10-29"
metadata:
  node_type: memory
  type: project
  originSessionId: 0082cad6-aead-4d12-8373-625c14cbcbd6
  modified: 2026-10-29T12:15:55.894Z
---

SDR01 = Shoot Die Repeat map1, Roman legionary throwing a dagger, rig `Map02/MC_char_map1_Rig.fbx` (Studio char `sdr01`), job `work/shoot_die_repeat/sdr01/`.
- Idle: 1 pose `p0_v5` (user posed it in Studio), 10 F loop.
- Shoot: 30 F full body, release F8, back to Idle at F30; blocking b8 → spline s1 approved.
- Rig skin of both elbows re-weighted (s3). On 2026-10-29 the rig plus `SDR01_MC_Idle.fbx` and `SDR01_MC_Shoot.fbx` (metas carry the game events `OnWeaponRelease`/`OnShootAnimationComplete`) were copied into Unity Map02. They were pushed to TungNV_Dev as f9a13447 (6 files). Nothing has been checked in the Unity editor yet.

**Why:** the next request will likely be a Unity check, a push to TungNV_Dev ([[feedback-sdr-git-branch]]), or a Reload/draw-dagger clip.
**How to apply:** read `sdr01/shoot_analysis.md` (sections A–P) and `MAP.md` before continuing.
