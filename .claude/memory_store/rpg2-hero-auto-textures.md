---
name: rpg2-hero-auto-textures
description: "RPG2 Hero in Frolvy: textures go on the meshes automatically whenever a scene is opened - plugin hero_textures (needs one Frolvy restart to load); by hand: exec the plugin file + apply(api, force=True)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: d1ba2fc2-259c-450d-a79c-ac6f7bc1b378
  modified: 2026-11-05T08:01:54.986Z
---

User 2026-11-05: "tự động add texture mỗi khi mở file" (after playblasts came out grey because a re-opened Hero_Blade scene had the meshes back on the grey default material while `texture_state` still said 'loaded').

**What exists:** plugin `hero_textures` (source `tools/frolvy_plugins/hero_textures/`, installed in `C:\Users\huongbtx\Documents\Frolvy\plugins\hero_textures\0.1.0\`). It polls every 3 s (`api.call_later`); when the scene signature changes (object names + texture ids; opening a file reloads textures) and the scene has the Hero meshes (`char_main_t2_body/hood/scarf_1/scarf_2`, `Vk_t1_Dualblades_L/R`) it creates / loads / assigns `M_Char_Main_T2` + `M_Colorpalette` and puts the selection back. The textures are the original .tga flipped top-to-bottom (Frolvy shows .tga upside down), PNGs ship inside the plugin `tex/`.

**How to apply:**
- The plugin is loaded when Frolvy starts, so a Frolvy that was already open needs ONE restart; tell the user that, do not claim it is automatic before then. Plugins menu: Add Hero Textures.
- In a session, when you open or start on a Hero_Blade scene and the plugin may not be loaded yet (or before any playblast), do it yourself: `exec(open(r'C:\Users\huongbtx\Documents\Frolvy\plugins\hero_textures\0.1.0\hero_textures.py', encoding='utf-8').read()); apply(api, force=True)`. It is idempotent.
- Do not copy these textures into the game repo or the user's Hero folder unasked. Related: [[rpg2-hero-playblast-after-edit]].
