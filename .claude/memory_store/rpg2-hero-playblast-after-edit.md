---
name: rpg2-hero-playblast-after-edit
description: "RPG2 Hero anim in Frolvy - after every anim edit, playblast an MP4 into C:\\Project\\RPG_2\\Hero\\Hero_Blade\\Blast_Test"
metadata:
  node_type: memory
  type: feedback
  originSessionId: ff756c3d-5eb7-4a99-b213-1e3368552015
  modified: 2026-11-05T03:45:38.710Z
---

Rule for every session/fork working on RPG2 Hero anims (Hero_Blade, Frolvy), user 2026-11-05: "sau mỗi lần sửa khi làm anim, sửa xong sẽ play blast và lưu vào" `C:\Project\RPG_2\Hero\Hero_Blade\Blast_Test`.

**Why:** the user reviews each change from the video, without opening Frolvy.
**How to apply:** after each finished edit (one fix round, not every execute_code call), in Frolvy via execute_code:
`api.set_playblast_video(True, 18, False, '', r'C:\Project\RPG_2\Hero\Hero_Blade\Blast_Test\<Clip>_<version>_<yyyymmdd-HHMM>.mp4')`, then `api.playblast(start, end, r'C:\Project\RPG_2\Hero\Hero_Blade\Blast_Test')` over the clip's full range (playback range). Poll `api.playblasting()` until False, check `api.playblast_status()`. Tell the user the file name in the reply. Never overwrite an older blast; each one gets a new name. Keeping the PNG frames is off. Do not save the .fv just because of the playblast. Related: [[rpg2-hero-new-anims]].
