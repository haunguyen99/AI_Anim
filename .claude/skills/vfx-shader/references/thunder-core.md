# Điện: 3 thành phần cốt lõi của VFX_BossRaid_Knight_Thunder (art lead chốt 2026-11-04)

Nguồn: bản copy 100% ở `Assets/VFX/_Imported/RpgThunder/` (prefab gốc `RPG_VFX/VFX_Base/VFX_BossRaid_Knight_Thunder.prefab`). Root của prefab: pos (0, -0.07, 2.39), **scale 0.5**: kích thước thật trong cảnh = size trong Particle System × 0.5 × scale của layer. Mọi layer bắn 2 nhịp (t = 0 và t = 0.1 / 1.0 như bên dưới), `Play On Awake`, không loop, simulation space Local, Gravity 0, Speed gần 0.

Art lead: **line_impact = cột sáng vàng ban đầu** (không phải tia zig-zag).

## 1. line_impact – cột sáng vàng
| Mục | Giá trị |
|---|---|
| Object | pos 0, rot 0, scale 1 |
| Main | Duration 0.2, Looping off, Start Lifetime **0.15**, Start Speed **0.1**, **3D Start Size (35, 50, 5)**, Start Rotation 0, **Start Color = Two Colors: (1, 0.804, 0.035) .. (0.955, 0.86, 0.481)** (vàng đậm .. vàng nhạt), Max Particles 1000 |
| Emission | Rate 0; Burst t=0 ×1 và t=**0.1** ×1 |
| Shape | Cone, Angle **0**, Radius 0.0001, Rotation X **-90** (hạt bay lên +Y) |
| Texture Sheet | Grid **5×1**, Whole Sheet, Frame over Time **tuyến tính 0→1** trong đời hạt, Start Frame 0, Cycles 1 |
| Color over Lifetime | màu: 0 trắng → 0.27 (0.96,0.95,0.96) → **0.47 xanh (0, 0.52, 1)** → 0.74 trắng; alpha: 1 đến 0.74 rồi → 0 ở 1 |
| Không bật | Size over Lifetime, Rotation, Custom Data, Noise, Velocity |
| Renderer | **Stretched Billboard**, Length Scale 2, Velocity Scale 0, Camera Velocity 0, **Pivot (0, 1, 0)** (đáy cột nằm trên mặt đất, cột mọc lên trên), **Flip (0.5, 0.5)** (lật ngẫu nhiên), Max Particle Size 5, Sorting Order 0, GPU Instancing on, Vertex Streams: Position, Normal, Color, UV, UV2, Custom1 XYZW (shader không dùng Custom) |
| Material | `M_lightning_bossraid`: `Mobile/Particles/Additive`, `_MainTex` = `lightning_texture_sheet1.png`, **Tiling 1×1**, Offset 0 |
| Kích thước trong cảnh | 35 × 0.5 = 17.5 m ngang, 50 × 0.5 = 25 m cao |

## 2. wave – sóng nền
| Mục | Giá trị |
|---|---|
| Object | rot X **-90**, scale 1 |
| Main | Duration 1.2, Start Delay **0.05**, Start Lifetime **0.5**, Start Speed 0, **Start Size 30**, Start Color (0.98, 0.93, 0.42, 1), Scaling Mode **Local** trong mẫu (khi dựng lại dùng Hierarchy theo luật art lead và nhân đôi Start Size lên 60 để vòng vẫn 30 m) |
| Emission | Rate 0; Burst t=0 ×1 và t=**1** ×1 |
| Size over Lifetime | 0.38 → 1 (mẫu: Scaling Mode Local nên không nhân root 0.5 → vòng cuối 30 m) |
| Color over Lifetime | màu trắng; alpha 1 đến 0.41 rồi → 0 |
| Renderer | **Billboard, Render Alignment Local** (kết hợp rot X -90 → nằm đất), Max Particle Size 5, Sorting Order 0 |
| Material | `wave 1`: `Mobile/Particles/Alpha Blended`, `_MainTex` = `wave 1.png` (PNG palette, **alpha thật 0..62, rgb trắng**: KHÔNG import alphaFromGray, nếu không sẽ thành khối vàng đặc) |

## 3. flare – chớp lõi
| Mục | Giá trị |
|---|---|
| Object | rot 0, **scale 2** |
| Main | Duration 2, Start Lifetime **0.3**, Start Speed 0, **Start Size 15**, Start Color (1, 0.91, 0.57, 1), Max Particles **1** |
| Emission | Rate 0; Burst t=0 ×1 |
| Color over Lifetime | màu trắng; alpha 1 đến 0.66 rồi → 0 |
| Không bật | Size over Lifetime, Rotation, Shape (type Cone mặc định, bị tắt) |
| Renderer | Billboard, **Render Alignment Local**, Max Particle Size 0.5, **Sorting Order 1** |
| Material | `glow add`: `Mobile/Particles/Additive`, `_MainTex` = `TX_VFX_Mask16.png` |
| Kích thước trong cảnh | 15 × 2 (scale layer) × 0.5 (root) = 15 m |

## Các layer còn lại của Thunder (phụ)
`Thunder` (root, nứt đất): Billboard, shader `VFX/Master` + `T_VFX_Ground_Crack`, size 25, vàng (1, 0.86, 0.23), alpha 0 → 1 (0.18) → 1 (0.71) → 0, life 1; `impact`: Billboard Local, `flashLarge`, burst t=0 và t=1; `electric_remain`: Stretched, `HandPaintedLightning2` 3×3, burst 10 hạt t=0 và t=1, Start Color Two Colors trắng .. (1, 0.94, 0.52), `ERB/Particles/Add_CenterGlow`; `Particle System`: mesh + `Thrust` shader, delay 1 s.
Nhịp: 2 lần, t=0 và t=1 (impact, wave, electric_remain); line_impact đánh t=0 và t=0.1.

Bản xem trước đã render: `Docs/VFX/_Reference/rpg-game_Thunder/`.

**Lưu ý đọc prefab:** Start Color có chế độ `minMaxState`: 0 = một màu (lấy maxColor), 2 = Two Colors (min..max). Texture thay được nếu cùng thuộc tính (art lead 2026-11-04): cột = sheet 5×1 có alpha, additive; wave = vòng alpha mềm, alpha blended; flare = mask tròn mềm, additive. Phần setup 3 layer giữ nguyên.

**Khi dựng lại:** không giữ scale 0.5 của root: nhân vào size (line_impact 3D (17.5, 25, 2.5), wave 30, flare 15, nứt đất 12.5, cung điện 2–5), mọi transform scale 1.
