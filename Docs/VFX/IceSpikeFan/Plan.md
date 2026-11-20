# IceSpikeFan — gai băng đâm lên theo quạt hình nón (Băng; Đất dùng chung builder, đổi texture)

Kế hoạch đã duyệt 2026-11-03 ("Duyệt, dựng Băng trước").

Không gian: ground · điểm đất, quạt hình nón phía trước (trục +z, góc mở 70°) · camera topdown 60° · vùng ~4 m · một lần ~1,2 s · nền tối.
Đã chốt: quạt hình nón, điểm đất ~4 m, topdown 60°, nhanh ~1,2 s, có khói băng + impact + vết nứt. Đề xuất: góc mở 70°, 3 hàng gai, nền tối.

| ID | Layer | Vai trò & timing | Carrier | Shader / nguồn | Kết thúc |
|---|---|---|---|---|---|
| S1 | Gai băng (3 hàng Near/Mid/Far) | trồi 0 / 0,07 / 0,14 s, ~0,15 s có nảy, đứng đến ~0,65 s | Mesh particle `Small_Crystal_01–03` (gần), `Big_Crystal_01/02` (xa); Circle shape arc BurstSpread, alignment World | Coloso **Alpha**, bảng màu `T_IceSpike_Palette.tga` (gradient dưới UV mảnh của mesh), ZWrite bật | co và mờ 0,65–1,05 s |
| S2 | Vết nứt dưới chân | 0–0,06 s hiện, mờ dần ~1 s | Billboard nằm đất (Local, X 90°) 5,2 m | Coloso **Additive**, `T_IceSpike_Cracks.png` (R = alpha), tint xanh lạnh | fade |
| S3 | Impact (chớp, quầng, vòng, tia, khói băng) | auto mix `Docs/VFX/_Recipes/IceSpike_Impact.json` (IMP + GLW + SPK + RNG + DST ground, bảng màu băng) | `MixRecipeBuild.Build` → `Assets/VFX/Mixes/IceSpike_Impact` lồng vào prefab ở (0,0,0,9) | shader của thành phần chuẩn | theo thành phần |
| S6 | Mảnh băng vỡ | 14 mảnh lúc gai trồi, 10 mảnh lúc vỡ (0,72 s) | Mesh `Debris_Crystal_01/02`, gravity + kick lên | Coloso Alpha, cùng bảng màu | thu nhỏ |

Băng / Đất: chỉ đổi 3 thứ — texture bảng màu (xanh băng ↔ nâu đất, cùng vị trí UV của mesh), màu vết nứt, recipe impact (bảng màu). Mesh, nhịp, bố cục giữ nguyên.

Texture: bảng màu `T_Colorpalette 1.tga` copy từ rpg-game (`RPG_VFX/Duong/Texture`) → `Assets/VFX/IceSpike/Textures/T_IceSpike_Palette.tga` (tắt mip, vì UV của mesh nằm trong mảng nhỏ ~0,45 × 0,4); vết nứt `GroundCracks_Radial.png` → `T_IceSpike_Cracks.png`.

Build: menu `VFX → IceSpike → Build` (tự dựng mix impact trước rồi prefab `VFX_IceSpikeFan_Ice`). Build kit: `Assets/VFX/IceSpike/Editor/IceSpikeBuild.cs`.

## v1.1 (sau preview đầu)
- Khói chuẩn (xám, nhiều cụm) quá to che hàng gai gần → recipe: DST size 0,7 · intensity 0,55 · dời vào giữa quạt (offset z +1,2) · delay 0,1; GLW size 0,6; RNG size 0,7.
- Gai chìm 0,12 m xuống đất (đỡ lơ lửng); camera preview gần hơn (6,2 m).

## v2 (2026-11-03, art lead: size băng quá đều, chưa có khối dài hẳn; xếp thành hình tròn; các khối phải sát nhau)
- **Bố cục đổi từ quạt hình nón sang cụm tròn**: 1 gai trung tâm rất dài (~4,4 m), 2 gai dài phụ (~3,4 m), rồi 4 vòng thấp dần (ring1 r 0,65 m × 7, ring2 r 1,25 m × 12, ring3 r 1,9 m × 16, ring4 r 2,55 m × 20). Số khối theo chu vi / bề rộng khối để **sát nhau**, jitter nhỏ (0,05–0,1).
- Chiều cao tách riêng khỏi bề rộng (`startSize3D`, Y độc lập): có khối dài mảnh và khối ngắn bè.
- Đất vỡ (S7): mảnh nâu từ cột nâu của bảng màu (`_MainTex` offset −0,05), ném lên giữa các vòng. Đây là phần thay cho "texture vỡ địa hình"; vết nứt vẫn dùng `GroundCracks_Radial`.
- Impact mix dời về tâm; khói (size 0,8, intensity 0,5), vòng 0,8, quầng 0,7.
- Quạt hình nón (v1) đã bỏ. Muốn quay lại thì đặt `arc` 70° và xoay shape theo +z trong `SpikeRow`.

## v3 (2026-11-03, art lead: quá nhiều băng, giới hạn 5–9 mảnh; hướng đâm ngẫu nhiên, đừng thẳng tuột)
- **8 khối băng** (trước 50+): 1 gai giữa dài ~4 m (nghiêng nhẹ ±0,25 rad), 2 gai dài ~3 m nghiêng mạnh (±0,65), 4 khối vừa ~2 m nghiêng mạnh (±0,75), 1 khối nhỏ ở rìa (±0,8).
- Mỗi hàng xoay shape một góc yaw riêng (0 / 25 / 52 / 120°) nên vị trí không thẳng hàng với nhau; hướng nghiêng ngẫu nhiên quanh X và Z, hướng quay Y ngẫu nhiên.
- Mảnh vỡ giảm theo: băng vỡ 5 + 4, đất vỡ 8.
- Giới hạn "5–9 mảnh" áp cho khối băng chính (S1); mảnh vỡ bay là lớp phụ.

## v3.1 (art lead: các mảnh gần vào nhau, lại xa nhau rồi)
- Cụm gọn: bán kính vị trí Long 0,5 m · Mid 0,95 m · Edge 1,4 m (trước 0,85 / 1,6 / 2,3); khối to hơn một chút (xz ≈ 1,0–1,1) để chạm nhau.
- Độ nghiêng giảm còn ≤ 0,45–0,5 rad (trước 0,65–0,8): đỉnh gai không văng ra xa tâm; vẫn nghiêng mỗi khối một hướng.
- Mảnh đất vỡ gom trong bán kính 1,6 m; camera preview 6,4 m.

## v3.2 (art lead: khói mặc định dùng `fx_t_smoke_02` + shader mobile mặc định của Unity)
- S5 khói băng không còn lấy từ thành phần chuẩn `DST_Ground_01`: layer riêng `S5_IceSmoke` dùng `Assets/VFX/fx_t_smoke_02.png` (trắng, alpha mềm) + `Mobile/Particles/Alpha Blended` (qua `VfxBuildKit.Material`, URP tự đổi sang URP Particles Unlit). Màu tô trắng xanh bằng Start Color.
- Recipe `IceSpike_Impact.json` chỉ còn IMP + SPK + GLW + RNG (bỏ DST).
- Khói: 13 cụm (8 lúc 0,06 s + 5 lúc 0,3 s) từ vòng bán kính 1,2 m quanh chân cụm, bốc lên chậm, to dần, tan ở ~1,1 s.
- **Mặc định khói của art lead cho mọi effect từ giờ** (đã ghi vào bộ nhớ và skill vfx-shader).

## v3.3 (art lead: thêm 1 lớp glow cho mặt đất, dưới layer vỡ địa hình, để băng sáng hơn)
- Thêm **S0_GroundGlow**: đĩa sáng xanh băng nằm đất (Billboard + Local, X 90°), 6,2 m, `Mobile/Particles/Additive`, texture `T_IceSpike_Glow.png` (từ `T_Glow_Soft`), hai đĩa chồng (Burst 2) để đủ sáng trên nền tối.
- Thứ tự vẽ: S0 glow −5 < S2 vết nứt −3 < S5 khói −2 < S7 đất vỡ −1 < gai 0 < mảnh băng 1.
- Nhịp: hiện nhanh (0,05 s), giữ đến ~0,65 s, tắt ở 1,1 s; to dần 0,7× → 1,1×.

## v4 (art lead: thời gian tồn lại của khối băng gấp đôi, thời gian biến mất khác nhau)
- Mỗi khối có **tuổi thọ ngẫu nhiên riêng** (`startLifetime` min–max theo hàng): Tall 2,3–2,6 s · Long 1,7–2,4 s · Mid 1,4–2,3 s · Edge 1,3–1,7 s (trước: tất cả 1,05 s, đứng ~0,45 s). Thời gian đứng tăng từ ~0,45 s lên ~1,1 s (gấp đôi trở lên), rồi co lại ~0,6 s; gai giữa dài nhất tồn lâu nhất.
- Đường cong kích thước theo tuổi chuẩn hoá: trồi 0–10% tuổi, đứng đến 70%, co đến 100%.
- Vết nứt (2,3 s) và glow đất (2,4 s) kéo dài theo để không tắt trước băng; mảnh băng vỡ đợt hai dời tới 1,55 s.
- Tổng thời lượng effect 2,7 s (trước 1,2 s).

## v5 — bản Đất (2026-11-04: "tiếp tục làm đến đất")
- Thêm `Element "Earth"` vào cùng builder `IceSpikeBuild.cs` → prefab `VFX_IceSpikeFan_Earth` (menu `VFX → IceSpike → Build` dựng cả Băng và Đất). Mesh, bố cục 8 khối, nhịp, tuổi thọ, lớp S0–S7 giữ nguyên bản Băng.
- Khác bản Băng đúng 5 thứ: cột bảng màu của gai = cột nâu đỏ u 0,025 (`_MainTex` offset −0,43: tối ở đáy → be ở đỉnh, giống đá hơn cột nâu trơn u 0,405) · đất vỡ dùng cột nâu u 0,405 (−0,05) · vết nứt và glow đất màu hổ phách `(1; 0,62; 0,25)` / `(0,95; 0,6; 0,28)` · khói bụi nâu xám (vẫn `fx_t_smoke_02` + Start Color `(0,62; 0,54; 0,45)`–`(0,78; 0,7; 0,6)`) · impact recipe `Docs/VFX/_Recipes/EarthSpike_Impact.json` (cùng các lớp IMP + SPK + GLW + RNG và cùng độ to với bản Băng, bảng màu đất: Core #FFE7B8, Mid #E0A45A, Outer #7A4A24, Dust #9A8A78).
- Cả hai nằm trong danh sách scene chung (tiền tố `VFX_IceSpikeFan_`): chạy lại **VFX → Showcase → Build Scene**.

## v5.1 (2026-11-04: Đất nhìn trơn như cát → "thay texture hoặc render lại giống đất đá hơn"; "rpg-game có shader vật liệu crystal, thử xem")
- **Shader mới `VFX/FX/Rock Facet`** (`SH_VFX_RockFacet.shader`, đã vào `SHADERS.md`): mặt phẳng + ánh sáng toon giả + MatCap tuỳ chọn. Kỹ thuật MatCap lấy từ vật liệu crystal của rpg-game (`CrystalProwler.mat`: shader OmniShade URP + MatCap `MC Metal Silver`; copy `T_IceSpike_MatCap.png`). Không dùng OmniShade trực tiếp: nặng và chỉ có bản URP.
- **Đất** dùng bảng màu đá riêng `T_IceSpike_RockPalette.png` (tầng màu cứng nâu tối → be, tạo bằng `Docs/VFX/IceSpike/make_rock_palette.py`, vẽ lại mảng UV của mesh) + Rock Facet với toon (tối 0,42 / giữa 0,72 / sáng 1) và MatCap 0,4. Mảnh đất vỡ cùng vật liệu, sáng hơn.
- **Thử pha lê (Băng)**: element `IceCrystal` → prefab `VFX_IceSpikeFan_IceCrystal` (Rock Facet, MatCap 1, tắt toon) để so với `VFX_IceSpikeFan_Ice` (Coloso gradient, đã duyệt). Chờ art lead chọn; xoá bản không dùng (element + prefab + `Docs/VFX/IceSpikeFan_*`).

## v6 (2026-11-04: art lead chọn "Dùng pha lê cho Băng")
- **Băng** đổi sang pha lê: element `Ice` dùng `VFX/FX/Rock Facet` với MatCap 1 (tắt toon) và bảng màu xanh `T_IceSpike_PaletteCrystal.tga` (bản sao có alpha từ xám để qua kiểm tra của kit). Bản Coloso gradient cũ của Băng bỏ.
- Bản thử `IceCrystal` đã xoá (element, prefab, material, scene demo, ảnh preview). Đường Coloso trong builder (`else` của `rock || crystal`) giữ lại làm lựa chọn nếu cần, không element nào dùng hiện giờ.
- Hiện có hai prefab: `VFX_IceSpikeFan_Ice` (pha lê) và `VFX_IceSpikeFan_Earth` (đá), cả hai Rock Facet.

## v7 (2026-11-04: băng cần sáng hơn; đất bỏ glow, đổi kiểu nứt vỡ đất — "đất không hướng tới ánh sáng nhiều, còn băng thì có")
- **Băng sáng hơn:** MatCap Brightness 1,6 → **2,7**, Contrast 1,2 → **0,85** (kéo mặt tối lên, khối vẫn còn mặt). Giữ glow đất và vết nứt phát sáng xanh (băng là hiệu ứng ánh sáng).
- **Đất không phát sáng:**
  - bỏ lớp `S0_GroundGlow`;
  - vết nứt phát sáng (Additive) → **vết nứt vỡ đất**: cùng texture `GroundCracks_Radial` nhưng alpha-blend màu nâu đen (`S2_Cracks`) + một lớp viền bụi nhạt phía sau, to hơn (`S2b_CrackRim`, order −4, alpha 0,55) để vết nứt vẫn đọc được trên nền tối;
  - mảnh đất vỡ tăng từ 8 lên 14;
  - impact `EarthSpike_Impact.json`: bỏ GLW, SPK (tia sáng) và RNG (vòng sóng nhìn như đĩa mờ); chỉ còn IMP chớp yếu (cường độ 0,4, size 0,8) + khói bụi riêng.
- Builder: thêm cờ theo element `groundGlow`, `darkCracks`, `mcBright`, `mcContrast`, `chunks` (Băng: glow, sáng; Đất: không glow, nứt tối, nhiều mảnh đất).

## v8 — Đất khác Băng nhưng vẫn là cùng hiệu ứng (2026-11-04, sửa hiểu lầm)
- Art lead: "tôi chỉ bảo làm có sự khác biệt chứ không phải tự làm thành một cái khác; nếu cần fx khác tôi sẽ yêu cầu". Bản `EarthTusks` (hàng thẳng, effect riêng) mình tự thêm là **sai ý**, đã gỡ (lưu `_archive/EarthTusks_standalone_2026-11-04/`).
- Bản Đất trở lại là **IceSpikeFan_Earth**: cùng hiệu ứng gai đâm lên quanh một điểm (7 khối, 5–9 theo art lead, vết nứt, bụi, đất vỡ, impact yếu), chỉ khác Băng ở **mesh, bố cục, timing** (và không ánh sáng):
  - **Mesh:** ngà đá dày `SM_VFX_Bone` (Băng: pha lê `Big_/Small_Crystal`).
  - **Bố cục:** hình lưỡi liềm (cung) quanh điểm đâm, giữa trống có vết nứt; 1 ngà lớn giữa cung, 2 cánh trái / phải, 2 ngà ngoài (Băng: cụm tròn dày đặc, gai giữa dài nhất).
  - **Timing:** nặng và chậm hơn: trồi 0,25 s (Băng 0,1 s), xuất hiện từ giữa ra ngoài (0 / 0,1 / 0,2 s) và vỡ **theo thứ tự ngược** (ngoài trước: 1,5 / 1,9 / 2,3 s), thay cho tuổi thọ ngẫu nhiên của Băng.
  - Giữ như bản Đất đã duyệt: không glow đất, vết nứt vỡ đất tối + viền bụi, 14 mảnh đất vỡ, khói bụi `fx_t_smoke_02`, impact chỉ chớp yếu (recipe `EarthSpike_Impact.json`), vật liệu đá Rock Facet (toon + MatCap nhẹ).
- Builder: mỗi `Element` có `rows` (bố cục + timing riêng: `IceRows`, `EarthRows`) và hệ số `rise`; `Row` có `arc` (< 360 = chỉ phủ một cung, bắt đầu ở `yaw` độ, chiều kim đồng hồ từ +z).

## v9 — Đất đúng cấu trúc gai, mesh tự vẽ (2026-11-04, sau 2 lần sai)
- Art lead: "đất với băng có cấu trúc gần giống; đổi mesh nhưng chỉ những mesh có cùng tính chất hình học; nếu không có mesh khác thì có thể tự vẽ". Hai thử trước đều **sai**: ngà `SM_VFX_Bone` (nhìn như xương / sừng, màu be) và đá tảng `Debris_Crystal_01` phóng to (tròn, không phải gai). Layout cung lưỡi liềm cũng bỏ.
- **Bản Đất hiện tại:** cùng cấu trúc với Băng: **cụm 8 gai nhọn đâm lên quanh một điểm** (1 dài giữa, 2 dài, 4 vừa, 1 nhỏ), nhưng:
  - **Mesh tự vẽ bằng code** `SM_VFX_EarthSpike_01/02/03` (`MakeSpike` trong builder → `Assets/VFX/IceSpike/Meshes/*.asset`): cột 6 cạnh thon dần thành mũi nhọn, vòng bán kính lệch nhau (có bậc), đỉnh dịch, trục hơi cong, mặt phẳng; UV dùng đúng mảng palette của mesh pha lê (u 0,455, v 0,33–0,51) nên cùng bảng màu đá. Ba biến thể: thon, dày vừa, kim. Thư viện không có mesh gai đá nào.
  - **Vị trí:** bán kính và góc khác Băng, ít đối xứng (Tall r 0,35 · Long r 0,7 · Mid r 1,2 · Edge r 1,7; yaw 40 / 70 / 18 / 200°).
  - **Timing:** nặng, chậm (trồi 0,25 s thay vì 0,1 s), từng hàng nối nhau từ giữa ra ngoài (0 / 0,08 / 0,16 / 0,24 s), **vỡ ngược lại, ngoài trước** với tuổi thọ cố định mỗi hàng (2,5 / 2,1 / 1,75 / 1,45 s), không ngẫu nhiên như Băng.
  - Giữ: không glow đất, vết nứt vỡ đất tối + viền bụi, 14 mảnh đất vỡ, khói bụi, chớp yếu, vật liệu đá Rock Facet (toon + MatCap nhẹ, bảng màu đất đá nâu xám tối `make_rock_palette.py`).

## v9.1 — Đất ngắn, không có tảng dài như Băng (2026-11-04)
- Art lead: "đất thì không nên có các tảng quá dài như băng, vì kết cấu của đất không chắc chắn như băng".
- Chiều cao Đất giảm từ ~1,8–4,2 m xuống **~1,1–2 m** (Tall y 1,3 × mesh 1,6 ≈ 2 m; Long ≈ 1,8; Mid ≈ 1,3; Edge ≈ 1,1). Vẫn là gai nhọn nhưng ngắn, bề ngang ~0,8–1 m.
- Mesh gồ ghề hơn: vòng bán kính lệch mạnh (0,72–1,32), đỉnh dịch sang bên (đỉnh vỡ), ba biến thể ngắn (`MakeSpike` 0,34 × 1,6 · 0,38 × 1,3 · 0,31 × 1,7).
- Thêm **đợt đất vụn thứ hai** (10 mảnh, lúc 1,45 s) khi các khối sập, như mảnh băng vỡ của Băng nhưng là đất.
- Băng giữ nguyên chiều cao (gai giữa ~4 m): băng chắc nên được dài.

## v9.2 — Đất: mesh khác nhau rõ, các khối sát nhau (2026-11-04: "các mesh quá giống nhau, cách quá xa nhau")
- **5 mesh tự vẽ khác hẳn nhau** (`MakeSpike` nhận thêm số cạnh, bán kính từng vòng, kéo dãn dấu chân x / z, độ cong trục): `EarthSpike_01` cột gồ ghề (6 cạnh) · `_02` nêm dẹt nghiêng (5 cạnh, kéo x 1,35 / z 0,7) · `_03` bậc thang (7 cạnh, thu hẹp rồi nở) · `_04` gốc vỡ thấp (đỉnh rộng) · `_05` mảnh mỏng cong (5 cạnh, kéo z 1,4). Trước đó 3 mesh gần như cùng một dạng.
- **Bố cục khít:** bán kính vị trí 0,25 / 0,55 / 0,85 / 1,0 / 1,2 m (trước 0,35 / 0,75 / 1,25 / 1,75), khối đủ rộng để chạm nhau. 5 hàng (Tall, Long, MidA, MidB, Edge), mỗi hàng bộ mesh, kích thước, góc yaw riêng, 8 khối tổng.
- Nhịp, tuổi thọ, chiều cao ngắn của v9.1 giữ nguyên.
