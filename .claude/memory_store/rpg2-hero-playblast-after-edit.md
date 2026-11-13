---
name: rpg2-hero-playblast-after-edit
description: "RPG2 Hero anim in Frolvy - playblast ONLY when the user asks (not after every edit); MP4 into C:\\Project\\RPG_2\\Hero\\Hero_Blade\\Blast_Test, camera1, no controls, textured"
metadata:
  node_type: memory
  type: feedback
  originSessionId: ff756c3d-5eb7-4a99-b213-1e3368552015
  modified: 2026-11-05T07:58:16.766Z
---

**WHEN (latest, user 2026-11-05: "playblast khi có lệnh", earlier "chỉ play blast khi có lệnh ở nhánh này"): playblast ONLY when the user tells you to.** This replaces the first rule below ("after every edit"), in every session/fork. After an edit, report and wait; do not playblast on your own. Everything below (where the files go, camera, no controls, textures) still applies WHEN a playblast is asked.

First rule, now superseded, user 2026-11-05: "sau mỗi lần sửa khi làm anim, sửa xong sẽ play blast và lưu vào" `C:\Project\RPG_2\Hero\Hero_Blade\Blast_Test`.

**Why:** the user reviews each change from the video, without opening Frolvy.
**How to apply:** after each finished edit (one fix round, not every execute_code call), in Frolvy via execute_code:
`api.set_playblast_video(True, 18, False, '', r'C:\Project\RPG_2\Hero\Hero_Blade\Blast_Test\<Clip>_<version>_<yyyymmdd-HHMM>.mp4')`, then `api.playblast(start, end, r'C:\Project\RPG_2\Hero\Hero_Blade\Blast_Test')` over the clip's full range (playback range). Poll `api.playblasting()` until False, check `api.playblast_status()`. Tell the user the file name in the reply. Never overwrite an older blast; each one gets a new name. Keeping the PNG frames is off. Do not save the .fv just because of the playblast. Related: [[rpg2-hero-new-anims]].

**Camera (user 2026-11-05: "khi playblast tự động góc camera1"):** every playblast of these anims is from `camera1`. First `api.look_through('camera1')`, then `set_playblast_video` + `playblast`; afterwards `api.look_through('')` to put the viewport back to Persp.
**No controls, with textures (user 2026-11-05: "camera 1 tôi ẩn control rồi mà blast lại có control", then "bật texture"):** the playblast draws what the viewport draws, but the viewport's hidden-controls state is NOT reliable from one call to the next, and the mesh materials can be lost (user undo / reopen): twice the meshes were back on grey lambert1 while `texture_state` still said 'loaded'. Safe recipe, in order, and look at one frame of the MP4 afterwards (`C:\Program Files\Frolvy\ffmpeg\ffmpeg.exe -i x.mp4 -vf select=eq(n\,15) -frames:v 1 f.png`):
1. (call A) re-assign both materials every time: `api.assign_material('M_Char_Main_T2', [body, hood, scarf_1, scarf_2])`, `api.assign_material('M_Colorpalette', [Vk_t1_Dualblades_L, Vk_t1_Dualblades_R])` (namespace `Hero_Blade_Rig:`; textures = `Documents\AnimationDCC\textest\*_flipV.png` because the .tga load upside down), `api.look_through('camera1')`; select the 6 meshes, `api.isolate_selected(v)` for v in 0..3, `api.select([])`.
2. `get_viewport_screenshot` (small) so the viewport redraws, then (call B) `set_playblast_video` + `playblast`; poll `playblasting()` in call C.
3. `api.isolate_off(v)` for v in 0..3, `api.look_through('')`.
A teal cylinder (`pCylinder1`) and the floor `pPlane1` are scene objects the user added; they stay in the video, do not hide them. Start the playblast in one execute_code and poll `playblasting()` in the NEXT call (it only runs once the call returns).
