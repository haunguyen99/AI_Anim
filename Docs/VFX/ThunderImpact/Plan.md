# ThunderImpact — Plan v1 APPROVED

User approved 2026-11-04: “duyệt”. Stylized yellow-white lightning from above onto a fixed ground point. Camera top-down 60 degrees, dark gray background. Height 5 m, ground spread diameter 3 m. Beats 0 / 0.22 / 0.44 s, bolt lifetime 0.15 s, all gone around 1 s.

| ID | Layer | Carrier | Reuse shader | Reuse texture |
|---|---|---|---|---|
| L1 | Bolt, three beats, dim regions erode before bright core | Stretched Billboard | Particles/Lightning_CustomBlend | Library/Lightnings_Electrics/Lightnings_Electrics_007; imported Gradient_lightning |
| L2 | Flash, root PS, synchronized with each strike | Billboard | Mobile/Particles/Additive | Library/glow/glow_004 |
| L3 | Expanding ground shockwave | Billboard Local | Mobile/Particles/Additive | Library/wave/wave_009 |
| L4 | Ground arcs spread outward and flicker away | Billboard Local | Mobile/Particles/Additive | Library/Lightnings_Electrics/Lightnings_Electrics_008, 3x3 variants |

New: four materials, one prefab with four native Particle Systems, editor builder and demo scene. Reuse texture imports unchanged. No new shaders or meshes. Target under 32 concurrent particles; mobile performance unmeasured.

Different from LightningStrike: jagged narrow bolt instead of broad column, three close beats, compact ground-only electric spread. No changes to LightningStrike.

L1 stream packing: Position, Color, UV, Custom1XY; cutoff TEXCOORD0.z, random UV offset .w. Shader ignores particle alpha, so cutoff reaches 1.01 to extinguish it. No shader changes.
