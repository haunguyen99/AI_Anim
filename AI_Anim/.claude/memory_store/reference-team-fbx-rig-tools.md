---
name: reference-team-fbx-rig-tools
description: "Animate on a team Unity FBX rig without Blender/Studio rig — tools/rigpose.py + tools/poselab_model.py (SDR03 map3 crossbow, 2026-10-28)"
metadata:
  node_type: memory
  type: reference
  originSessionId: 01e821e4-a999-46ec-8786-cd29946496ce
  modified: 2026-10-28T10:13:39.712Z
---

- Studio `rig.useFbx` keeps only the 25 body bones (drops prop `slingshot_*`, hair `joint*_M`, `root`) → unusable when a clip must animate props/hair on the team skeleton.
- `tools/rigpose.py`: FK on FBX bind, hinge IK for arms, LBS with the team weights, textured render (`tools/render_fbx_tex.py`), reads frames of team anim FBX. `tools/poselab_model.py`: rig + texture + poses → Pose Lab glTF (vertices in METERS, meshes at scene root, IBM = inv(0.01·bind)); cm vertices made the Pose ghost 100× (user screenshot 2026-10-28).
- Register with `clip_registry.py pose-version … --names "slingshot_1=Dây nỏ,joint1_M=Bím tóc 1"` so extra joints show in the Pose joint panel.
- Pushed to GitHub main e841afe. Job scripts: work/shoot_die_repeat/sdr03 (p0_build, shoot_block, rig_check, rigfix). Related: [[reference-codex-img]], [[project-studio]].
