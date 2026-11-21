# Waterfall_Map6 (airport-tycoon, scene S_Map6), 2026-11-12

Thác nước loop cho map 6 của airport-tycoon (`D:\Projects\airport-tycoon`), làm qua Unity MCP.
Tạo hình: `Docs/VFX/_Anatomy/waterfall.md`. Ref: video art lead `VFX waterfall.mp4` (khung `ref_frame.png`).

## Lịch sử
1. Bản 1 (chưa có video): vệt trắng 2 lớp + bọt bắn tung + bọt phẳng lưới + gợn to. Art lead: "trông rối quá".
2. Bản 2 (theo video ref): thân màu phẳng + viền trắng mép, cụm bọt trắng đặc, vòng gợn mảnh đứt đoạn. Ảnh `preview.png`.
3. Art lead: "thiếu 1 chút chỗ này". Bậc phẳng y≈13.5 giữa thác trên và 3 dải dưới bị bộ lọc độ dốc bỏ ra nên không có dòng chảy. Đã phủ flow lên bậc (hướng (0.64, 0, −0.77), không viền mép); nền phủ đặc hơn. (Lần đầu thêm nhầm cụm bọt `Ledge_Top`, đã bỏ.) Ảnh `preview_ledge_flow.png`.

## Không gian
- Đứng yên trong thế giới, Built-in, camera game ortho size 96, nhìn xuống 45°, yaw 334.8°. Dải thác rộng 8–15 m, cao ~22–46 m.
- Thân: mesh phủ lên mặt thác. Bọt: Billboard. Gợn: Billboard + Local, GO xoay X 90.

## File (trong airport-tycoon, `Assets/Anim & VFX/`)
- `Editor/WaterfallMap6Build.cs`: menu **VFX → Waterfall → Build Map6 Waterfall** (mở S_Map6 trước; chạy lại thì thay bản cũ). Mọi số chỉnh ở đây.
- `Shader/WaterfallFlow.shader` (`AnimVFX/Waterfall Flow`): màu nền + dải sáng nhạt cuộn V xuống + viền mép từ UV2 (x = 0..1 ngang mặt, y = bề rộng mặt, m).
- `Shader/ToonMaskParticle.shader` (`AnimVFX/Toon Mask Particle`): mask = R×A, viền cứng; alpha hạt = ăn mòn; `_BreakCount/_BreakGap` cắt vòng thành cung.
- `Texture/Waterfall/`: `T_Waterfall_Streak` (Library `water/tile/water_tile_005`), `T_Waterfall_FoamBlob_4x4` (`water/splash/water_splash_006`), `T_Waterfall_Ripple` (`ring/thin/ring_thin_014`).
- `Materials/Waterfall/` (Flow, FoamBlob, Ripple), `Prefab/Waterfall/VFX_Waterfall_Map6.prefab` + mesh `Waterfall_Map6_Flow.asset`. Instance ở gốc scene, đã lưu scene.

## Lớp (bản 2)
| Lớp | Cách làm | Số chính |
|---|---|---|
| Flow | tam giác `Road_M6/Plane.037` có normal.y < 0.93, đẩy ra 0.25 m; gom tam giác chung cạnh + cùng hướng thành mặt; UV0 u = ngang / 24 m, v = theo dốc / 45 m | nền (0.34,0.54,0.93) α 0.65, dải sáng α 0.65 cut 0.75, speed 0.4; viền phải 0.9 m, trái 0.35 m |
| Foam_Blobs | hộp W×1.0 × W×0.25, dời ra trước 0.55W (trước đá), speed 0.5–2, gravity 0 | size W×0.8–1.3, 30/s·strength, life 0.5–0.9, cut 0.18 soft 0.01 |
| Ripples | vòng nở 0.45→2.3× (ease-out), alpha ăn mòn, 3 cung, khe 22% | size W×1×hệ số, 1.1/s, life 1.8–2.2, cut 0.3 |

Điểm chân (x,z): Fall_A–D ở mặt sông dưới y −9.79; Pool_Top (y 35.5, gợn ×0.45); Ledge_Mid (y 13.5, không gợn).

## Chưa làm
- Mép tràn (lip), giọt bắn: ref không có, bỏ.
- Chưa xem trong Play mode / máy thật.
