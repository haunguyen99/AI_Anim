# ThunderImpact QA — 2026-11-04

Built and rendered using Unity 2022.3.62f3, Built-in, in isolated QAProject because main project is open. Generated Materials/Prefabs/Scenes copied to main project, retaining file metadata and existing dependency GUIDs. Shared sources and texture import settings unchanged.

- Four native systems, root is Flash; max particle capacity 30; hierarchy scaling, unit transforms.
- Built-in validation passes. ShaderUtil.GetShaderMessages after rendering returns no messages. No deliberately broken shader negative-control test performed.
- Native simulation at 1.2 s confirms zero remaining particles. Preview sampled at all three strikes and intervening gaps; reviewed sheet and peak image.
- Preview.gif assembled from 36 Unity-rendered frames at 30 fps; Review.html includes timeline and images. Desktop in-game playback and mobile profiling remain unverified.
- Existing LightningStrike and Showcase source unchanged. Rebuild via VFX > ThunderImpact > Build if needed. Showcase inclusion awaits visual review.
- QAProject is a reproducible isolated scratch project, excluded from Git by local .gitignore.
