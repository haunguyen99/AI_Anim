# IceSpikeFan: biến thể Magma (obsidian) và Thorn (gai độc) (2026-11-09)

Cùng hiệu ứng với Ice / Earth: cụm 7-8 gai đâm lên từ mặt đất quanh một điểm, vết nứt dưới chân, đất vỡ, khói, mảnh vỡ. Không gian: ground, camera topdown 60°, vùng ~4-5 m, một lần ~2,4-2,9 s, nền tối. Mọi ParticleSystem Scaling Mode Hierarchy (do `Particle()` của kit đặt). Chất liệu quyết định hình: obsidian cứng nên dài sắc; gai độc mảnh, cong, mềm.

Builder: `Assets/VFX/IceSpike/Editor/IceSpikeMagmaBuild.cs`, `IceSpikeThornBuild.cs`, dùng chung `IceSpikeVariantKit.cs` (bản sao helper của `IceSpikeBuild.cs`, không sửa file gốc, không dùng mix recipe). Menu `VFX/IceSpike/Build Magma` / `Build Thorn`; `BuildBatch` có ở cả hai. Prefab: `VFX_IceSpikeFan_Magma`, `VFX_IceSpikeFan_Thorn`.

| | Ice | Earth | Magma | Thorn |
|---|---|---|---|---|
| Mesh | pha lê `Big/Small_Crystal` | 5 gai đá tự vẽ gồ ghề | **4 mảnh obsidian tự vẽ (4-5 cạnh, lưỡi / lăng trụ / mảnh dẹt)** | **4 gai cong móc tự vẽ (5 cạnh, trục cong mạnh)** |
| Bố cục | cụm tròn dày, r 0-1,4 m | cụm tròn, r 0,25-1,2 m | **quạt hình cung 130° phía +z, 4 hàng r 0,35 / 1,0 / 1,7 / 2,4 m** | **vòng hở r 1,5 m, 6 gai + 2 gai nhỏ ở giữa (giữa trống như lồng)** |
| Timing | trồi 0,1 s, tuổi ngẫu nhiên | chậm 0,25 s, vỡ ngược | **sóng phun từ gần ra xa 0 / 0,12 / 0,26 / 0,4 s, trồi rất nhanh có nảy, vỡ đồng loạt 1,8-1,95 s** | **xoắn theo chiều kim đồng hồ mỗi gai 0,07 s, trồi chậm 0,4 s không nảy, héo lần lượt 2,0-2,5 s** |
| Lớp phụ | glow xanh, nứt sáng | nứt tối + viền bụi, bụi | **nứt dung nham phát sáng (cam, nguội dần), glow dung nham, cục dung nham văng, khói tro sẫm, chớp** | **glow độc yếu, nứt dây leo tối, bào tử xanh trôi lên, khói độc xanh xám** |
| Vật liệu | Rock Facet MatCap 1 | Rock Facet toon | Rock Facet tím đen, MatCap 1 (kính) | Rock Facet xanh olive, MatCap 0,25 |

Mỗi biến thể đổi cả 4 trục. Thang chiều cao: Magma 1,4-3 m (obsidian cứng), Thorn 1,2-2,3 m.

Texture: dùng lại `T_IceSpike_RockPalette.png`, `MatCap`, `Cracks`, `Glow` của IceSpike (chỉ đọc, builder import lại đúng setting đã dùng), tô màu bằng `_Tint` (UV mesh nằm trong mảng palette u 0,455 / v 0,33-0,51 như mesh pha lê). Khói `fx_t_smoke_02` + shader mobile mặc định, tô bằng Start Color. Mesh mới lưu ở `Assets/VFX/IceSpike/Meshes/SM_VFX_MagmaSpike_01..04.asset`, `SM_VFX_ThornSpike_01..04.asset` (builder log bounds, trục Y lên, đỉnh +Y).

Chưa kiểm tra bằng Unity (Editor đang mở): hình thực của mesh tự vẽ (seed / bend chỉnh trong `MakeSpike(...)` ở builder), độ sáng MatCap, tên thuộc tính Rock Facet (`_Tint`, `_ShadeDark`, `_ShadeMid`, `_MatCap*`, copy từ `IceSpikeBuild`).
