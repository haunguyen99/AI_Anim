---
name: ai-animation
description: Animate a user's rigged 3D character by eye to match multi-view reference videos of that same character (front/back/left/right, synchronized, e.g. AI-generated or hand-drawn). Claude reads the reference frames, writes keyframe poses in keys.json, and checks the model overlaid on the reference from every view in headless Blender. Use when the user wants keyframes/an animation of their model copied from reference videos or turnarounds, or wants to refine such a result.
---

# AI Animation: eye-keying from multi-view references

The reference videos show **the same character** as the 3D model, filmed from
standard views (front / back / left / right). All views are synchronized:
frame N is the same moment in every view. Claude works like an animator:

1. pick the key poses on the timeline,
2. write each pose as bone directions/rotations in `keys.json`,
3. render the model from the reference cameras, laid semi-transparently over the reference,
4. compare, correct, add breakdown keys where the in-betweens drift.

No pose-estimation model is used. Claude's eyes are the tracker.

```bash
PY=".venv/Scripts/python.exe"   # run from the project root
$PY legacy/blender_tools/keyanim.py prep    --work work/<job> --view front=F.mp4 --view left=L.mp4 [--view back=… --view right=…]
$PY legacy/blender_tools/keyanim.py ref     --work work/<job> --frames 1,40          # reference frames with pixel rulers
$PY legacy/blender_tools/keyanim.py calib   --work work/<job> --view front --top 212 --ground 688 --center 355
$PY legacy/blender_tools/keyanim.py inspect --work work/<job> MODEL                  # rig.json, mapping.json, controls.json, keys.json
$PY legacy/blender_tools/keyanim.py look    --work work/<job> --frames 1,40 [--views front,left] [--stack cols]
$PY legacy/blender_tools/keyanim.py video   --work work/<job>                        # compare.mp4, every frame, all views
$PY legacy/blender_tools/keyanim.py export  --work work/<job> --out work/<job>/result.fbx
$PY legacy/blender_tools/keyanim.py view    --work work/<job>                        # GLB + web refs for the 3D viewer
```

**3D viewer** (`tools/viewer/index.html`, three.js): after `view`, start the
`anim-viewer` entry in `.claude/launch.json`, which runs
`python -m http.server 8765` at the project root. Open
`http://localhost:8765/tools/viewer/?job=work/<job>`. The viewer offers
orbit, pan and zoom, Front/Back/Left/Right/Top/3-4 cameras, ortho,
skeleton, wireframe, a timeline with key markers, play speed, and the
reference video of the current view synced to the frame. Every job that has
been run through `view` appears in its dropdown (from `work/index.json`).
Run `view` after each change to `keys.json` so the GLB stays current.

If `.venv` is missing, run `tools/setup.ps1`. Blender 4.5 runs headless.

## Workflow

0. **Animation brief first — think like a senior game animator.** Before
   any key, watch the whole reference (zoomed contact sheets of every view,
   plus measured motion curves). Write `work/<job>/anim_brief.md` covering:
   - what the animation is: idle, attack, locomotion; loop or one-shot; in-place or root motion;
   - what the character is doing and why;
   - the **feel**: weight, mood, personality;
   - the beats, with frame numbers, for each layer (breath, look, the main action);
   - which animation principles drive it (lead and follow, overlap, arcs, anticipation, settle);
   - what NOT to copy: reference noise and AI or drawing wobble;
   - gameplay needs: blend pose, readability from the game camera;
   - a pose-to-pose key plan.

   Key from the brief's intent and timing. Use the reference to check
   intent, not as a pixel target. Get the user's agreement on the brief
   before keying.
1. **Prep.** Run `prep` with every view the user gave. It prints suggested
   keyframes (pauses and turning points, from pixel motion) and writes
   `sheets/<view>.png`, a timeline thumbnail every 5 frames. Read the sheets
   and describe the action in phases before keying anything.
   **Check the view names first.** Files are often named by where the camera
   sits *on screen*, not by which side of the character it films. In the
   `left` view (camera at the character's left) the character faces image
   left, and in the `right` view it faces image right. Cross-check with
   something asymmetric: which hand holds a prop in the front and back views.
   If the names are swapped, pass them swapped to `prep`, for example
   `--view left=…_right.mov`.
   The character is often small in the frame. `ref` and `look` crop around
   the calibrated character automatically; use `--crop x0,y0,x1,y1` for a
   manual zoom.
2. **Calibrate each view.** If the background is an engine grid (for example
   a Unity Scene view, where 1 cell = 1 m), measure the grid spacing in pixels:
   that gives the exact scale. Then set `--ground` on the floor line and
   `--top` = ground − height_m × px_per_m, using `character_height_m` from
   `controls.json`. This is more reliable than measuring the head of a
   crouching character. Otherwise, pick a frame where the character stands straight
   and run `ref` on it. Read the yellow rulers, which are in original
   reference pixels. Note three values per view: the y of the head top, the y
   of the soles, and the x of the pelvis centre. Run `calib` for each view
   with those values. Then run `look` on a frame with an empty pose. The
   rest-pose model should stand on the same ground line, at the same height
   and position. Re-calibrate until it does, because every later comparison
   depends on this.
3. **Inspect the rig.** Run `inspect`, then read `mapping.json` (the joint ↔
   bone guess) and `controls.json`, which lists each key bone with its parent
   and its `rest_aim` (where it points in rest pose). Fix the mapping if a
   side or bone is wrong. It drives the review skeleton and the aim chains.
4. **Key in passes.**
   - *Blocking:* key the main poses only, at the suggested frames and phase
     changes. Work torso first (root, spine), then limbs from the shoulder or
     hip outward, then head.
   - *Check:* run `look` on the keyed frames. Fix the worst view first.
   - *Breakdowns:* run `look` on frames midway between keys. Where the model
     drifts from the reference, add a key there.
   - *Final:* run `view` and open the 3D viewer for the user. Run `video` and
     send `compare.mp4`. Run `export` if they want an FBX or GLB.
5. Run `look` on at most ~4 frames per call. Read every image it produces;
   never claim a pose matches without looking.

## Per-frame keys: silhouette fitting (when the reference is a render of this model)

Eye keys give the poses; the fitter then keys **every frame**. For each frame
it renders the model's silhouette and colour-part labels (red / dark / gold /
purple), compares them with the reference in all views (IoU), and adjusts the
bone rotations by pattern search. All of this runs in numpy, outside Blender.

```bash
PY=".venv/Scripts/python.exe"
"$BLENDER" -b --factory-startup -P legacy/blender/key_pose.py -- dump --work work/<job>   # rig_np.npz: mesh, weights, cameras, current anim
$PY -c "import sys; sys.path.insert(0,'tools/fit'); import refmask; refmask.build('work/<job>'); refmask.build_labels('work/<job>')"
$PY tools/fit/check.py     work/<job> [basis.npy] --frames 1,52    # silhouette diff image + IoU
$PY tools/fit/labcheck.py  work/<job> [basis.npy] --frames 1       # colour-part maps, ref | model
$PY tools/fit/refine_cams.py work/<job> fit_basis.npy --frames 1,30,60 --range 20 --zoom 0.97,1,1.03
$PY tools/fit/fit_all.py   work/<job> --jobs 14 --scale 0.3        # all frames, parallel -> fit_basis.npy
$PY tools/fit/smooth.py    work/<job> --loop                       # -> fit_smooth.npy (use --loop for cycles)
```

Second and later passes (start each one from the previous result: bake it, then `dump`):
```bash
$PY tools/fit/fit_grip.py work/<job>                                 # one prop-in-hand offset for the clip -> grip.json
$PY tools/fit/fit_all.py  work/<job> --jobs 14 --scale 0.3 --extra "--reg 0.00005 --temporal 0.0002 --fixed-grip --warmup 3"
$PY tools/fit/smooth.py   work/<job> --in fit_basis.npy --loop
$PY tools/fit/glb_bake.py work/<job> --basis fit_smooth.npy --out anim.glb   # straight into the GLB, ~1 s, no Blender
$PY legacy/blender_tools/keyanim.py view --work work/<job> --fast                   # refresh viewer.json (+ calibrated cameras)
```
Check the result in the viewer's **Overlay** mode (V). It renders the model
through the calibrated reference camera, with the reference video as the
background. `glb_bake.py --basis basis0 --check` confirms that the GLB writer
matches Blender's own glTF export (bones go through C·M·K·C⁻¹, the Z-up→Y-up
conjugation). Blender is only needed to export FBX.

Set `"bake": "fit_smooth.npy"` in keys.json. After that, `look`, `view`,
`video` and `export` key every frame from the fit. Re-run `dump` after a bake,
so the next fit starts from the current result.

Lessons from the first run (idle clip):
- Refine the camera offsets first, alternating with pose fits. A view off by
  ~30 px means no pose can satisfy every view.
- Mirrored views (front/back, left/right) are not exact mirrors of each other.
  Always fit with all four views.
- `fillPoly` with many triangles uses an even-odd rule, so overlapping
  triangles cancel. Fill each triangle separately.
- Pin held props to their hand (`attach`) while fitting. A free prop drifts
  toward other dark regions.
- Keep regularisation tiny (≈1e-5 per deg²). A strong prior stops the fitter
  from making the 10–20° corrections that eye keys need.
- Measure with numbers (`check.py`) before judging from small images.
- Fitting each frame independently jitters (up to 33°/frame). Add a
  temporal penalty, use small search steps when warm-started, give each
  parallel chunk a warm-up, and fix the grip for the whole clip.
- Calibrate the cameras level, with world up. Deriving "up" from a hunched
  rig's hip→shoulder line tilted every view by 6° and capped the side-view
  IoU at about 0.75.
- Progress on the idle clip (mean silhouette IoU): eye keys 0.696 → pass 1
  0.768 → 2 0.808 → 3 0.818 → 4 0.827.

## Animator workflow: base pose + additive layers + measured timing (preferred)

This is what worked on the boss idle (Idle_Breath): key like an animator, then check with numbers.
1. **Base pose** (`keys`): key the master pose (P0) in all views, using the ref+outline / solid-model panels from `look`.
2. **Additive layers** (`"layers"` in keys.json, edited with `tools/keyedit.py W layer <name> <bone> rot|loc f=x,y,z ...`):
   - each bone/channel has its own key frames, so offsets, overlap and lead/follow are just shifted keys;
   - `rot` is degrees about the character axes in the bone's rest frame (FK); `loc` is metres;
   - interpolation is Catmull-Rom, and `"cyclic": true` makes loops seamless.
3. **Foot lock**: `"foot_lock": [["Hip_L","Knee_L","Ankle_L"], ...]` runs two-bone IK every frame, so the feet stay where they are at frame 1 and the knees absorb root motion.
4. **Measure motion, don't eyeball centimetres**: `legacy/blender_tools/motion_compare2.py W --regions regions.json`
   tracks each body region in the reference with optical flow and the same region on the model
   with exact mesh vertices. It reports the peak (cm and frame) and the RMS for up/down and side
   motion, and plots `look/motion_compare.png`. Do not measure the model with flow on its renders:
   flat Workbench shading makes that unreliable.
5. Use `tools/keyedit.py` for all key edits; it keeps keys.json compact and readable.
6. **Held props: place the prop, then IK the hand to it, never the reverse.**
   - `"props": [{"bone":"Weapon","parent":"Chest_M","at":-0.3,"pos":[x,y,z],"aim":[...]}]` makes the prop a
     child of the parent bone (it rides the breathing). `pos` is the world point where the prop's bone
     fraction `at` sits.
   - `"arm_ik": [{"chain":["Shoulder_L","Elbow_L","Wrist_L"],"follow":"Weapon","target":[...],"pole":[...]}]`
     solves two-bone IK to a grip point that rides on the prop. The hand keeps its keyed orientation
     relative to the prop. Key the hand's `aim`/`twist` palm-down onto the shaft and curl the fingers with `rot`.
   - Get world points by triangulating reference pixels from two orthographic views:
     `tools/tri.py W front=u,v left=u,v`. `tools/tri.py W --joints A,B` shows where joints currently project.
     Sanity-check a point against bone lengths: a "joint" farther away than the bone length is a misread.
   - `tools/clip_check.py W --frames 1,16` counts body vertices inside the prop. A prop must REST ON the body,
     not pass through it: keep its axis at least about its radius plus the muscle thickness away from the shoulder.
     Choose the elbow pole so the arm stays out of the prop.
   - Always inspect props in the 3D viewer from a high oblique angle. Front and side outlines hide
     penetrations and hands buried inside the prop.
7. **Loops**: the last key equals the first, and all motion must arrive at the seam with matching speed
   (check per-bone velocity across frame N → 2). `"loop": true` (the default) makes the viewer skip the
   duplicated last frame.

## keys.json

```jsonc
{
 "fps": 29.97, "frame_count": 221, "interpolation": "BEZIER",
 "keys": {
  "1":   {"root": {"loc": [0, 0, 0]},
          "bones": {"Shoulder_L": {"aim": [-0.35, 0, -0.94]},
                    "Elbow_L":    {"aim": [-0.1, 0.25, -0.97]}}},
  "150": {"bones": {"Spine1_M": {"rot": [0, 0, 35]},
                    "Chest_M":  {"rot": [0, 0, 35]},
                    "Shoulder_R": {"aim": [0, 0.3, -0.95], "twist": 20}}}
 }
}
```

**Character space** (used for every number): **x = the character's right,
y = forward, z = up**, in metres and degrees. This is a right-handed frame
fixed to the character's rest orientation.

- `aim: [x,y,z]` sets the absolute direction the bone points, toward the next
  joint (shoulder→elbow, hip→knee…), in character space. It is independent of
  the parents, so this is the easiest control to read off the views:
  - The **front** view shows x (image left = character's right) and z.
  - The **left/right** views show y (forward) and z. In the left view the
    character faces image left; in the right view it faces image right.
  - The **back** view mirrors the front view.

  Combine the views into one vector; it does not need to be normalised.
  `twist` (degrees) rolls the bone about its aim, right-hand rule.
- `rot: [x,y,z]` is an FK rotation in degrees on top of the parent, Euler
  XYZ about the character axes. `[0,0,0]` is the rest pose relative to the
  parent. Use it for the root, spine, neck and head:
  - `+z` turns toward the character's left.
  - `+x` leans an upright bone back.
  - `+y` leans an upright bone to the character's right.

  Use `aim` or `rot` on a bone, not both. Spread a torso twist over the spine
  bones; for example, a 70° turn is `rot z` +35 on each of two spine bones.
- `root.loc: [x,y,z]` moves the root bone (whole body) in metres. Use it for
  steps, crouches and jumps; z is up.
- `loc: [x,y,z]` (any bone) adds a translation offset in metres in character space.
- **Held props** such as a weapon on a separate root bone use
  `"Weapon": {"aim": [...], "twist": 0, "grip": {"bone": "Wrist_L", "at": 0.75, "offset": [0,0,0]}}`.
  The prop is aimed head→tail, and the point `at` along it (0 = bone head,
  1 = tail) is pinned to the grip bone **on every frame**, so it follows the
  hand between keys. Check which end of the prop is the bone head: if the prop
  points the opposite way in the overlay, negate `aim` and use `at` → 1 − at.
- **Carry-forward:** a bone missing from a key keeps its value from the
  previous key. Give a bone `{"rot": [0,0,0]}` to return it to rest.
- Bones never named in any key stay in rest pose. That covers fingers, props
  and twist bones.

## Reading the overlay (`look_<frame>.png`)

Each view has two panels: the reference on the left, and the reference with
the model overlaid in translucent orange on the right. On the model, the
character's left limbs are cyan and its right limbs magenta. The red lines
are the calibrated head-top and ground; the grey lines mark each tenth of the
height and the body centre.

| Symptom | Fix |
|---|---|
| Limb correct in front view, wrong in side view | Change only the y part of its `aim` |
| Whole body mis-sized or shifted, even in rest pose | Re-run `calib` |
| Feet slide or sink between keys | Key `root.loc` z; add breakdown keys |
| Elbow or knee bends the wrong way after an `aim` | Add `twist` (±90/180) to the upper bone, or aim the lower bone explicitly |
| Snapping or flipping between two keys | Two aims are nearly opposite: add a breakdown key halfway |
| Idle and loop clips | Make the last key equal to the first, so the loop closes |
| Subtle motion (idle, breathing) is hard to see | Compare frames numerically (the mean pixel difference against frame 1) to find the extremes, then key those |
| Torso twists the wrong way | The sign of `rot` z (+ = toward the character's left) |

The references are AI-generated or drawn, so proportions can differ from the
model. Match the **directions** of the limbs and the torso, not the exact
pixel outline.

## Limits

- Only the four standard views are supported, and the cameras are
  orthographic: perspective in the reference shows up as small size errors,
  so ignore those.
- No automatic tracking: quality and time scale with the number of keys. A
  typical 7-second clip needs about 10–20 keys.
- Fingers and facial expression are not keyed unless their bones are added
  to a key by name with `rot`.
