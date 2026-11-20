---
name: vfx-maker
description: "Quy trình VFX bằng texture + particle: từ mô tả/ảnh/JSON Shape Lab → ĐỊNH HƯỚNG KHÔNG GIAN (bắt buộc, thiếu thì hỏi) → effect kiểu đòn trúng/nổ thì AUTO MIX từ thành phần chuẩn (Impact/Glow/Ring/Sparks/Dust) ra recipe rồi Unity dựng → kế hoạch (duyệt 1 lần) → asset (texture lấy từ Assets/Library trước, rồi script / Shape Lab / ChatGPT, mesh, shader nhẹ cho mobile, Built-in + URP) → prefab Unity dựng bằng build script, tự chụp preview kiểm tra → Review Lab. Chế độ B: chỉ xuất spec + prompt tiếng Anh để bàn giao. Chỉ chạy khi người dùng gọi /vfx-maker."
disable-model-invocation: true
metadata:
  version: "2.3.1"
---

# VFX_Maker

Biến mô tả effect thành **prefab Unity chạy được** với **một lần duyệt duy nhất**. Trao đổi bằng tiếng Việt; code, tên asset và prompt cho ChatGPT hay agent khác viết bằng tiếng Anh.

Prefab được **dựng từ một Editor script** (`<Effect>Build.cs`), không chỉnh tay trong Inspector. Vì vậy mỗi lần sửa chỉ cần sửa script rồi build lại. Kết quả luôn tái tạo được, và Claude tự chụp preview để kiểm tra.

```
Mô tả → ĐỊNH HƯỚNG KHÔNG GIAN (thiếu → HỎI) → (Shape mới? Shape Lab) → Kế hoạch (DUYỆT 1 lần) → Asset → Build script → Build + preview → Review Lab → Bàn giao → Sửa
                                    ├── Đòn trúng / nổ: AUTO MIX từ thành phần chuẩn → recipe → Unity (mục 9)
                                    └── Chế độ B: Spec + prompt tiếng Anh để bàn giao (không dựng)
```

Skill `/vfx-shader` (VFX chỉ bằng shader) đã bỏ ngày 2026-11-02. Bước định hướng của nó được gộp vào đây (mục 1a), bản lưu ở `Docs/VFX/_ArtDirection/_archive/vfx-shader_skill_2026-11-02/`. Shader dùng chung của project vẫn giữ: `Docs/VFX/SHADERS.md`, `Assets/VFX/_Shared/Shaders/VfxShaderLib.cginc`, noise ở `Assets/VFX/_Shared/Textures/Noise/`.

Chế độ C (**codefx**, VFX hoàn toàn bằng code) cùng thành phần Scorch và CodeFX đã bỏ khỏi skill ngày 2026-11-03 (bản 2.3.0). Bản lưu skill 2.2.0 có codefx: `Docs/VFX/_ArtDirection/_archive/vfx-maker_2.2.0_before_codefx_removal_2026-11-03/`. Prefab đã dựng trong project vẫn giữ.

**Người dùng là art lead.** Yêu cầu hình khối của họ thắng nghiên cứu web và số đo thư viện ([references/shape-language.md](references/shape-language.md), mục "Yêu cầu của art lead"). Quy tắc đang thử nghiệm nằm nháp ở `D:\Game_prj\VFX_LIb\Docs\VFX\_ArtDirection\`. Chỉ đưa vào skill khi art lead nói "chốt".

**Texture lấy từ `Assets/Library/` trước** (art lead 2026-11-04). Đây là thư viện texture đã phân loại bằng mắt:
- Cây `Assets/Library/<nhóm>/<vai trò>/` (glow, impact, ring, ground, lightning, noise, smoke, spark, trail, water, rune, mask, Slash). Chọn theo `Docs/VFX/_Library/LIBRARY.md` (bảng thành phần → thư mục).
- Tên file `<nhóm>_<vai trò>_NNN`; tên cũ và nguồn của từng file ở `Docs/VFX/_Library/library_index.csv`.
- Xem ảnh ứng viên (Read PNG) rồi chọn. Chỉ tạo texture mới (script / Shape Lab / ChatGPT) khi Library không có hình hợp, và nói lý do trong kế hoạch.
- Texture trong Library dùng chung: build script chỉ `LoadAssetAtPath`, không `ImportTexture` lên nó. Cần import setting khác thì copy ảnh (không copy `.meta`) sang `Assets/VFX/<Effect>/Textures/`.
- Ghi đường dẫn Library của từng texture trong kế hoạch.
- Luật đã chỉ định texture cụ thể vẫn giữ (khói mặc định `fx_t_smoke_02.png`, khói vụ nổ GroundBlast v5c).

## 0. Chuẩn bị project (chỉ lần đầu trong mỗi project)

Làm nhanh, không hỏi người dùng trừ khi thiếu thông tin:

1. **Unity version:** đọc `ProjectSettings/ProjectVersion.txt`. Unity.exe nằm ở `C:/Program Files/Unity/Hub/Editor/<version>/Editor/Unity.exe`.
2. **Render pipeline:** `ProjectSettings/GraphicsSettings.asset` có `m_CustomRenderPipeline: {fileID: 0}` → Built-in; có guid → kiểm tra `Packages/manifest.json` có `com.unity.render-pipelines.universal` → URP. HDRP: báo người dùng, skill không hỗ trợ.
3. **Build kit:** nếu chưa có `Assets/VFX/_Kit/`, copy từ thư mục `assets/` của skill này:
   - `assets/VfxBuildKit.cs` → `Assets/VFX/_Kit/Editor/VfxBuildKit.cs`
   - `assets/VfxDemoReplay.cs` → `Assets/VFX/_Kit/Runtime/VfxDemoReplay.cs`
   Nếu đã có, so `VfxBuildKit.Version` với bản trong skill; bản skill mới hơn thì cập nhật (không đụng build script của từng effect).
4. **Quy ước có sẵn:** nếu project đã có quy ước đặt tên/thư mục VFX riêng (xem vài effect cũ), hỏi người dùng giữ quy ước cũ hay dùng quy ước của skill. Mặc định dùng [references/naming.md](references/naming.md).
5. **Pooling/gameplay:** nếu project có hệ pool hoặc VFX manager, ghi lại để prefab khớp (`stopAction`, entry point).

Chế độ B không cần bước này khi chưa có project.

## 1. Nhận mô tả và chọn chế độ

Đầu vào có thể là: mô tả chữ ngắn; ảnh hoặc video tham chiếu (xem bằng Read, chỉ coi là "quan sát được" những gì thật sự thấy); **JSON "Copy thông số" từ Shape Lab** (đọc như ý đồ hình khối chính xác của art lead); hoặc spec đã có. Đọc hết những gì đã có trước khi hỏi, không bắt làm lại phần đã chốt.

**Chế độ:**
- **A. Làm prefab** (mặc định).
- **B. Chỉ spec + prompt bàn giao**: khi người dùng xin prompt/spec, khi effect làm cho engine khác Unity, hoặc khi giao cho người/agent khác. Xem mục 8.
- **Mix (mặc định cho đòn trúng / va chạm / nổ):** nếu effect ghép được từ thành phần chuẩn, **tự mix** (auto mix) rồi dựng, không lập kế hoạch từ đầu. Xem mục 9. Art lead xem rồi yêu cầu đổi.

### 1-pre. Tạo hình — BẮT BUỘC (art lead 2026-11-10)

Trước 1a: mở `Docs/VFX/_Anatomy/<loại>.md` + `materials.md`, chép "Bất biến" vào kế hoạch. Chưa có file hoặc chưa hiểu đối tượng thì research và **lưu file mới** (cách làm: `_Anatomy/README.md`). Biến thể phải giữ hình xương sống; sau build đối chiếu preview với "Bất biến".

### 1a. Định hướng không gian — BẮT BUỘC, trước mọi chế độ

Đọc [references/direction.md](references/direction.md). Xác định: **ngữ cảnh** (air / ground / dir) · **mặt phẳng** (Billboard / nằm đất = Billboard + Render Alignment Local / Stretched; **không dùng Horizontal / Vertical Billboard**) · **góc camera** (mặc định 3/4 nhìn xuống 40°) · **neo** · **quy mô** (m, so với người 2 m) · **di chuyển** · **nền**. Kèm **thời gian** và **các lớp**.

**Brief chưa đủ thông tin về không gian thì PHẢI hỏi trước khi lập kế hoạch hay viết code** (art lead, 2026-11-02). Không tự đoán. Tối đa 2 lượt hỏi; mục người dùng đã nói thì không hỏi lại. Gợi ý của Claude ghi là *đề xuất*. Kết quả ghi thành dòng **Không gian** trong kế hoạch (mục 2).

**Hỏi gọn (các điểm thiết kế khác):** chỉ hỏi điều **làm thay đổi thiết kế**. Gom chung lượt với câu hỏi không gian bằng `AskUserQuestion` (≤ 4 câu, 2–4 lựa chọn mỗi câu; `multiSelect` cho các lớp độc lập). Ví dụ:
- **Art Style** (bắt buộc có trạng thái rõ, nếu brief chưa nói thì hỏi): Stylized / Anime–cel-shaded / Realistic / Hand-painted / Pixel art / Theo dự án–tham chiếu. "Tuỳ bạn" thì tự đề xuất, ghi là *đề xuất*.
- Kiểu phát: một lần (impact, explosion) / lặp (aura, fire loop) / bay (projectile + trail).
- Kiểu sản xuất (art lead định nghĩa): **(1) một phần tử đơn cho particle random** hay **(2) texture sheet chạy frame by frame** (loop = 8 frame 4×2, không loop = 16 frame 4×4).
- Màu chủ đạo (3 ô Core / Mid / Outer; khói bụi dùng ô Dust).
- Có gắn gameplay không (hit, damage, khoá trạng thái), hay chỉ trang trí.

Phần không hỏi thì tự chọn giá trị hợp lý và ghi là **giả định** trong kế hoạch. Đề xuất của Claude không bao giờ được ghi là lựa chọn của người dùng.

### 1b. Shape mới (khi effect cần silhouette chưa có)

1. Tìm trong **`Assets/Library/`** trước (bảng thành phần → thư mục ở `Docs/VFX/_Library/LIBRARY.md`, xem ảnh rồi chọn). Chưa có hình hợp thì tìm tiếp trong **thư viện shape theo nguyên tố** của Shape Lab (gồm nhóm **PixelFX**, 187 effect tham chiếu hình và nhịp) và các thư viện khác ([references/library.md](references/library.md)).
2. Chưa có thì dựng/chỉnh trong **Shape Lab** (link và cách dùng ở library.md). Art lead có thể tự chỉnh rồi gửi JSON "Copy thông số".
3. Đưa **preview silhouette đen–trắng** vào kế hoạch ở bước 2. Không tạo vòng duyệt riêng: silhouette được duyệt cùng kế hoạch.

## 2. Kế hoạch — lần duyệt duy nhất

Trước khi lập kế hoạch, tìm asset tái sử dụng: texture trong `Assets/Library/` trước, rồi project hiện tại, rồi các thư viện ([references/library.md](references/library.md)). Xem trực tiếp ảnh texture ứng viên (Read file PNG) thay vì đoán theo tên.

Đọc [references/particles.md](references/particles.md) để chọn layer và thông số; [references/shaders.md](references/shaders.md) nếu cân nhắc shader mới; [references/dissolve.md](references/dissolve.md) nếu có layer tan/kết thúc đặc biệt.

**Chọn kỹ thuật đơn giản nhất đủ dùng cho từng layer:**
- texture tĩnh + Particle System;
- UV/mask/dissolve trên quad;
- flipbook cục bộ, chỉ khi hình bên trong phải biến đổi mà module không làm được;
- mesh, khi cần thể tích hoặc nhiều góc nhìn.

Texture mang silhouette của **một phần tử**, emitter ghép thành bố cục. Không bake cả effect vào một ảnh, trừ kiểu sản xuất (2). Atlas biến thể không phải chuỗi animation.

Trình bày kế hoạch **gọn trong chat**, theo mẫu:

```markdown
## VFX_<Effect> — kế hoạch v1
Pipeline: <Built-in/URP> · Kiểu: <one-shot/loop> · Thời lượng: <s> · Kích thước: <m> · Art Style: <giá trị> (<đã chọn/đề xuất>)
Không gian: <air/ground/dir> · <mặt phẳng> · camera <3/4 40°> · neo <...> · nền <...> (đã chốt: ...; đề xuất: ...)

| # | Layer (GameObject) | Vai trò & timing | Kỹ thuật | Kết thúc | Material / Shader | Texture (nguồn) |
|---|---|---|---|---|---|---|
| 1 | Flash | lóe sáng 0–0.15s | billboard burst 1 | fade | M_<Effect>_Flash_Add / Mobile/Particles/Additive | T_Glow_Soft (script: glow) |
| 2 | Sparks | tia văng 0–0.6s | stretched billboard, burst 20 | thu nhỏ | ... | T_Spark_Comet (script: comet --style anime) |

Silhouette mới: <ảnh preview / "không">
Gameplay: <chỉ trang trí / hợp đồng: ai sở hữu hit-damage-khoá, thời điểm áp/gỡ, cancel/despawn/pool>
Asset mới cần tạo: <script / thư viện / ChatGPT cho từng texture, hoặc "không">
Shader mới: <không / SH_xxx — lý do>
Ngân sách: tổng max particles ≈ <n>, <m> material, texture ≤ <size>
Giả định: <các giá trị tự chọn>
```

Cột **Kết thúc**: fade / thu nhỏ / ăn mòn (dissolve) / quét theo hướng / vỡ mảng / flipbook. Mỗi layer một cách kết thúc hợp vai trò, không áp một noise dissolve chung cho mọi layer.

Hỏi duyệt bằng `AskUserQuestion` với các lựa chọn kiểu "Duyệt, build luôn" / "Sửa kế hoạch". Người dùng có thể sửa bằng chat. **Không tạo file trong project trước khi kế hoạch được duyệt** (trừ build kit ở bước 0).

Sau khi duyệt, lưu kế hoạch vào `Docs/VFX/<Effect>/Plan.md` (kèm nguồn của từng asset lấy từ thư viện).

## 3. Chuẩn bị asset

**Texture: luôn thử theo thứ tự rẻ → đắt** và ghi nguồn từng texture trong kế hoạch.

**Cách 0. `Assets/Library/`** (art lead 2026-11-04, luôn thử trước). Chọn theo `Docs/VFX/_Library/LIBRARY.md` (bảng thành phần → thư mục) (thư mục con = vai trò), xem ảnh trước khi chọn. Chỉ sang cách 1–3 khi Library không có hình hợp.

**Cách 1. Sinh bằng script** (~1 giây, gần như không tốn token). Các preset:
- **Sáng và hạt:** glow, dot, ring (shockwave), flare, comet (spark cho stretched billboard), star (sao anime đặc), glint.
- **Đòn đánh:** impact (hit spark gai bất đối xứng + mảnh vụn), slash (lưỡi liềm mép rách).
- **Khói:** smoke (khói hoạt hình nhiều múi, bóng chồng khối).
- **Lửa:**
  - fire_element: **lửa kiểu 1 đã chốt với art lead**. Phần tử đơn cho particle random, có sẵn mờ; dùng `--look`, `--sharp`. Quy tắc ở shape-language.md.
  - fire: ngọn lửa anime (lõi tròn + lưỡi S/C + mảng tách), chưa theo spec art lead.
  - fireblob: mảng lửa hạt đậu kiểu cfxr (thư viện ngoài; **không** theo luật lửa của art lead, ở đó dáng hạt đậu là sai).
- **Điện:** lightning (đoạn thẳng góc ngẫu nhiên, thắt sau góc gãy, nhánh 20–45°; nằm ngang hoặc `--vertical`).
- **Khác:** ember, trail, gradient, noise, dissolve.

Tuỳ chọn thêm:
- **Atlas biến thể:** `--grid 2x2`.
- **Flipbook:** chỉ cho khói, lửa, điện (`smoke`, `fire`, `fireblob`, `lightning`).
  - Lệnh: `--grid 4x4 --anim --dir <độ>`. Chọn `--dir` theo hướng effect tan trong game (0 = phải, 90 = lên).
  - Script tự dissolve bằng ít lỗ lớn/vừa/nhỏ và làm mờ dọc theo hướng tan.
  - Script in ra số cặp lỗ cùng cỡ nằm cạnh nhau: con số này phải bằng 0.
- **Kiểu cel:** `--style anime`.

Ví dụ:
   ```
   python -I "D:/Game_prj/VFX_LIb/.claude/skills/vfx-maker/scripts/make_texture.py" comet -o "Assets/VFX/<Effect>/Textures/T_Spark_Comet.png" --style anime
   ```

`python -I <script> list` liệt kê preset và tham số mặc định. Xem ảnh sau khi tạo (Read), chỉnh tham số nếu cần (`--radius --thickness --halo --lobes --pinch --seed`...; đổi `--seed` để có hình khác).
- Chuẩn chất lượng và cách tự kiểm tra: [references/texture-quality.md](references/texture-quality.md).
- Nguyên tắc hình khối từng loại (nghiên cứu web + board Pinterest của người dùng + yêu cầu art lead): [references/shape-language.md](references/shape-language.md). Đọc khi thiết kế hoặc viết TEXTURE REQUEST.

**Cách 2. Shape Lab hoặc thư viện.** Shape Lab xuất PNG đơn và sheet 4×2/4×4 (định dạng Trắng + alpha cho Unity) theo thông số art lead đã chỉnh. Với hình hữu cơ đã có sẵn (lửa, khói, slash, tàn lửa...):
- copy file ảnh, không copy `.meta`;
- đặt vào `Assets/VFX/<Effect>/Textures/`, hoặc `Assets/VFX/_Shared/Textures/` nếu dùng chung;
- **đổi tên theo quy ước**. Import settings do build script đặt lại.

**Cách 3. ChatGPT** (1–2 phút/ảnh, chậm nhất). Chỉ dùng khi hai cách trên không đáp ứng, ví dụ hình đặc thù của concept.
- Làm theo [references/textures-chatgpt.md](references/textures-chatgpt.md): Project "Texture_Maker", gửi khối TEXTURE REQUEST qua app ChatGPT trên máy.
- Claude copy prompt vào clipboard và mở app; người dùng dán, gửi và lưu ảnh.
- Gộp nhiều hình vào một atlas khi được.
- Trong lúc chờ, có thể build với texture tạm (từ script hoặc thư viện), đặt tên `..._TEMP`.

Texture VFX mặc định grayscale/trắng để tint, alpha riêng khi cần. Kiểm tra kênh mà shader thật sự đọc (R hay alpha), không đoán theo đuôi file.

- **Mesh:** ưu tiên mesh có sẵn (thư viện, primitive Unity) hoặc mesh tạo bằng code trong build script (ring, cone, quad strip). Chỉ dùng Blender MCP khi cần hình phức tạp và Blender đang mở.
- **Shader mới** (chỉ khi shader có sẵn không đáp ứng):
  - Kiểm tra `Docs/VFX/SHADERS.md` và `Assets/**/*.shader` trước.
  - Bắt đầu từ `assets/SH_VFX_Particle.shader`, có thể dùng hàm trong `Assets/VFX/_Shared/Shaders/VfxShaderLib.cginc`.
  - Lưu vào `Assets/VFX/_Shared/Shaders/` nếu dùng chung, rồi ghi vào `SHADERS.md`.

## 4. Viết build script

Copy `assets/EffectBuild.template.cs` → `Assets/VFX/<Effect>/Editor/<Effect>Build.cs`, thay `__EFFECT__`, rồi viết từng layer theo kế hoạch đã duyệt. Dùng helper của `VfxBuildKit` (`ImportTexture`, `Material`, `Particle`, `SizeOverLifetime`, `AlphaOverLifetime`, `Finish`...); cấu hình các module còn lại trực tiếp bằng API `ParticleSystem` của Unity.

**Frame over Time của flipbook phải là đường thẳng:** `new ParticleSystem.MinMaxCurve(1f, AnimationCurve.Linear(0f, 0f, 1f, 0.999f))` hoặc `ComponentKit.LinearFrames`. Không dùng `VfxBuildKit.Curve`: curve này có tangent phẳng (ease) nên flipbook khựng ở đầu.

Giữ đúng tên GameObject, material, texture như trong kế hoạch — tên là một phần của hợp đồng với người dùng. Effect có gameplay: tách hình ảnh khỏi logic; shader không quyết định gameplay; cancel/despawn/pool reuse phải dọn đúng trạng thái effect sở hữu.

## 5. Build và tự kiểm tra

1. **Unity đang mở project?** Kiểm tra process: `Get-CimInstance Win32_Process -Filter "Name='Unity.exe'" | Select-Object CommandLine` có chứa đường dẫn project.
   - **Đang mở:** Unity tự compile khi file thay đổi. Nhờ người dùng chọn menu **VFX → <Effect> → Build**, rồi báo lại.
   - **Không mở:** chạy batchmode (chạy nền, có thể mất vài phút):
     ```
     "<Unity.exe>" -batchmode -projectPath "<project>" -executeMethod VfxEffects.<Effect>Build.BuildBatch -logFile "<project>/Logs/vfx_<Effect>.log"
     ```
     Không thêm `-nographics` (cần GPU để chụp preview). Exit code ≠ 0 → đọc log, tìm `error CS` hoặc exception.
2. **Đọc kết quả** trong `Docs/VFX/<Effect>/`:
   - `BuildReport.txt` — lỗi shader, material thiếu, tổng particle.
   - `Preview_sheet.png` — dải ảnh chụp effect ở các mốc thời gian. **Xem ảnh** và so với kế hoạch/tham chiếu: hình dạng, màu, kích thước, timing, cách kết thúc, có layer nào không hiện (material hồng = shader lỗi). Có ảnh concept thì so cùng góc/scale/mốc thời gian và ghi rõ chỗ lệch theo layer.
3. Tự sửa và build lại tối đa 2 vòng cho các lỗi rõ ràng. Không tuyên bố "đã xong" khi chưa xem preview. Compile/build thành công không có nghĩa là đạt mỹ thuật.

## 5b. Review Lab (xem sản phẩm không cần mở Unity)

Sau khi build xong (mục 5), **dựng trang review web** để art lead xem và góp ý ngay trên trình duyệt:

```
python -I "D:/Game_prj/VFX_LIb/.claude/skills/vfx-maker/review-lab/build_review.py" --project "<project>" --effect <Effect>
```

- Ghi ra `Docs/VFX/_Review/index.html` (một file tự chứa, mở bằng double-click; bỏ `--effect` = gom tất cả effect; `--link` = không nhúng ảnh, file nhỏ nhưng phải giữ nguyên thư mục).
- Gồm: timeline Preview_sheet (kéo/phát từng mốc), trình phát flipbook (lưới, FPS, lặp, nền, additive, tint), thư viện ảnh/GIF có zoom, so sánh A/B (kéo ngang / cạnh nhau / nháy; kéo thả ảnh concept vào), Plan + BuildReport, nút Duyệt/Cần sửa, **ghim góp ý lên đúng vị trí và mốc thời gian**.
- Art lead bấm "Xuất phản hồi" rồi dán vào chat: đọc như danh sách sửa chính xác (mỗi ghim có effect, mốc, toạ độ x/y %).
- Bàn giao (mục 6): thay vì chỉ gửi ảnh, nói "đã dựng Review Lab ở `Docs/VFX/_Review/index.html`". Muốn xem qua launch.json thì dùng cấu hình `review-lab` (http.server thư mục `_Review`).
- Chạy lại lệnh sau mỗi lần build lại effect để cập nhật. Góp ý lưu trong localStorage của trình duyệt theo tên project, không mất khi dựng lại.

## 6. Bàn giao

Báo ngắn gọn:
- Đường dẫn prefab `Assets/VFX/<Effect>/Prefabs/VFX_<Effect>.prefab` và scene demo `.../Scenes/<Effect>_Demo.unity` (Play để xem, phím Space để phát lại).
- Gửi ảnh preview sheet và đường dẫn Review Lab (mục 5b).
- Asset mới, asset lấy từ thư viện, phần còn tạm (`_TEMP`), điều chưa kiểm chứng được (ví dụ: chưa test trên thiết bị mobile thật).

## 7. Sửa theo phản hồi

Sửa trong `<Effect>Build.cs` rồi build lại; cập nhật `Plan.md` nếu thay đổi layer/asset. Thay đổi nhỏ (màu, timing, số lượng) không cần duyệt lại; thêm/bớt layer hoặc asset mới thì nêu ngắn rồi làm. Chỉ sửa phần được yêu cầu: đổi màu không được đổi silhouette, timing hay kết thúc đã duyệt.

**Lưu ý:** build lại sẽ ghi đè prefab. Nếu người dùng đã chỉnh tay prefab trong Inspector, hỏi trước: chuyển các chỉnh sửa đó vào script, hay dừng dùng build script cho effect này.

## 8. Chế độ B — spec + prompt bàn giao

Dùng khi không dựng trực tiếp (xem mục 1). Đọc [references/handoff-prompt.md](references/handoff-prompt.md).

1. Lập kế hoạch như mục 2, bổ sung timeline theo layer, hợp đồng gameplay, bảng "dấu hiệu trong concept → cách dựng → cách kiểm tra" nếu có ảnh concept. Đây vẫn là **lần duyệt duy nhất**.
2. Sau khi duyệt, xuất **prompt tiếng Anh tự chứa** (dán được vào phiên mới, không "như trên"). Prompt dài thì lưu `Docs/VFX/<Effect>/Handoff_Prompt.md`.
3. Người dùng xin prompt khi kế hoạch chưa duyệt: xuất bản nháp, ghi rõ **DRAFT — NOT APPROVED** và giữ các điểm còn mở.
4. Chỉ viết prompt thì không tự sửa project hay tạo asset; không tuyên bố đã test trong engine.

## 9. Ghép từ thành phần chuẩn — AUTO MIX (mặc định cho đòn trúng / nổ)

Đọc [references/mix.md](references/mix.md). Chuẩn: [references/components/STANDARD.md](references/components/STANDARD.md).

1. **Không gian** (mục 1a). Chưa rõ ngữ cảnh (đất / trên không / có hướng) thì hỏi.
2. **Brief** (`name`, `context`, `element`, `weight`, `smoke`) → `mix/auto_mix.py --project <project>`.
   Script chọn thành phần, nhịp, độ to, bảng màu, **in lý do từng lớp** và ghi recipe vào `Docs/VFX/_Recipes/`.
3. **Unity** `MixRecipeBuild.BuildBatch -recipe <recipe>` → `Assets/VFX/Mixes/<name>/`.
   - Xem preview, rồi dựng Review Lab (mục 5b).
4. Bàn giao **kèm lý do các lựa chọn**. Art lead yêu cầu đổi thì sửa recipe hoặc brief rồi dựng lại. Mix Lab dùng để xem và tinh chỉnh.
5. **Luật cứng:**
   - một effect chỉ một ngữ cảnh và một chớp va chạm;
   - thứ tự vẽ theo bảng trong `ComponentKit` (mặt phẳng trước, rồi độ sáng; không trùng số);
   - danh sách lớp xếp lớp trước mặt ở trên cùng;
   - Frame over Time dùng `LinearFrames`.
6. Thêm thành phần mới thì làm theo mục 5 trong `references/mix.md`. Sau đó chụp lại dữ liệu Mix Lab bằng `MixCapture`.

Project mới chưa có bộ thành phần: chép vào thư mục **`Editor/`** (đây là script Editor, đặt ngoài `Editor/` thì build game lỗi):
- `assets/components/_Kit/ComponentKit.cs` → `Assets/VFX/_Components/_Kit/Editor/`
- `assets/components/_Mix/MixRecipeBuild.cs`, `MixCapture.cs` → `Assets/VFX/_Components/_Mix/Editor/`

Rồi dựng thành phần theo các spec trong `references/components/`.
