# ThunderChainImpact — independent effect and three-target demo

Requested 2026-11-04: create a different thunder impact and a scene demonstrating lightning spreading to 2–3 targets, without using any skill. Direct implementation, no skill scripts or workflows used.

Retain prior yellow-white palette, 60-degree camera and three impact beats as implementation defaults. New composition: initial ground strike, then three sequential target connections. Each receiver flashes and plays a native hit prefab. Chain connections are controlled outside the effect prefabs by a scene-only demo script.

Visual selection: inspected all 33 electric textures as a contact sheet, then full-size 025/020/024. Selected 025 for vertical irregular bolt, strong primary bends, bright core and fine branches; 020 was not selected. Existing 008 atlas supplies ground arcs; glow_004 and wave_009 supply soft flash/ring. Source imports remain unchanged. New materials use Unity Mobile/Particles/Additive; scene surfaces use Standard. No custom shader, no new raster texture.

Two native particle prefabs (primary and receiver), standalone editor builder, demo scene script and scene. No changes to previous ThunderImpact or LightningStrike. Native impact prefabs have no runtime scripts; the demo supports 2 or 3 targets by array configuration, default 3. Target damage is visual only.

## Validation and use

Unity 2022.3.62f3 Built-in isolated QA project compiled the scripts and rendered 54 frames at 30 fps. Shader errors: zero. At 1.8 s, all particles and connecting lines are inactive. Reviewed rendered frames showing sequential targets 01/02/03; revised sparks to use the soft existing flash texture instead of untextured rectangles. Main-project script GUID synchronized before final build and verified in delivered scene. Generated prefabs/materials/scene copied back preserving their metadata. The open main Unity session was not closed or controlled.

Open `Assets/VFX/ThunderChainImpact/Scenes/ThunderChainImpact_Demo.unity` and press Play. Automatic loop 2.8 s, Space replays. Scene-only controller follows target transforms. To configure two targets, use equal two-element `targets` and `hits` arrays and remove the unused demo target/hit instance. Prefabs contain no runtime controller. Build menu: VFX > ThunderChainImpact > Build Demo. `Preview.html` provides sampled timeline and playback speed; `Preview.gif` is the rendered animation. Main-project Play mode and physical mobile performance have not been verified.
