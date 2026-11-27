# VioletThunder — biến thể Crimson và Azure (2026-11-09)

Cùng hiệu ứng với `VFX_VioletThunder` (sét từ trời đánh một điểm đất: tích điện → một tia → nổ trên đất → dòng điện bò trên đất). Mỗi bản đổi **ít nhất hai** trong: mesh/hình tia, bố cục, timing, lớp phụ. Không gian giữ như bản gốc: ground, tia đứng = Stretched Billboard (texture ngang, đầu chạm đất = mép trái), lớp nằm đất = Billboard + Local (GameObject X 90°), camera 3/4 40°, neo điểm đất, tia cao ~6 m, vùng nổ ~3–5 m. Mọi hạt Scaling Mode Hierarchy, Frame over Time tuyến tính, shader `Mobile/Particles/Additive` (không shader mới).

Texture của Crimson / Azure (bản cũ): sheet tia 2×4 và halo của bản gốc (`Assets/VFX/VioletThunder/Textures/T_VioletThunder_Bolt_2x4`, `_BoltGlow_2x4`; trắng + alpha nên tô màu bằng Start Color). **Cần build bản gốc (VFX → VioletThunder → Build) ít nhất một lần trước.** Còn lại lấy từ `Assets/Library/`: `glow/soft_round/glow_soft_round_008`, `glow/flare/glow_flare_005` (sao X), `ring/thin/ring_thin_003`, `ring/ragged/ring_ragged_002`, `ground/crack_radial/ground_crack_radial_001`, `spark/shard/spark_shard_001` (1×4, mũi bên trái), `spark/star/spark_star_001`.

Ghi chú: builder gốc còn trỏ tên cũ trong Library (`glow/glow_023`, `wave/wave_015`...) — Library đã đổi tên, builder gốc sẽ báo thiếu asset nếu build lại. Hai biến thể này dùng đường dẫn mới.

## Crimson (đỏ cam, địa ngục) — menu `VFX/VioletThunder/Build Crimson`, prefab `VFX_VioletThunder_Crimson`
Màu: lõi `FFF1D6`, nóng `FFB040`, cam `FF5A14`, đỏ `D81414`, tối `6A0A10`.

| Trục | Khác bản gốc |
|---|---|
| Bố cục | tia nghiêng 14° (từ trái trên) + tia nhánh mảnh nghiêng −27° (1,9 m, cùng điểm đất); vết nứt đất phát sáng (`crack_radial_001`, 4,4 m) và vòng mảnh co vào điểm đánh lúc tích; dòng điện bò = sheet tia nằm phẳng (hạt 3D 2:1) bán kính 1,9 m, 2 lớp glow + lõi cùng seed |
| Timing | tích 0,6 s (gốc 0,4 s), tia chạm đất 0,64 s; vết nứt âm ỉ ~2,2 s; dòng điện 1,6 s |
| Lớp phụ | chớp = sao X (`flare_005`, một chớp), Cracks, ChargeRing, Embers (mảnh tia lửa Stretched bắn lên rồi rơi, gravity 2), Shock = vòng ragged; bỏ Residue, ImpactStar |

Lớp: Charge (root, order 3), ChargeRing −2, Cracks −3, BoltGlow 4, BoltCore 5, Fork 6, Flash 7, GroundFlash −4, Shock −1, Embers 2, ArcsGlow 0, ArcsCore 1. Thời lượng ~2,7 s (cracks 0,1 + 2,2 s).

## Azure (xanh lam điện) — menu `VFX/VioletThunder/Build Azure`, prefab `VFX_VioletThunder_Azure`
Màu: lõi `EAFBFF`, cyan `4FD8FF`, xanh `2A6BFF`, sâu `1B2CC8`.

| Trục | Khác bản gốc |
|---|---|
| Bố cục | quầng tích điện tụ **trên trời** (5,6 m) rồi loé sao ở gốc tia; tia nghiêng 24°, hẹp hơn (2,6 m); 3 vòng gợn liên tiếp (0 / 0,1 / 0,2 s); vòng tĩnh điện xoay chậm nằm lại trên đất; dòng điện bán kính 2,3 m |
| Timing | tích rất ngắn 0,26 s (gốc 0,4 s), tia 0,24 s (nhanh hơn), tia dội (Echo, mảnh) 0,26 s sau; đất nhiễm điện tồn ~2,3 s (arcs 2,2 s, bắt đầu 14 cung) |
| Lớp phụ | SkyGlow, SkyFlare, Echo, Ripples ×3, StaticRing, Motes (sao lấp lánh bay lên, `spark_star_001`); bỏ Residue, ImpactStar, sóng hồng |

Lớp: SkyGlow (root, order 3), SkyFlare 8, BoltGlow 4, BoltCore 5, Echo 6, Flash 7, GroundFlash −4, Ripples −1, StaticRing −3, ArcsGlow 0, ArcsCore 1, Motes 2. Thời lượng ~2,7 s.

## Chưa xác minh
- Chưa build trong Unity (Unity đang mở). Cần chạy menu, xem preview `Docs/VFX/VioletThunder_Crimson|Azure/Preview_sheet.png` và Review Lab.
- Hướng nghiêng của tia (`shape.rotation = (90 − tilt, 90, 0)`) tính bằng tay: tilt dương phải nghiêng từ trái-trên; nếu ngược dấu thì đổi dấu `tilt`.
- (Đã lỗi thời cho Azure / Crimson, chúng vẫn dùng frame của sheet tia 2:1 và nên được làm lại như Toxic / Gold) Dòng điện bò phải lấy từ `lightning/arc_sheet`, không dùng sheet tia đặt nằm phẳng; xem mục "Dòng điện bò trên đất" ở dưới.

# Đợt 2026-11-13: Toxic, Gold (biến thể) + VioletStorm (effect mới cùng phong cách)
Builder dùng chung `Editor/VioletThunderKit.cs`. Không gian giữ như bản gốc (ground, tia đứng Stretched, lớp đất Billboard + Local, camera 3/4 40°, tia ~6 m). Cần build bản gốc một lần trước (sheet tia). Menu `VFX/VioletThunder/Build Toxic | Build Gold | Build Storm`.

**Bất biến giữ nguyên (Toxic, Gold):** tích → một phát giáng → vỡ vụn → dư điện; tia toon zig-zag (viền + lõi); một chớp + sóng lan đất.

| Bản | Màu | Bố cục | Timing | Lớp phụ |
|---|---|---|---|---|
| Toxic | lõi `F2FFD8`, lime `9CFF3A`, xanh `2FBF2A`, sâu `0E5A1E` | tích sôi ngay trên đất, tia gần đứng (−8°, nét làm dày) rộng 2,9 m (Length Scale 2,25, tia dài ~6,6 m), vũng axit nằm lại | tích 0,55 s, tia 0,4 s, dư ~4,8 s (Pool 3,65 s, Arcs 3,5 s, Spores 4,8 s) | Bubbles (vòng bọt nổ), Pool + PoolEdge, Spores bay lên |
| Gold | lõi `FFFBE6`, vàng `FFD24A`, hổ phách `FF9A1E`, sâu `B8560A` | tích trên cao 4,2 m, tia đứng thẳng rộng 2,67 m (Length Scale 3, tia dài ~8 m), Halo đập tại chỗ | tích 0,32 s, tia 0,3 s | Halo, Shards phun cao (rơi lại), 2 gợn, Motes |

**VioletStorm (effect khác, tím-hồng):** mây giông 6 m, 3 điểm đất được báo (vòng co) rồi bị đánh lần lượt (0,30 / 0,52 / 0,74 s), cuối là một tia lớn ở tâm (0,98 s) kèm chớp đất, sóng ragged, dòng điện bò, vết cháy. Mỗi điểm một chớp + một vòng. Sorting (không trùng): tia 10..17, chớp 30..33, vòng báo −12..−15, vòng −4..−7, Scorch −8, GroundFlash −3, Shock −1, Arcs 0/1, mây 3, vòng −4...

## Sheet tia riêng từng bản (sửa 2026-11-13 sau góp ý của art lead: "sao không thay texture bolt khác?")
Ban đầu 3 bản dùng chung sheet tia của bản gốc nên nhìn na ná nhau. Đã chọn lại sau khi xem contact sheet `lightning/bolt_sheet`:
| Bản | Sheet Library | Nét | Loại |
|---|---|---|---|
| Toxic | `lightning_bolt_sheet_011` + **làm dày nét 17 px** (`make_bolt_sheet.py ... 17`) | mảnh có gân, dày lên để đúng Bất biến "tia toon dày" | thử `012` rồi **bỏ**: nét móc "S"/"C" ngắn, tia lơ lửng không chạm đất (đúng lỗi "móc" của Crimson); `009` (dùng cho Storm), `010` (dùng cho Gold) |
| Gold | `lightning_bolt_sheet_010` | dày vừa, zig-zag cao | `011` (quá mảnh), `012` (móc), `013` (2 khung to, không phải lưới 4×2) |
| VioletStorm | `lightning_bolt_sheet_009` | ngắn, gấp khúc | `010` / `011` (dùng cho Gold / Toxic), `012` (móc) |
Ảnh Library là tia **đứng** 4×2 (1024×2048), nên `tools/make_bolt_sheet.py <png> <tiền_tố>` cắt từng khung, xoay 90° cùng chiều kim đồng hồ (đầu chạm đất = mép TRÁI), ghép lại 2 cột × 4 hàng theo thứ tự khung và làm thêm bản glow mờ: `Textures/T_VioletThunder_<Toxic|Gold>_Bolt(Glow)_2x4.png`, `T_VioletStorm_Bolt(Glow)_2x4.png`. Nội dung tia được **thu về 75% bề ngang ô** (SQUEEZE) để glow mờ không chạm biên ô (lỗi cũ: glow bị cắt thẳng, agent review vòng 3 bắt được), nên Length Scale mặc định 3 và bề rộng bù lên (Toxic 2,9 / Gold 2,67 / Storm 2,0 và 2,8 cho tia cuối), độ dài thật giữ ~6–8 m.
Bài học: lớp glow và lõi **phải cùng bề rộng** (cùng Stretch), glow rộng hơn thì lệch khỏi lõi.

## Dòng điện bò trên đất: dùng `lightning/arc_sheet` (sửa 2026-11-13, art lead nhắc)
Lần đầu mình đặt sheet tia nằm phẳng làm arc mà **không tra bảng LIBRARY.md** (vai trò "cung điện" có sẵn `arc_sheet`). Đã làm lại đúng quy trình (tra bảng → contact sheet → chọn):
| Bản | Sheet | Lưới | Nét | Đã loại |
|---|---|---|---|---|
| Toxic | `arc_sheet_003` (đổi từ `006` sau review: các ô `006` là nét cong chữ "C"/"2" hiện thành móc, không đọc như điện) | 3×3 | zig-zag gọn | 005 (mờ, khó chia lưới), 004 / 007 (có sẵn màu), `arc_single_001` (một sợi đơn) |
| Gold | `arc_sheet_003` (đổi từ `001`: nét `001` nhỏ, coverage 0,011 (`003` 0,019, nét lớn hơn; số đo mean_lum chỉ nhích 0,014 → 0,017 nên lý do chủ yếu là nhìn contact sheet và preview; **arc `003` vẫn nhỏ và mờ**, điểm yếu còn lại) | 3×3 | zig-zag gọn | `001`, `006` |
| Storm | `arc_sheet_003` | 3×3 | zig-zag gọn | |
Ô vuông nên hạt Start Size 1,6–2,8 m, không còn 3D 2:1. Glow = bản làm mờ của chính sheet đó (`tools/make_arc_glow.py` → `Textures/T_..._ArcGlow.png`), đặt dưới sheet Library. **Bài học: mọi thành phần phải tra LIBRARY.md trước, kể cả lớp phụ.**

## Trạng thái
Đã build trong Unity qua MCP (không lỗi compile / console), preview ở `Docs/VFX/VioletThunder_Toxic|Gold`, `VioletStorm/Preview_sheet.png`. Còn yếu: arc của Gold mờ và nhỏ, mây giông Storm còn tròn, tia Toxic mảnh. **Đã duyệt và đưa vào Showcase (art lead 2026-11-13)**: `VFX_VioletStorm` thêm vào `Included`; Toxic / Gold khớp prefix `VFX_VioletThunder` sẵn có; đã chạy Build Scene, scene có 3 instance (nhóm VioletThunder). Spark Gold chỉnh theo art lead: Cone 45°, Limit Velocity over Lifetime (limit 1, dampen 0,2), lifetime 0,3–0,5 s.

## Bảng chọn texture lớp phụ của Toxic / Gold / VioletStorm (xem contact sheet 2026-11-13)
Quầng mềm `Textures/T_VioletThunder_SoftGlow.png` **không nằm trong Library**: là bản alpha-correct của `glow/soft_round/glow_soft_round_017` (512 px, mép mịn) do bản gốc tạo, thay `_008` (chỉ 128 px, vỡ khi to); dùng cho quầng tích điện, GroundFlash, Pool, Scorch. (Dòng "glow_soft_round_008" ở đầu file là của bản cũ, lỗi thời.)
| Thành phần | Ảnh chốt | Lý do | Đã loại |
|---|---|---|---|
| Flash (chớp chữ X, cả 3) | `glow/flare/glow_flare_002` | X sáng sắc, xám, nền đen dùng Additive; omni nên xoay được | `005` (X quá mờ, chớp yếu, từng dùng ở bản đầu), `004` / `006` (có vòng tròn), `001` (đỏ), `003` (tia xoè, không phải X), `010` (alpha, 4 cánh dài hơi cứng) |
| Vòng báo / gợn / vòng (Ripples, Warn, Ring, Bubbles) | `ring/thin/ring_thin_003` (128 px, vòng chỉ chiếm ~36% khung: vòng 7 m thực ~2,5 m, hơi mờ khi to) | vòng mảnh sắc, alpha, omni, co / nở dễ | `013` (vàng), `012` (xanh), `004`/`007`/`008` (viền đặc nền đen), `001` (răng cưa), `014`/`009` (vòng sạch hơn, lớn hơn: chưa dùng vì phải chỉnh lại kích thước, có thể đổi lần sau) |
| Shock (Storm), Halo (Gold) | `ring/ragged/ring_ragged_002` | quầng vòng tia xạ mềm, omni, black_bg Additive; **không phải viền rách** (agent review nhắc đúng), dùng như sóng mềm | `003` (lửa có màu), `006`/`007` (xanh có màu), `005` (cầu vồng), `008`/`010` (quá nhạt), `004` (có hướng) |
| Shock (Toxic) | `ring/thin/ring_thin_014` | vòng mảnh sạch, alpha, omni: đọc rõ là sóng lan (`ragged_002` mềm quá, hoà vào đĩa Pool) | `ring_ragged_002`, `ring_ragged_009` (rất tối, mean_lum 0,027, không đọc được) |
| PoolEdge (Toxic) | `ring/thin/ring_thin_011` | vòng mảnh có quầng, alpha, omni, đọc được làm viền vũng | `ring_ragged_009` (răng cưa nhưng quá tối), `002` (viền mềm không rách), `001` (hai cung rời, có hướng, nhãn xem), `004` (có hướng, vệt nhoè) |
| Spores (Toxic), Motes (Gold) | `spark/star/spark_star_001` | sao 4 cánh trắng, alpha, omni | `006`/`007`/`015` (có màu), `010` (hình sao 5 cánh), `014` (dấu cộng), `012`/`018` (nền đen, quá nhạt) |
| Shards (Gold) | `spark/shard/spark_shard_002` (2×4) **làm bản mềm** `Textures/T_VioletThunder_Gold_ShardSoft.png` (`tools/make_soft_sprite.py`: mờ viền theo từng ô, lõi nóng); **spark điện bắn nhanh, tắt nhanh** (art lead 2026-11-13: bản 1 to, đặc, giống giọt nước; bản 2 rơi chậm như que tăm): sống 0,14–0,32 s, tốc độ 10–18, gravity 0,6, 28 hạt + 14 hạt sau 0,07 s, Start Size 0,22–0,4 m, Size over Lifetime lớn → 0 (1 → 0,55 ở 40% → 0), Length Scale 1,8 + Velocity Scale 0,04 (vệt ngắn) | **đầu dày ở mép TRÁI, đuôi nhọn bên phải = đúng luật Stretched**; có alpha thật | `001`: **ngược hướng** (đầu sáng tù nằm bên phải), black_bg; Crimson (bản cũ) dùng `001` nên bị ngược, chưa sửa |
| Arc (cả 3 dùng `003`; khác nhau ở màu, bán kính, số hạt) | xem mục "Dòng điện bò" phía trên | | |
| Tia (Toxic 011 dày lên / Gold 010 / Storm 009) | xem mục "Sheet tia riêng" phía trên | | |

**Arc là sheet có hướng (nhãn `dir`) nhưng được xoay ngẫu nhiên**: ngoại lệ có chủ ý vì đây là dòng điện bò tứ phía trên đất (không có đầu / đuôi rõ như tia); để bớt spam đã giảm còn 6–7 hạt đầu + rate nhỏ, tối đa 24 hạt. **Chờ art lead chốt**: đổi nhãn arc thành `omni` trong `library_direction.csv`, hay bắt đặt hướng cố định.

## Đèn demo trong Showcase (thêm 2026-11-13, art lead nhắc sau khi đưa vào Showcase)
Khớp tên trong `VfxShowcaseLights.Table` là **khớp chính xác** (prefix bản gốc không áp cho biến thể), nên mỗi effect mới phải có dòng riêng. Đã thêm 12 dòng (chỉ lúc Play, không sửa prefab):
- Toxic: charge (root) `#9CFF3A`, `Flash` `#D8FF9A`, `ArcsCore` `#9CFF3A`.
- Gold: charge (root, tích trên cao) `#FFD24A`, `Flash` `#FFF0B0`, `ArcsCore` `#FFD24A`.
- VioletStorm: mây (root) `#A04CFF` 8 m, `S1_Flash`..`S3_Flash` `#D890FF`, `S4_Flash` `#F0C8FF` (sáng hơn), `ArcsCore` `#E8C0FF`.
Đã chạy Play và kiểm bằng `execute_code`: cả 12 lớp bật Lights module, không có cảnh báo "layer not found". **Quy trình**: mỗi effect mới đưa vào Showcase thì thêm dòng vào `Table` (trong CLAUDE.md đã ghi, lần này mình bỏ sót).
