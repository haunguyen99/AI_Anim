---
name: vfx-code
description: "Làm VFX hoàn toàn bằng code (Python/numpy → flipbook + prefab Unity, kèm công thức shader realtime), tổng hợp kỹ thuật từ ~50 thư viện VFX mã nguồn mở trên GitHub: pixelfx, minerva pixel-effect-generator, NovaShader, GDQuest, three.quarks, Effekseer, Godot, stable-fluids, WebGL-Fluid-Simulation, VFXToolbox, officina-vfx-tool... Gồm noise có chu kỳ (tile / loop liền), SDF 2D, toạ độ cực, toon band, dissolve / erosion, tia sét, hệ hạt (curl, vortex, sub-emitter, stretched billboard), mô phỏng khói chất lỏng, metaball nổ, vệt chém. Skill độc lập, tách khỏi vfx-maker; chỉ dùng chung Review Lab để review. Chạy khi người dùng gọi /vfx-code."
disable-model-invocation: true
metadata:
  version: "1.2.0"
---

# vfx-code — VFX bằng code

Trao đổi bằng tiếng Việt; code và tên asset bằng tiếng Anh. Thư mục skill: `D:/Game_prj/VFX_LIb/.claude/skills/vfx-code/`.

**Skill độc lập** (art lead, 2026-11-03): không dùng công cụ, asset hay quy trình của `vfx-maker`. Điểm chung duy nhất là **Review Lab** để art lead review (mục 4).

```
Brief → KHÔNG GIAN (thiếu → HỎI) → chọn kỹ thuật (references/techniques.md) → viết effect .py
     → render --effect --check → xem preview + GIF → sửa chỗ tệ nhất (≥ 3 vòng)
     → Review Lab → (art lead duyệt) → prefab Unity (assets/VfxCodeBuild.cs)
```

**Người dùng là art lead.** Yêu cầu hình khối của họ thắng mọi kỹ thuật học từ thư viện.

## 0. Luật của art lead (áp dụng cho mọi VFX của dự án)

1. **Không gian trước** (2026-11-02). `META["space"]` gồm `context` (air / ground / dir), `plane` (billboard / ground / stretch), `camera` (mặc định `3/4 40`), `width_m` (so với người 2 m), `anchor`, `background`. Thiếu thì `render.py` dừng (mã 2) và in câu cần hỏi → **hỏi bằng AskUserQuestion**, ≤ 4 câu/lượt, tối đa 2 lượt; mục người dùng đã nói thì không hỏi lại; gợi ý của Claude ghi là *đề xuất*. Hỏi chung lượt: thời gian (một lần / loop, thời lượng), Art Style, màu chủ đạo.
2. **Không dùng Horizontal / Vertical Billboard.** Đứng = Billboard hoặc Stretched Billboard (texture ngang, hướng bay = mép TRÁI); nằm đất = Billboard + Render Alignment Local, xoay X 90° → vẽ hình TRÒN, không ép dẹt.
3. **Khói toon**: thân + thuỳ bám sát, lớn trong nhỏ ngoài, **không cắt đáy**; không tô từng thuỳ như quả cầu nhựa. Mô phỏng chất lỏng / metaball dùng cho cột khói, hơi, bụi cuộn, nổ.
4. **Vệt chém** = mesh + UV cuộn texture; `slash_arc` chỉ vẽ texture vệt, giữ bố cục UV gốc.
5. Flipbook: Frame over Time **tuyến tính** (tangent phẳng làm flipbook khựng ở đầu). Loop 8 frame 4×2, một lần 16 frame 4×4. Sheet ≤ 1024 px.
6. Thời gian nằm ở particle (curve, Custom1.x); shader chỉ giữ thông số hình.
7. **Texture có sẵn lấy từ `Assets/Library/`** (2026-11-04). Khi effect cần một ảnh không vẽ bằng code, lấy từ đây:
   - ví dụ mask, noise, hình vệt chém cho mesh (`Assets/Library/Slash/`), khói, glow;
   - cây `Assets/Library/<nhóm>/<vai trò>/`, tên `<nhóm>_<vai trò>_NNN`; chọn theo `Docs/VFX/_Library/LIBRARY.md` (bảng thành phần → thư mục), nguồn ở `library_index.csv`;
   - xem ảnh trước khi chọn; không đổi import setting của file trong Library (dùng chung), cần thì copy ảnh sang `Assets/VFX/<Effect>/Textures/`.

   Texture vẽ bằng code (flipbook của skill này) vẫn làm như cũ.

## 1. Thư viện (`lib/`)

| Module | Nội dung | Học từ |
|---|---|---|
| `core.py` | `Canvas` (thân alpha-over + sáng cộng, mép 1 px), hình `disc/streak/arc/star/poly/shade`, `glow*`, `ease`, `Rng`, ramp 7 bậc (`ramp_from_slots`, `at`), `Particles` 6 loại, xuất sheet, `check` | pixelfx |
| `fxlib.py` | noise **có chu kỳ** `perlin2/3`, `fbm`, `ridged`, `voronoi`, `curl2`, `warp`; SDF `sd_*` + `op_smin…` + `rep_polar`; `polar`; toon `ramp_hard/posterize/bands/outline`; `dissolve`, `erosion`, `wipe`, `Equalizer`; `fire_mask`, `fireball`, `bolt`, `doom_fire`, `palette_cos`; `Curve/Gradient/MinMax`; `box_blur` | IQ, FastNoiseLite, keijiro, NovaShader, GDQuest, arc-synapse, doom-fire |
| `stylize.py` | `field_bands`, `carve`, `puff_cluster`, `id_edges`, `drag_travel`, `env_punch`, `slash_arc`, `dissolve_mask`, `keep_components` | minerva pixel-effect-generator, RetroImpacts |
| `particles.py` | `System` SoA: burst / sub-emitter / trail; behavior `drag, gravity, radial, vortex, attractor, curl, limit_speed, wander`; vẽ `disc / streak / trail / glow`; `loop_phase_ages` | three.quarks, Godot, Effekseer, LÖVE, pixi, Proton, Pixel FX Forge |
| `fluid.py` | `Fluid` (stable fluids: advect, vorticity, Jacobi, nổi nhiệt), `loop_crossfade`, `loop_sync`, `motion_vectors` | GregTJ, PavelDoGreat, VFXToolbox |
| `render.py` | render → sheet + json + preview + GIF + `--check`; `--effect` xuất đúng chỗ Review Lab đọc | |

Danh mục thư viện GitHub + giấy phép: [references/sources.md](references/sources.md). **LYGIA, hg_sdf, Shadertoy** chỉ tham khảo toán, không chép code.

## 2. Viết effect

Effect của dự án để ở `<project>/Docs/VFX/<Effect>/code/<tên>.py`. Bắt đầu từ mẫu gần nhất trong `examples/` (ảnh: `examples/previews/`):

| Mẫu | Kỹ thuật | Kiểu |
|---|---|---|
| `shockwave_ground.py` | toạ độ cực + noise có chu kỳ + `Equalizer` + dissolve, toàn bộ là một "fragment shader" `cv.shade` | ground, một lần 0.5 s, add |
| `spark_burst.py` | `particles.System`: burst đều, drag + trọng lực, streak, sub-emitter tàn lửa theo curl | air, một lần 0.55 s, add |
| `lightning_arc.py` | `bolt` + giữ hình 2 frame (`stepped=True`) | dir / stretch, loop 8 frame, add |
| `fluid_plume.py` | `Fluid` → làm mờ → ngưỡng → 2 tông theo gradient mật độ | ground, một lần 1.4 s, alpha |

```python
import core as cf, fxlib as fx, numpy as np
META = dict(name="CFX_Ten", size=(128, 128), origin=(64, 64), duration=0.5, loop=False, fps=30, blend="add",
            space=dict(context="air", plane="billboard", camera="3/4 40", width_m=1.5,
                       anchor="world point", background="dark"),
            options=dict(seed=1))
def draw(cv, t, o):                         # hàm thuần của t (loop liền); hoặc create(o) → St.update/draw cho mô phỏng
    def fn(X, Y):                           # "fragment shader" trên lưới pixel
        a = fx.cov(fx.sd_ring(X, Y, 30 * cf.ease.out_expo(t / 0.5), 6))
        return np.ones(X.shape + (3,)), a, None   # (rgb thân, alpha, rgb sáng cộng hoặc None)
    cv.shade(-64, -64, 64, 64, fn)
```

- Toạ độ: x phải, **y xuống**, (0, 0) = `origin` (điểm trúng / chân chạm đất). Effect có hướng thì vẽ hướng sang phải.
- `blend`: `add` (một sheet Additive) hoặc `alpha` (Body Alpha Blended + Light Additive).
- `stepped=True`: effect đổi hình theo nhịp (sét, chớp) → `--check` bỏ phép đo nối loop.
- Chuẩn chất lượng: [references/techniques.md](references/techniques.md) §6 (nhịp hero → overshoot → toả → giữ → tắt; fast attack, slow release; một tâm điểm; đòn một lần kết thúc trống).

## 3. Render và kiểm tra

```bash
python -I "D:/Game_prj/VFX_LIb/.claude/skills/vfx-code/lib/render.py" <effect.py> --project "D:/Game_prj/VFX_LIb" --effect <Effect> --gif --check [--frames 8 --cols 4] [--res 2] [--review]
```

`--effect` ghi:
- `Assets/VFX/<Effect>/Textures/`: `T_<name>_4x4.png` (hoặc `_Body_` + `_Light_`) + `<name>.json` (duration, lưới, pivot, `space`, sheets);
- `Docs/VFX/<Effect>/`: `Preview_sheet.png` (timeline), `BuildReport.txt` (thời điểm frame, không gian, kết quả check), `<name>_preview.png`, `<name>.gif`.

Nháp thử nhiều hướng thì dùng `--out <thư mục tạm>` thay cho `--effect` (không đụng `Assets/`).
`--check` phải sạch: tất định, không tràn mép, đòn một lần tắt hẳn, loop không giật.

**Vòng sửa**: xem preview + GIF (Read), sửa **chỗ tệ nhất**, tối thiểu 3 vòng. Hướng còn mở thì làm 3–5 nháp khác hẳn nhau.

| Thấy | Nguyên nhân | Sửa |
|---|---|---|
| "Tắt cái bụp" trong 1–2 frame | fbm dồn quanh 0, ngưỡng tuyến tính quét qua hết | `Equalizer` / `fbm_equalizer`, ngưỡng đi tới > 1 + soft |
| Tan thành chấm lấm tấm | tần số noise quá cao | giảm tần số (vỡ thành mảng / cung lớn), `keep_components` |
| Vòng có đường nối | noise theo góc không có chu kỳ | `fbm(u·P, …, period=(P, …))`, P nguyên |
| Mô phỏng nổ số, khói vỡ vụn | `vort` > ~2 hoặc nguồn quá mạnh | giữ mặc định `buoy 0.1, vort 0.5`, splat 0.1–0.15/bước |
| Khói có sọc bóng | pháp tuyến lấy trên mật độ chưa mờ | lấy gradient trên bản `box_blur` mạnh hơn |
| Frame đầu trống (mô phỏng) | chưa có bước nào ở t = 0 | splat sẵn trong `create` (frame hero) |
| Lờ đờ / cứng / bệt / phẳng | thiếu ease, thiếu ngẫu nhiên, thiếu sáng | `out_expo` + frame trắng; random mọi thứ; glow 0.2–0.5; sáng trên-trái |
| Hạt chạm mép ô | tốc độ / tuổi thọ / inherit quá lớn | giảm, hoặc tăng `size` |
| "Chưa tắt hẳn" | tuổi thọ + sub-emitter > duration | rút tuổi thọ, hoặc kéo dài duration |
| Loop giật ở frame cuối | `round(t·30)` đẩy frame cuối sang chu kỳ sau | `floor(t·30 + 1e-6)` |

## 4. Review Lab (dùng chung)

Thêm `--review` vào lệnh render (dựng lại cả trang), hoặc chạy riêng:
```bash
python -I "D:/Game_prj/VFX_LIb/.claude/skills/vfx-maker/review-lab/build_review.py" --project "D:/Game_prj/VFX_LIb"
```
Không dùng `--effect` của build_review khi ghi vào `index.html` chung: trang sẽ chỉ còn 1 effect.
→ `Docs/VFX/_Review/index.html`: timeline từ `Preview_sheet.png`, trình phát flipbook từ sheet trong `Textures/`, GIF, A/B, ghim góp ý. Art lead bấm "Xuất phản hồi" rồi dán vào chat: đọc như danh sách sửa (effect, mốc, toạ độ %). Sửa → render lại với `--review`.

## 5. Đưa vào Unity (sau khi art lead duyệt)

1. Lần đầu trong project (hoặc khi bản trong skill mới hơn): chép `assets/VfxCodeBuild.cs` + `assets/VfxCodeAutoBuild.cs` → `Assets/VFX/_VfxCode/Editor/` và `assets/VfxCodeReplay.cs` → `Assets/VFX/_VfxCode/Runtime/` (ngoài `Editor/`). Script mới chỉ biên dịch khi cửa sổ Unity được focus → nhờ art lead click vào Unity **một lần**.
2. **Unity đang mở → TỰ BUILD** (`VfxCodeAutoBuild`, art lead 2026-11-03: "không phải thao tác build mỗi lần"): `render.py --effect` ghi json vào `Assets/VFX/<Effect>/Textures/` → Unity tự nhập và dựng prefab + scene sau ~5–10 s, **kể cả khi không focus**. Không cần nhờ bấm menu. Kiểm tra: chờ file `Assets/VFX/<Effect>/Scenes/<Effect>_Demo.unity` rồi đọc dòng `[vfx-code] Auto Build xong` trong `%LOCALAPPDATA%/Unity/Editor/Editor.log`. Không tự build khi đang Play / đang compile (chờ xong mới chạy). Bật / tắt: menu **VFX → vfx-code → Auto Build**. Dựng tay: **Build From Json...**. Unity không mở → batchmode:
   ```
   "C:/Program Files/Unity/Hub/Editor/<version>/Editor/Unity.exe" -batchmode -projectPath "<project>" -executeMethod VfxCode.VfxCodeBuild.BuildBatch -vfxjson Assets/VFX/<Effect>/Textures/<name>.json -quit -logFile "<project>/Logs/vfxcode_<Effect>.log"
   ```
3. Builder: import texture (không mip, Clamp), material `Mobile/Particles/Additive` hoặc `Alpha Blended`, mỗi sheet một layer, **1 particle chạy cả flipbook** (Start Lifetime = duration, Frame over Time tuyến tính), Start Size theo `space.width_m`, mặt phẳng theo `space.plane`, pivot = điểm gốc → `Assets/VFX/<Effect>/Prefabs/VFX_<Effect>.prefab`.
   Kèm **scene demo** `Assets/VFX/<Effect>/Scenes/<Effect>_Demo.unity`: effect đặt theo `space` (ground ở mặt đất, air/dir cao 1 m), camera 3/4 nhìn xuống 40°, mặt đất theo `background`, hình nhân 2 m để so tỷ lệ, `VfxCodeReplay` tự phát lại (Space = phát ngay). Scene dựng ở chế độ phụ rồi đóng, không đụng scene đang mở; cuối cùng builder hỏi có mở scene demo không. Chỉ dựng lại scene: menu **Make Demo Scene...**.
4. Shader realtime thay flipbook: [references/shaders.md](references/shaders.md). Kiểm `Docs/VFX/SHADERS.md` + `VfxShaderLib.cginc` trước; viết mới thì ghi vào sổ.
5. Hạt Shuriken dựng từ recipe (chưa có builder): [references/particles.md](references/particles.md) §3.

## 5b. Realtime: code + shader, không texture (2026-11-09)

Dùng khi art lead muốn effect **hoàn toàn bằng code và shader** (không sheet, không ảnh Library). Hình do shader tính trên quad particle, thời gian / seed đi qua Custom1. Mẫu đã duyệt: **ElectricBolt**, tia điện nối A→B. Chi tiết ở [references/electric-bolt.md](references/electric-bolt.md):
- không gian;
- cách shader dựng tia: hash gấp khúc, ghim đầu, toon, đổi hình, đứt khúc;
- bảng lớp + số;
- cách đặt tia A→B bằng Stretched Billboard;
- lỗi đã gặp.

- Shader (bản lưu trong skill; chép vào `Assets/VFX/_Shared/Shaders/` nếu project chưa có, rồi ghi vào `Docs/VFX/SHADERS.md`):
  - `assets/shaders/SH_VFX_ElectricBolt.shader` (`VFX/FX/Electric Bolt`): tia / cung điện gấp khúc, 0 sample;
  - `assets/shaders/SH_VFX_GlowStar.shader` (`VFX/FX/Glow Star`): chớp, quầng, sao gai toon, 0 sample.
- Builder mẫu: `assets/ElectricBoltBuild.example.cs` → `Assets/VFX/<Effect>/Editor/<Effect>Build.cs`. Dùng `VfxBuildKit` / `VfxLightningKit` của project (`Assets/VFX/_Kit/`) để tạo hạt, lưu prefab và chụp preview; dùng lại `VFX/FX/Spark` cho tia lửa.
- Quy trình giữ như skill: không gian trước (thiếu thì hỏi), research nhanh, kế hoạch duyệt một lần. Sau đó:
  - Unity đang mở thì nhờ art lead bấm **VFX → <Effect> → Build**;
  - đọc `BuildReport.txt` + `Preview_sheet.png`, sửa;
  - dựng Review Lab;
  - được duyệt thì thêm vào `Included` + `VfxShowcaseLights`.

## 6. Bàn giao

Báo ngắn: đường dẫn effect `.py`, sheet, Review Lab, prefab (nếu đã dựng); kết quả `--check`; phần chưa kiểm chứng (chưa xem trong Unity, chưa thử trên máy mobile).

## 7. Tài liệu

- [references/techniques.md](references/techniques.md): chọn kỹ thuật theo loại effect, noise, SDF, toon, tan, thời gian, loop.
- [references/particles.md](references/particles.md): hệ hạt, nhịp, đưa sang Unity, đóng gói flipbook.
- [references/shaders.md](references/shaders.md): công thức shader realtime mobile.
- [references/sources.md](references/sources.md): danh mục ~50 repo đã khảo sát, giấy phép, học được gì.
- [references/electric-bolt.md](references/electric-bolt.md): tia điện A→B realtime bằng shader, không texture (mẫu đã duyệt 2026-11-09).
