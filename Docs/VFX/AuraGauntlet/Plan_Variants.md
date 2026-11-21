# VFX_AuraGauntlet: biến thể Fire và Poison (2026-11-09)

Art lead: "tự chọn nguyên tố + chất liệu". Cùng hành vi với bản gốc: aura lặp (loop) ôm một vật thể cao 1.5 m đứng ở gốc toạ độ, camera 3/4 40°, quy mô ~2 m, không scale transform, mọi layer Scaling Mode Hierarchy, root là Particle System. Nằm đất = Billboard + Render Alignment Local, GameObject X 90. Không viết shader mới, không dùng mesh sét: texture từ `Assets/Library/` (đường dẫn mới) + `fx_t_smoke_02` (khói mặc định).

Builder: `Assets/VFX/AuraGauntlet/Editor/AuraGauntletFireBuild.cs` (menu `VFX/AuraGauntlet/Build Fire`) và `AuraGauntletPoisonBuild.cs` (`VFX/AuraGauntlet/Build Poison`). Prefab: `Prefabs/VFX_AuraGauntlet_Fire.prefab`, `VFX_AuraGauntlet_Poison.prefab`. Preview: `Docs/VFX/AuraGauntlet_Fire/`, `Docs/VFX/AuraGauntlet_Poison/`.

## So với bản gốc (sét tím-hồng: khói đỏ, haze, mesh bolt `Guardian_Lighting`, chấm sáng)

| Trục | Gốc | Fire (nóng chảy / tàn lửa) | Poison (bào tử độc) |
|---|---|---|---|
| Lớp phụ | smoke, smoke haze, electric (mesh), dot_Light | ash (khói tro), heat (quầng nóng dưới đất), flames, embers, sparks; **bỏ mesh sét** | gas, puddle (vũng độc), bubbles, spores, drips; **bỏ mesh sét** |
| Layout | hộp phát rải đều quanh vật thể, bolt hướng ngẫu nhiên | **vành đáy r 0.35 phát thẳng lên, xoáy quanh vật (orbital Y 2.5)**; ember rải cả cột; tia bắn từ đỉnh | khí **dồn thấp** (hộp cao 0.35 m), bào tử **quay chậm** quanh vật (orbital Y 0.8), giọt rơi từ đỉnh (y 1.45), vũng bò trên đất |
| Timing | vòng lặp 2 s, đời 0.4 đến 2.5 s | vòng lặp 3 s; lửa 0.6 đến 1 s (nhanh, sôi), ember 1.2 đến 2.4 s, quầng nóng nhịp 1.6 s | vòng lặp 3.5 s, khí 2 đến 3.5 s, mọi thứ chậm và nặng (gravity dương cho khí) |
| Mesh | mesh bolt | không mesh (mất layer mesh) | không mesh (mất layer mesh) |

Mỗi bản khác gốc ở 3 trục (lớp phụ, layout, timing).

Số chính:
- Fire: ash (root, 8/s, 0.6 đến 1.1 m, gravity -0.15), flames (30/s, `smoke_sheet_002` 2x2 khung ngẫu nhiên, vàng → cam → đỏ → tro, co lại), embers (20/s, `glow_soft_round_007`, noise), sparks (6/s, Stretched đầu trái, `spark_streak_001`), heat (`glow_soft_round_029` dưới đất, nhịp 1.6 s). Thứ tự vẽ: ash 0, heat 1, flames 2, embers 4, sparks 5.
- Poison: gas (root, 10/s, 0.8 đến 1.4 m), puddle (`water_splash_002` 2 m, xoay chậm 0.15 rad/s), bubbles (`water_bubble_004`, 5/s), spores (`glow_soft_round_005`, 16/s), drips (6/s, Stretched, gravity 1.2). Thứ tự vẽ: gas 0, puddle 1, bubbles 2, spores 3, drips 4.

Chưa kiểm chứng (Unity đang mở, không build batch): chưa build, chưa xem preview. Orbital velocity quay quanh gốc của system (root), nên tâm xoáy trùng trục vật thể; cần xem hướng xoáy trong Review Lab.
