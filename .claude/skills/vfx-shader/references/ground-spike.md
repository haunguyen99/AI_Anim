# Gai băng / đất đâm lên mặt đất (mẫu: IceSpikeFan, `Assets/VFX/IceSpike/`)

**IceSpikeFan Băng / Đất là demo:** hai bản dùng chung một builder, khác nhau chủ yếu ở bảng màu, vật liệu và lớp ánh sáng. **Đừng lặp lại cách đó cho effect sau:** art lead muốn mỗi effect khác nhau thật (mesh, bố cục, timing, lớp phụ), xem "Mặc định của art lead" trong `SKILL.md`. Một effect gai / khối khác nên đổi: mesh (ví dụ `Fang*`, `Spike`, `Cylinder_*`, `Curve_*` thay cho pha lê), bố cục (hàng thẳng, quạt, vòng, rải), thứ tự trồi (sóng từ gần ra xa, đồng loạt rồi vỡ lần lượt), và lớp phụ.

Băng và Đất **dùng chung một builder** (demo); chỉ đổi bảng màu (texture), màu vết nứt và recipe impact. Ví dụ đầy đủ: `assets/GroundSpikeBuild.example.cs` (từ `IceSpikeBuild.cs`), kế hoạch và lịch sử chỉnh: `Docs/VFX/IceSpikeFan/Plan.md`.

## Lớp (từ dưới lên, theo `sortingOrder`)

| ID | Lớp | Ghi chú |
|---|---|---|
| S0 | Glow đất | đĩa Additive nằm đất (Billboard + Local, X 90°), 6 m, hai đĩa chồng (`Burst(ps, 2)`) mới đủ sáng trên nền tối; order −5 |
| S2 | Vết nứt | `GroundCracks_Radial.png` (R = alpha) + Coloso Additive, tint xanh lạnh; order −3 |
| S5 | Khói | **mặc định:** `fx_t_smoke_02.png` + `Mobile/Particles/Alpha Blended`, tô màu bằng Start Color; order −2 |
| S7 | Đất vỡ | mảnh mesh màu nâu ném lên giữa các khối; order −1 |
| S1 | Gai (khối chính) | mesh pha lê / gai, order 0 |
| S6 | Mảnh băng vỡ | `Debris_Crystal_*`, hai đợt: lúc trồi và lúc các khối bắt đầu co; order 1 |
| S3–S4 | Impact | **auto mix** (`mix/auto_mix.py`, ground, element ice) → `MixRecipeBuild.Build(recipe)` rồi lồng prefab vào; bỏ DST khỏi recipe nếu dùng khói riêng |

## Gai (S1): số khối, bố cục, chuyển động

- **Ít khối, sát nhau:** art lead giới hạn **5–9 khối chính** (IceSpikeFan: 8). Đặt khối **sát nhau** (bán kính các vòng nhỏ: 0 / 0,5 / 0,95 / 1,4 m), không rải rời rạc. Lần đầu làm 50+ khối và quạt hình nón đều: bị chê "đều, không có khối dài, quá nhiều".
- **Không đều:** có **một khối dài hẳn** (gai giữa ~4 m), vài khối dài (~3 m), vài khối vừa (~2 m), một khối nhỏ ở rìa. Chiều cao tách riêng khỏi bề rộng: `startSize3D` với `startSizeY` độc lập.
- **Hướng ngẫu nhiên, không thẳng tuột:** `startRotation3D`, nghiêng X và Z ngẫu nhiên (≤ 0,45–0,5 rad; nghiêng mạnh hơn thì đỉnh văng xa và cụm trông rời), xoay Y ngẫu nhiên. Mỗi hàng xoay shape một góc `yaw` riêng để các hàng không thẳng hàng.
- **Vị trí:** mỗi hàng = một Particle System, Circle shape trên mặt đất (`AngleAxis(-120, (1,1,1))` để vòng nằm XZ, bắt đầu ở +z), `arcMode = BurstSpread`, `randomPositionAmount` nhỏ. `renderer.alignment = World` để mesh luôn đứng thẳng dù shape xoay.
- **Trồi và tan:** `sizeOverLifetime` tách trục: Y 0 → 1,15 (nảy) ở 5% tuổi, đứng đến 70%, co về 0; X/Z co nhẹ về 0,25. Gai chìm 0,12 m xuống đất để không lơ lửng.
- **Tuổi thọ:** mỗi khối một tuổi thọ ngẫu nhiên (`startLifetime` min–max theo hàng) để **tan không cùng lúc**; gai giữa lâu nhất. Đã chọn: đứng ~1,1 s, tổng ~2,1 s (art lead: "tồn lại gấp đôi, thời gian biến mất khác nhau"). Kéo dài S0 và S2 theo, nếu không đất tắt trước khi băng tan.

## Texture bảng màu (đổi Băng ↔ Đất)

Mesh `Big_/Small_Crystal_*`, `Debris_Crystal_*` có UV nằm trong một mảng nhỏ (~0,45 × 0,34–0,50) vì được làm để dùng với `T_Colorpalette 1.tga` (rpg-game, copy thành `T_IceSpike_Palette.tga`). Mỗi cột của bảng là một gradient từ tối ở đáy lên sáng ở đỉnh.
- **Băng:** cột u ≈ 0,455 (tím tối → xanh → xanh nhạt). **Đất / đá vỡ:** cột nâu u ≈ 0,405, tức `_MainTex` offset **−0,05**. Chỉ việc dịch offset của material, không cần texture mới.
- Import: **tắt mipmap**, filter Bilinear, bỏ alpha (mip làm nhoè gradient trong mảng UV nhỏ).
- Shader: Coloso **Alpha**, `_CullMode` 2, **`_ZwriteMode` 1** (khối đặc tự che nhau), dissolve giữ hiện hẳn (`_UseManual_DebugDissolve` 1, `_ManualDissolve` 1), `_MainClamp` bật.
- Muốn thử cột khác: đọc palette bằng Python (PIL) tại u, v ∈ [0,34; 0,49] để chọn gradient mong muốn.

## Ghi chú theo nguyên tố

- **Băng:** bảng màu xanh (cột 0,455); vết nứt tint `(0,55; 0,85; 1)`; impact `element = ice`; khói trắng xanh (Start Color `(0,78; 0,9; 1)`–`(0,92; 0,97; 1)`); mảnh vỡ `Debris_Crystal_*`.
- **Đất** (đã làm, `VFX_IceSpikeFan_Earth`, cùng builder): **gradient mượt chưa đủ giống đá** (cột nâu trơn trông như cát; cột nâu đỏ u 0,025 vẫn mượt). Bản hiện tại: bảng màu đá riêng `T_IceSpike_RockPalette.png` (tầng màu cứng, `make_rock_palette.py`) + shader **`VFX/FX/Rock Facet`** (mặt phẳng tô toon 3 bậc bằng ánh sáng giả + MatCap 0,4). Cũ: cột nâu đỏ u 0,025 (offset −0,43) cho gai, cột nâu 0,405 (−0,05) cho đất vỡ; vết nứt `(1; 0,62; 0,25)` và glow đất `(0,95; 0,6; 0,28)` màu hổ phách; khói bụi nâu xám (vẫn `fx_t_smoke_02`, Start Color `(0,62; 0,54; 0,45)`–`(0,78; 0,7; 0,6)`); impact: copy recipe Băng (bỏ DST, cùng size) đổi `palette` thành Core #FFE7B8 / Mid #E0A45A / Outer #7A4A24 / Dust #9A8A78 (`EarthSpike_Impact.json`). Thêm nguyên tố mới = thêm một `Element` (các trường `palette`, `crystalColumn`, `chunkColumn`, `crack`, `glow`, `smokeA/B`, `recipe`).
- **Slash Đất** (`Slash360_Earth`): Coloso **AlphaCutOut** (cutoff ~0,4), mảnh đá `SM_VFX_Spike` + `Debris_Crystal_01`, bảng màu core `(0,95; 0,8; 0,5)` / mid `(0,6; 0,4; 0,22)` / outer `(0,28; 0,17; 0,1)`.
- Slash không cần nguyên tố khác (art lead), HealCircle: xem [magic-circle.md](magic-circle.md).
- Các nguyên tố còn lại (Lửa, Sét, Độc): art lead sẽ bổ sung cách làm; thêm vào đây khi có.

## Bài học quy trình

- **Chọn mesh bằng cách render thử UV** (đỏ = u, xanh = v) trước, đừng tin tên: `Slash_360` là vòng dây đứng; `Slash_Circle_Thin` mới là vành phẳng. Mesh vành có mặt cắt hai mặt chồng: `_CullMode` 2 để Additive không cộng đôi.
- **Dựng thử ở project tạm** khi Unity chính đang mở (`-batchmode`, không `-nographics`; manifest chỉ có `com.unity.modules.*` + `com.unity.ugui`), xem preview và phóng to tìm lỗi viền / lớp lòi ra ngoài trước khi báo art lead. Preview của Unity chính trùng từng byte với bản tạm.
- **Chỉnh theo phản hồi từng bước, nhìn ảnh sau mỗi bước.** Phản hồi mơ hồ ("đang có lỗi visual") không kèm ảnh: phóng to preview, sửa phần thấy được, nói rõ phần chưa chắc.
- Dùng `Docs/VFX/<Effect>/Plan.md` ghi từng phiên bản (v1, v1.1, …) với lý do art lead đưa ra: lịch sử này giúp khỏi lặp lại lỗi.
- Giữ prefab đặt tên `VFX_<Tên>.prefab` trong `Prefabs/`; chạy lại **VFX → Showcase → Build Scene** sau khi build, và thêm tiền tố vào `Included` khi effect được duyệt.


## Vật liệu pha lê / đá: shader Rock Facet + MatCap (2026-11-04)

- Gradient bảng màu chỉ cho dải mượt theo chiều cao; muốn **khối low-poly có mặt sáng / tối** (đá, pha lê) dùng `VFX/FX/Rock Facet`: pháp tuyến mặt phẳng tính bằng ddx/ddy nên không phụ thuộc normal của mesh, không dùng ánh sáng scene (`_LightDir` cố định).
- **Đá:** bảng màu tầng cứng (script `make_rock_palette.py` vẽ lại mảng UV) + toon (`_ShadeDark` 0,42, `_ShadeMid` 0,72) + MatCap nhẹ (0,4).
- **Pha lê (Băng, đã chọn 2026-11-04):** tắt toon (`_ShadeDark = _ShadeMid = 1`), `_MatCapAmount = 1`, MatCap `MC Metal Silver` của rpg-game (kỹ thuật vật liệu crystal `CrystalProwler.mat`: OmniShade URP + MatCap; chỉ lấy ý tưởng MatCap, không dùng OmniShade vì nặng và chỉ có bản URP).
- Texture bảng màu cho Rock Facet phải import `alphaFromGray` (kiểm tra alpha-blend của kit). Nếu cùng một file dùng cho Coloso (cần alpha tắt) thì copy thành file riêng.
- Ví dụ: element `Earth` (đá) và `Ice` (pha lê) trong `assets/GroundSpikeBuild.example.cs`. Băng ban đầu dùng Coloso gradient (mượt, bóng); art lead chọn pha lê MatCap vì nhiều mặt hơn.

## Băng phát sáng, Đất không (art lead, 2026-11-04)

Quy tắc theo nguyên tố: **băng hướng tới ánh sáng** (nhiều glow, vết nứt phát sáng, pha lê MatCap sáng: `mcBright` 2,7 / `mcContrast` 0,85), **đất không phát sáng** (không glow đất, không tia sáng, không vòng sóng đĩa mờ; vết nứt = **vết nứt vỡ đất** alpha-blend nâu đen + viền bụi nhạt phía sau; nhiều mảnh đất vỡ; impact chỉ chớp yếu + khói bụi). Cờ trong `Element`: `groundGlow`, `darkCracks`, `mcBright`, `mcContrast`, `chunks`. Áp tương tự cho nguyên tố khác: lửa / sét / băng / thánh = phát sáng (Additive); đất / độc? hỏi art lead khi chưa nói.


## Đất: biến thể khác Băng nhưng cùng hiệu ứng và cùng tính chất hình học (2026-11-04)

Art lead: Đất và Băng **cấu trúc gần giống nhau** (cụm gai nhọn đâm lên); "bạn đổi mesh nhưng cũng chỉ những mesh có cùng tính chất hình học thôi; nếu không có mesh khác thì có thể **tự vẽ**"; "chỉ bảo làm có sự khác biệt chứ không phải tự làm thành một cái khác". Hai lần mình làm sai: **ngà `SM_VFX_Bone`** (nhìn như xương / sừng, màu be nhẵn) và **đá tảng tròn** (`Debris_Crystal_01` phóng to) thay cho gai; còn tự biến thể thành effect riêng (`EarthTusks`, hàng thẳng). Cách đúng, đã áp dụng ở `IceSpikeFan_Earth` (builder `assets/GroundSpikeBuild.example.cs`):
- Giữ **bản chất** (cụm 5–9 gai **nhọn** đâm lên quanh một điểm, vết nứt, bụi, đất vỡ, impact). Mesh phải **cùng tính chất hình học** (nhọn, thon, đứng): không dùng mesh tròn / cong / dẹt.
- Thư viện không có mesh gai đá → **tự vẽ**: `MakeSpike` trong builder tạo `SM_VFX_EarthSpike_01/02/03` (cột 6 cạnh thon thành mũi nhọn, vòng bán kính lệch nhau, đỉnh dịch, trục hơi cong, mặt phẳng, UV vào mảng palette u 0,455 / v 0,33–0,51 như mesh pha lê). Sửa tham số `MakeSpike(name, seed, radius, height)`, `hy` (chiều cao các vòng), `hr` (bán kính các vòng; đỉnh nhỏ = nhọn hơn).
- Khác Băng ở **vị trí** (bán kính / góc khác, ít đối xứng) và **timing** (chậm, nối nhau từ giữa ra ngoài, vỡ ngược, tuổi thọ cố định theo hàng) và ánh sáng theo nguyên tố (đất không phát sáng).
- Trong builder: mỗi `Element` có `rows` (bố cục + timing riêng: `IceRows`, `EarthRows`) và `rise`; `Row.arc` < 360 phủ một cung (`yaw` = góc bắt đầu).
- Mesh có UV nằm trong mảng nhỏ của palette cần **vẽ thêm mảng đó** trong `make_rock_palette.py` (`PATCHES`); nhớ kiểm tra mesh không ra màu tím vì mảng chưa vẽ.
- `ShapeType.Edge` + `radiusMode Loop` không rải vị trí phát dọc đường: dùng `Random`.

## Độ dài theo vật liệu (art lead, 2026-11-04)

**Chất liệu quyết định chiều cao**: băng chắc nên có gai rất dài (đến ~4 m); **đất kết cấu không chắc nên chỉ ngắn (~1–2 m), gồ ghề, đỉnh vỡ, rồi vụn ra khi sập** (đợt đất vụn thứ hai). Đá / đất / cát: ngắn và dày; băng / pha lê / kim loại: có thể dài mảnh. Khi làm biến thể sang chất liệu khác, đặt lại chiều cao theo độ chắc của chất liệu, đừng chép chiều cao của bản trước.

## Nhiều mesh phải khác nhau thật, và đặt sát (art lead, 2026-11-04)

Khi một cụm dùng nhiều mesh, **các mesh phải khác nhau rõ về hình** (không chỉ đổi kích thước / seed): đổi số cạnh, hồ sơ bán kính từng vòng (thu hẹp rồi nở = bậc thang), kéo dãn dấu chân (nêm dẹt), độ cong trục, độ cao (gốc vỡ thấp ↔ mảnh mỏng). Mẫu: `EnsureEarthSpikeMeshes` (5 mesh Đất). Và **các khối đặt sát nhau**: bán kính vị trí cỡ nửa bề rộng khối; cách xa là lỗi hay mắc (Đất lần đầu bán kính tới 1,75 m, bị chê "cách quá xa"). Dùng nhiều hàng nhỏ (mỗi hàng bộ mesh + kích thước + yaw riêng) để các khối cạnh nhau không cùng dạng.
