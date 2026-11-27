# Thư viện VFX bằng code trên GitHub — danh mục đã khảo sát (2026-11-03)

Khảo sát bằng 4 agent đọc **mã nguồn thật** (curl raw.githubusercontent / GitHub API). Sao (★) là con số lúc khảo sát; một số repo không lấy được do giới hạn API.
Công thức trong skill được **viết lại bằng code của mình**, không chép nguyên văn.

## ⚠ Giấy phép — đọc trước khi dùng

| Được port thẳng (MIT / Apache / Unlicense / zlib) | Chỉ tham khảo toán, **không chép code** vào game thương mại |
|---|---|
| pixelfx, minerva pixel-effect-generator, NovaShader, GDQuest godot-visual-effects (code), three.quarks, Effekseer, Godot, Proton, pixi-particle-emitter, LÖVE, psrdnoise, webgl-noise, keijiro NoiseShader, FastNoiseLite, Material Maker, stable-fluids (GregTJ), WebGL-Fluid-Simulation, taichi, doom-fire, deepnight libs, Pixel FX Forge (Apache), bevy_hanabi, officina-vfx-tool | **LYGIA** (Prosperity 3.0, phi thương mại), **hg_sdf** (CC BY-NC), shader port từ **Shadertoy** (mặc định CC BY-NC-SA), art của GDQuest (CC BY-NC-SA), MotionFrame (GPL-3, *texture xuất ra* thì không bị ràng buộc), RetroImpacts (không ghi license), Unity VFXToolbox / VFX Graph Samples (Unity Companion License — chỉ dùng trong Unity) |

## 1. Sinh texture / flipbook bằng code (2D)

| Repo | Lang | Học được gì | Ở đâu trong skill |
|---|---|---|---|
| **patch-gg/pixelfx** (MIT, 3.7k★) | JS | SDF + 2 lớp (thân bậc cứng + sáng cộng), ramp theo nhiệt, hạt theo loại có drag, nhịp hero / overshoot 30 fps | `lib/core.py` |
| **minerva-studio/pixel-effect-generator** (MIT) | TS | **một trường quyết định cả viền và bậc màu**; nhám chỉ ăn vào trong; cụm metaball nổ có nhiệt lồng trong viền; nét toon tự động (viền + giữa khối); bộ dissolve 1 tham số; vệt chém cực (đầu/đuôi/mũi thon); vòng xung kích dùng chung luật hãm; dọn vụn giữ khối gốc; xuất Unity zip + golden test | `stylize.py` |
| ssencho/RetroImpacts (không license) | Python/PIL | 16 mô hình hit-effect fighting game; đường năng lượng lên tuyến tính → tắt mũ; đổi góc tia mỗi 2 frame; **analyzer**: đo pixel, tâm, bán kính, palette từng frame của sheet tham chiếu | `stylize.env_punch`; ý tưởng `diagnose` |
| GameDev-Toolkit/pixel-ability-fx-generator "Pixel FX Forge" (Apache-2.0) | JS | **loop hạt liền** bằng sinh đều theo pha: tuổi = ((φ − birth) mod 1)·life; nhịp double-pulse / stagger / slow-build / echo | `particles.loop_phase_ages` |
| deepnight/deepnightLibs `HParticle` (MIT) | Haxe | ma sát riêng x/y, scale có vận tốc + ma sát, xoay theo hướng bay, nảy, squash pop, alpha nhấp nháy | references/particles.md |
| anhminhzui-dev/arc-synapse (MIT) | JS | sét chia đôi đoạn + nhánh (cường độ ×0.5–0.8), nhịp anime "on 2s/3s" | `fxlib.bolt`, mẫu `lightning_arc.py` |
| RodZill4/material-maker (MIT) | GDScript/GLSL | 399 node: SDF boolean, `make_tileable` (trộn bản lệch 0.5/0.25), `tones_step`, `palettize`, splatter | `fxlib.op_*`, `posterize` |
| Auburn/FastNoiseLite (MIT) | nhiều | OpenSimplex2, cellular, domain warp tiến dần (mỗi tầng warp lên toạ độ đã warp), ridged / ping-pong | `fxlib.fbm/ridged/voronoi/warp` |
| njbrown/texturelab, CXUtk/LightningGen | C++ | node texture / sét bằng geometry shader (chưa đọc kỹ) | — |

## 2. Shader VFX / SDF / noise

| Repo | Lang | Học được gì | Ở đâu |
|---|---|---|---|
| **CyberAgentGameEntertainment/NovaShader** (MIT, 1.6k★) | HLSL URP | Uber particle shader production: **alpha erosion** theo vertex alpha / custom data (remap để p = 0 nguyên, p = 1 mất hết), flowmap, ramp màu phát sáng, rim, soft particle, depth fade, flipbook blend | `fxlib.erosion`, shaders.md |
| **gdquest-demos/godot-visual-effects** (MIT code) | GDShader | nổ (sphere: fresnel × noise, lửa → khói theo ngưỡng rồi ăn mòn), blast (**kênh G quét dải qua kênh R**), shockwave rim, slash, fire burst (warp 2 sin) | `fxlib.wipe`, shaders.md |
| iquilezles.org (bài viết; demo Shadertoy phần lớn MIT) | GLSL | SDF 2D, smin (đa thức / bậc 3 / mũ), domain warp q→r→f, **palette cosine** | `fxlib.sd_* / op_smin / warp / palette_cos` |
| stegu/psrdnoise, stegu/webgl-noise, keijiro/NoiseShader (MIT) | GLSL/HLSL | noise có chu kỳ (tile liền), **psrdnoise xoay gradient theo alpha → loop khi alpha 0 → 2π**, đạo hàm giải tích | `fxlib.perlin2/3(period=…)` |
| patriciogonzalezvivo/lygia (**Prosperity**) | đa ngôn ngữ | fbm, voronoi, curl, cart2polar, stroke, starSDF — chỉ tham khảo | — |
| hg_sdf / Mercury (**CC BY-NC**) | GLSL | union tròn / bậc thang, pModPolar — chỉ tham khảo | `fxlib.rep_polar` (viết lại) |
| yumayanagisawa/Unity3D-Lightning-Shader (MIT, port Shadertoy) | CG | sét = chuỗi đoạn lệch noise, glow k/d | shaders.md |
| **Cyanilux/BakeShader** (MIT) | C# | nướng shader Unity bất kỳ ra PNG / **flipbook** (`_Slice` 0 → 1) | đường lui khi effect dễ viết HLSL hơn numpy |
| albertomelladoc/DissolveParticleShader, AdultLink/VerticalDissolve (MIT) | CG | dissolve particle: `clip(noise - (1 - vertexAlpha))`, custom data dời UV noise | shaders.md |
| haowg/GODOT-VFX-LIBRARY (MIT) | GDShader | VFX 2D action đã ship: hit, dash, dissolve trạng thái, heat distortion | — |

## 3. Hệ hạt runtime

| Repo | Lang | Học được gì | Ở đâu |
|---|---|---|---|
| **MiruSona/officina-vfx-tool** (MIT, 10/2026) | Python + C# | **gần như y hệt pipeline dự án**: AI viết recipe JSON → Python mở rộng thành `resolved.json` (C# không bao giờ tự đoán mặc định) → Unity batchmode dựng Shuriken + chụp frame → đo **bảng triệu chứng** (empty / offscreen / too_dense / too_short / lingers / off_palette / lopsided / too_bright) → patch theo **tên layer** → tối đa 4 vòng, kém hơn thì quay lại bản tốt nhất. Bẫy Unity: gradient `Fixed` lệch 1 key; startColor × colorOverLifetime nhân đôi | particles.md §Unity, `diagnose` (đề xuất) |
| **Alchemist0823/three.quarks** (MIT) | TS | behavior `initialize/update/frameUpdate` + registry; **bộ nhớ ngẫu nhiên theo hạt** (random giữa 2 curve giữ nguyên hệ số suốt đời); Bezier từng đoạn; stretched billboard giống Unity; trail miter; sub-emitter Birth/Death/Frame | `particles.System`, `fxlib.MinMax/Curve` |
| djeedai/bevy_hanabi (Apache-2.0) | Rust/WGSL | tách init / update / render modifier; mỗi modifier khai báo thuộc tính cần | kiến trúc `particles.py` |
| effekseer/Effekseer (MIT) | C++ | easing có start/end/middle ngẫu nhiên; **lực lái** (vortex, turbulence: `acc = field - prevVel` → không nổ); ribbon / ring / track | `particles.vortex` |
| godotengine/godot `particle_process_material` (MIT) | C++/GLSL | seed hash theo chỉ số hạt; **curl noise trộn hướng vận tốc** `v = mix(v, curl·|v|, influence)`; min/max × curve texture | `particles.curl` |
| defold/defold particle | C++ | curve nướng thành LUT 64 đoạn; hệ số "spread" 1 số / hạt; vortex có hướng dự phòng | particles.md |
| pixijs-userland/particle-emitter (MIT) | TS | behavior JSON `{type, config}` có thứ tự; **giá trị bậc (stepped)**; burst chia góc đều | `burst(even=True)` |
| drawcall/Proton, three-nebula (MIT) | JS | Initialize vs Behaviour; behaviour có "năng lượng" giảm theo easing; hút `(1 − d²/R²)` | `particles.attractor` |
| love2d/love ParticleSystem (zlib) | C++ | vòng lặp tối giản: gia tốc hướng tâm / tiếp tuyến, drag `v /= 1 + k·dt` | `particles.drag/radial` |
| stone-SJH/unity-particle-quarks-exporter (MIT) | C# | xuất Unity → JSON, chế độ strict / best-effort + báo cáo chuyển đổi | particles.md §Unity |
| tsparticles, keijiro/Smrvfx, Unity VFX Graph Samples | TS / C# | preset JSON lớn (web); GPU / VFX Graph (ít liên quan Shuriken) | — |

## 4. Mô phỏng (khói / lửa / chất lỏng) để nướng flipbook

| Repo | Lang | Học được gì | Ở đâu |
|---|---|---|---|
| **GregTJ/stable-fluids** (Unlicense) | numpy+scipy | ~60 dòng Stam 1999; áp suất giải trực tiếp bằng sparse factorized | `fluid.py` |
| **PavelDoGreat/WebGL-Fluid-Simulation** (MIT, 16.8k★) | JS/GLSL | thứ tự bước, splat Gauss, vorticity confinement, **warm-start áp suất p *= 0.8**, 2 độ phân giải (vận tốc 128, màu 1024), tô sáng theo gradient | `fluid.Fluid` |
| taichi-dev/taichi `stable_fluid.py` (Apache-2.0) | Python | lần ngược RK3 (giữ xoáy sắc), tiêu tán mũ | đề xuất nâng cấp |
| tum-pbs/mantaflow `simpleplume.py` | C++/Py | nguồn × noise (mép cột khói vỡ mà không tăng độ phân giải), MacCormack | đề xuất |
| Scrawk/GPU-GEMS-2D-Fluid-Simulation (MIT) | Unity | nổi theo nhiệt và mật độ `σ(T−T₀) − κ·D` | `Fluid.buoy` |
| matthias-research Ten Minute Physics 17 (MIT) | JS | lưới MAC, Gauss-Seidel over-relax 1.9 | — |
| keijiro/StableFluids (Unlicense) | Unity compute | port Unity tham chiếu | — |
| **Unity-Technologies/VFXToolbox** ImageSequencer | C# | chuỗi xử lý flipbook: **Loop** (frame đồng bộ + đường S), FixBorders, AlphaFromRGB, Premultiply, RemapColor, Retime | `fluid.loop_sync` |
| aki-null/MotionFrame (GPL-3) + UnityFlipbookMotionBlending (MIT) | Rust / HLSL | atlas **motion vector** (Farneback) + shader blend → ít frame mà vẫn mượt | `fluid.motion_vectors` (lấy thẳng từ vận tốc, không cần optical flow), shaders.md §MV |
| stylerhall/flipbook-packer (MIT) | Python | xếp kênh Atlas / Super / Stagger (192–256 frame) | particles.md |
| shady-poly/Blender-Flipbook-Maker (MIT) | bpy+OpenCV | render timeline Blender → flipbook | — |
| filipedeschamps/doom-fire-algorithm (MIT) | JS | lửa automaton: gần như miễn phí, hợp pixel art | `fxlib.doom_fire` |
| sideeffects/SideFXLabs | Houdini | quy ước texture sheet / motion vector / padding của ngành | — |

## Kết luận chung (rút từ cả 4 nhóm)

1. **Một trường → cả hình lẫn màu** (minerva, Shadertoy fire, NovaShader ramp). Không vẽ mask rồi tô riêng.
2. **Ngưỡng tăng dần trên một noise đứng yên** là cách tan / ăn mòn chung của mọi thư viện. Noise phải được **giãn phân bố** (`Equalizer`) hoặc ngưỡng phải đi hết −w..1+w (Nova remap), nếu không effect "tắt cái bụp".
3. **Lực "lái" thay vì cộng** (Godot curl, Effekseer vortex) → hạt ổn định ở fps thấp.
4. **Ngẫu nhiên một lần / hạt, nhớ suốt đời** (three.quarks memory, Godot hash) → tất định, A/B so được.
5. **Loop = thiết kế từ đầu**: noise có chu kỳ (z = t/T·P), tần số thời gian nguyên, hạt sinh đều theo pha. Crossfade chỉ là đường lui.
6. **Recipe hai tầng** (officina): người/AI viết ngắn → Python mở rộng đủ → C# chỉ ánh xạ 1-1.
