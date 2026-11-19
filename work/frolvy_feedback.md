# Frolvy feedback (gửi qua Help → Send Feedback… hoặc hello@frolvy.com, tiếng Anh, mỗi lỗi 3 dòng)

Nguồn: phiên "New Pet" 18/11/2026, Linux, Frolvy 0.9.x, rig game 30–46 joint, Python API qua MCP.
Trạng thái: `chưa gửi` → hỏi người dùng trước mỗi lần gửi, gửi xong ghi ngày.

| # | Bug | How to see it | Request | Trạng thái |
|---|---|---|---|---|
| 1 | `api.save_scene(path)` returns False and writes nothing when `path` already exists (no error text). | Save a scene to `/tmp/a.fv`, change it, call `save_scene("/tmp/a.fv")` from another open scene → False, file unchanged. | Overwrite, or return a clear error / add an `overwrite` flag. | chưa gửi |
| 2 | `api.open_scene(path)` returns False when the current scene has unsaved changes; an "Unsaved changes" dialog appears that only a manual click closes. | Edit any scene, call `open_scene` on another file from the API. | Let the API choose (discard/save) or raise an error instead of a blocking dialog. | chưa gửi |
| 3 | `go_to_bind_pose` reports 4 joints "cannot return" when the scene has animation keys, even though the bind pose is valid. | Rig with IK legs + keyed controls → `go_to_bind_pose` → 4 joints stay posed. | Return the joints to bind regardless of keys (or say which key/constraint blocks it). | chưa gửi |
| 4 | PNG and TGA textures are shown flipped vertically in the viewport; UVs and the exported FBX are correct. | Assign a PNG to a mesh → texture is upside down in Frolvy, right in Unity. | Flip V on load (or add a "flip V" option on the texture node). | chưa gửi |
| 5 | When the MCP port of one Frolvy window dies, `Frolvy-mcp` silently switches to another open Frolvy window; later commands run on the wrong scene. | Run 2+ Frolvy windows on different ports, restart one → save/step/select commands hit the other window, no error. | Fail with "port not available" instead of auto-switching (or report the new instance in the reply). | chưa gửi |
| 6 | FBX export bakes the animation into the open scene, so the un-baked original is gone from the window. | Export FBX from a rigged scene with IK/constraints → controls are no longer driving after export. | Bake on a copy, or keep the scene unchanged. | chưa gửi |
| 7 | After deleting all keys of a channel the channel stays "dead": `rotate` has no effect and the next key is written as 0. | Delete every key on `Head rx`, then rotate Head or set a key → no change / value 0. | Reset the channel to a plain attribute when its last key is deleted. | chưa gửi |
