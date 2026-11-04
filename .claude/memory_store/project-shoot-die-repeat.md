---
name: project-shoot-die-repeat
description: "Shoot Die Repeat project intake (2026-10-20) - Roman legionary + gladius, clips Idle + Attack, NO reference video, Unity 30fps"
metadata:
  node_type: memory
  type: project
  originSessionId: 8218d775-e470-4bab-8fca-6e6d0eb37e54
  modified: 2026-10-20T07:30:25.497Z
---

Shoot Die Repeat (Assets/Shot-die-repeat/MC_char_map2_Rig.fbx + T_Color_ShotDieRepeat.tga): low-poly Roman legionary,
1.94 m, 23 bones (no fingers/toes, mitten hands), gladius mesh `knife1` rigid on bone `slingshot_0` (child of Wrist_R,
rest lies on the floor 1.34 m in front -> must be placed in the right hand for P0). Faces -Y.

User asked (2026-10-20) for clips **Idle** and **Attack/Shoot**, **no reference video** (Claude designs key poses,
user approves each), target **Unity 30 fps**. Scene built headless by `work/blender/build_sdr.py` -> `work/shoot_die_repeat/blender/sdr_char.blend`
(Ref_front/back/left/right/top/game ortho cams), renders in `work/shoot_die_repeat/sdr/look/`.

Gameplay (concept + competitor video, 2026-10-20): 2D side-scroller, character faces screen-right, knife THROWER
(left arm points at target = aim line, right hand cocks the gladius behind the shoulder). Decisions by user:
- Only the **right view** matters (in-game camera = `Ref_right`, from the character's right side, screen right = front).
- **Idle = one single static pose** (no breathing loop).
- **Attack = throw, then recover straight to Idle; no draw-new-knife action.** Demo the knife flying out and sticking
  into a target so dev can code the projectile. Aim up/down is done by code (IK/aim), poses aim horizontally.
- Character can walk while aiming -> Attack must work as an upper-body layer (mask from Spine1 up, legs = Idle stance).

**Why:** first project without ref; pipeline steps that compare REF|ANIM are replaced by pose design + user approval.
**How to apply:** follow [[feedback-coarse-to-fine]] and [[feedback-stepped-blocking]]; quality bar [[project-gaygor-idle-approved]].
- 2026-10-20 status: Idle v12 approved, then **Idle v13** stance from review note on SDR Attack blocking_v1 F16 ("hông cao
  hơn, thu hai chân gần nhau"): root_drop 0.13 -> 0.06, feet y -0.38/0.34 -> -0.27/0.23 (old file sdr_p0_v12.blend); then **Idle v14** (note "hông cao lên thêm, gối cong quá"): root_drop 0.02, knees 22°/8° -> user wants a tall, relaxed stance, not a deep lunge.
  Idle v15 (head back, knife flat to camera, aim arm level, back knee 26°); Idle back to **v15** (= Attack blocking_v4; v16–v18 forward-lean tries rejected "quá tệ"); then Idle v19 = v4 + hip only (tilt 7.5°, push 3 cm, "50% of A" picked from stills); Idle v20 (knife arm lower: upR z -0.55, aim arm +5°, back foot y 0.20, drop 0.038); Attack **blocking_v8 approved** ("Oki rồi", 2026-10-20) → spline v1–v3 (26F, recover retimed; v4 rolled back) → polish v1/v2 (overlap delays, knife hit shake, board fixed, F20–F26 pure Idle) → **polish_v3** (2026-10-21, own suggestions approved from stills: stronger wind-up, release under chin, aim arm back by F11). Exported: work/shoot_die_repeat/sdr/export/SDR_MC_Attack.fbx, SDR_MC_Attack_KnifeInHand.fbx (knife never leaves the hand), SDR_MC_Idle.fbx, SDR_MC_Attack_events.json. Review page: see [[reference-review-page]]. polish_v4 (aim arm returns over ~5F) → polish_v5 (2026-10-21: aim arm folded at the release F6); both FBX re-exported. **polish_v5 APPROVED ("done", 2026-10-21)** — SDR Attack is finished; final files in work/shoot_die_repeat/sdr/export.
