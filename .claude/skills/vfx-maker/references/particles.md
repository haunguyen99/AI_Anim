# Particle System: layer và thông số

Một effect tốt thường là 3–6 layer đơn giản chồng lên nhau, mỗi layer một vai trò rõ, hơn là một layer phức tạp. Đây là điểm khởi đầu — chỉnh theo brief, không áp nguyên si. **Không dùng Horizontal / Vertical Billboard** (một số game không render được; art lead 2026-10-31): nằm đất = Billboard + Local, đứng theo hướng = Stretched Billboard.

## Nhịp thời gian (one-shot)

**Anticipation → Peak → Dissipation.** Lóe sáng ngắn và mạnh nhất ở đầu (0–0.15s), thân effect (0.1–0.6s), tàn dư kéo dài (khói, ember 0.5–2s). Effect gameplay cần đọc được ngay frame đầu: đặt layer sáng nhất ở t=0.

## Công thức layer phổ biến

Giá trị cho effect cỡ ~2 m. `burst` = Emission → Bursts; `SOL` = Size over Lifetime; `AOL` = alpha trong Color over Lifetime.

| Layer | Texture | Blend | Thiết lập chính |
|---|---|---|---|
| **Flash** | glow tròn mềm | Add | burst 1, lifetime 0.1–0.2, size 2–3, speed 0, SOL 0.5→1.2, AOL 1→0 |
| **Core/Glow** | glow tròn | Add | burst 1, lifetime 0.3–0.6, size 1–1.5, AOL 0→1→0 (đỉnh ~20%) |
| **Sparks** | streak mảnh | Add | burst 15–30, lifetime 0.3–0.7 (random), speed 4–10, shape Sphere/Hemisphere, renderer **Stretched Billboard** (speed scale 0.05–0.1, length scale 1–2), size 0.05–0.15, gravity 0.5–1, Limit Velocity drag hoặc SOL 1→0 |
| **Embers** | chấm tròn nhỏ | Add | burst 10–20, lifetime 1–2, speed 0.5–2, gravity −0.1 (bay lên), Noise strength 0.3–0.5, AOL nhấp nháy nhẹ |
| **Smoke** | puff mềm (hoặc flipbook) | Alpha | burst 4–8, lifetime 1–2, speed 0.5–1.5, start rotation 0–360, Rotation over Lifetime ±30°/s, SOL 0.6→1.5, AOL 0→0.6→0, màu tối hơn nền |
| **Shockwave** | ring | Add | burst 1, lifetime 0.3–0.5, renderer **Billboard + Render Alignment Local** (GameObject xoay X 90°, nằm sát đất) hoặc Mesh, SOL 0.2→1 (ease-out), size 3–5, AOL 1→0 |
| **Debris** | mesh nhỏ | Alpha/Opaque | burst 5–10, renderer Mesh, speed 3–6, gravity 1–2, start rotation 3D random, Collision (plane) nếu cần nảy |
| **Trail** (projectile) | gradient/streak | Add | module Trails (ratio 1, lifetime 0.2–0.4, width over trail 1→0) hoặc TrailRenderer trên root, Inherit Velocity |
| **Ground decal/scorch** | vết cháy | Alpha | burst 1, **Billboard + Render Alignment Local** (xoay X 90°, y 0.01), lifetime 1–3, AOL 1→0 ở cuối, không xoay theo camera |

**Stretched Billboard kéo quad ngược hướng vận tốc** (từ vị trí particle về phía nó vừa đi qua), dài khoảng `size × lengthScale + speed × velocityScale`. Với đuôi lửa bắn về sau quả cầu, quad sẽ chọc ra phía trước nếu phát từ tâm: dời điểm phát (`shape.position`) ra sau đúng bằng chiều dài quad, giảm tốc độ, và đặt `lengthScale` theo tỉ lệ khung texture (frame 2:1 → ~1.6–2).

## Thiết lập mặc định (VfxBuildKit.Particle)

`loop=false`, `playOnAwake=true`, simulation **Local**, scaling **Hierarchy** (scale prefab là scale cả effect), burst 1 tại t=0, shape tắt, không đổ/nhận bóng, random seed cố định theo tên (preview ổn định). Đổi sang **World** cho layer cần để lại dấu vết khi effect di chuyển (trail, khói của projectile).

Loop effect (aura, lửa): `main.loop=true`, `emission.rateOverTime` thay cho burst, `prewarm=true` nếu cần đầy ngay khi bật.

## Ngân sách mobile (đề xuất, đo lại trên thiết bị đích)

| | One-shot thường | One-shot lớn (skill ultimate) | Loop |
|---|---|---|---|
| Tổng particle đồng thời | ≤ 60 | ≤ 150 | ≤ 40 |
| Material | ≤ 4 | ≤ 6 | ≤ 3 |
| Texture | ≤ 256–512 | ≤ 512 | ≤ 256 |

- Overdraw là chi phí lớn nhất trên mobile: hạn chế particle to, alpha thấp chồng nhiều lớp (đặc biệt khói). Ít particle to và rõ tốt hơn nhiều particle mờ.
- Đặt `maxParticles` sát số thực dùng (burst + chút dư), không để mặc định 1000.
- Tránh Collision với world, Lights module, Noise chất lượng cao trên nhiều layer. Dùng chung material giữa các layer khi có thể (giảm draw call).
- Root nên có `stopAction = Destroy` hoặc để hệ thống pool của game xử lý — hỏi nếu project có pool riêng.

## Module hay dùng (API)

```csharp
var main = ps.main; main.startLifetime = new ParticleSystem.MinMaxCurve(0.3f, 0.7f); main.startSpeed = new ParticleSystem.MinMaxCurve(4, 10);
main.startRotation = new ParticleSystem.MinMaxCurve(0, Mathf.PI * 2); main.gravityModifier = 0.8f;
var shape = ps.shape; shape.enabled = true; shape.shapeType = ParticleSystemShapeType.Hemisphere; shape.radius = 0.2f;
var em = ps.emission; em.SetBursts(new[] { new ParticleSystem.Burst(0f, 20) });
var r = ps.GetComponent<ParticleSystemRenderer>(); r.renderMode = ParticleSystemRenderMode.Stretch; r.velocityScale = 0.08f; r.lengthScale = 1.5f;
var tsa = ps.textureSheetAnimation; tsa.enabled = true; tsa.numTilesX = 4; tsa.numTilesY = 4;   // flipbook _4x4
tsa.frameOverTime = new ParticleSystem.MinMaxCurve(1f, AnimationCurve.Linear(0f, 0f, 1f, 0.999f)); // đường thẳng, không dùng VfxBuildKit.Curve (ease → khựng)
var noise = ps.noise; noise.enabled = true; noise.strength = 0.4f; noise.quality = ParticleSystemNoiseQuality.Low;
var limit = ps.limitVelocityOverLifetime; limit.enabled = true; limit.drag = 2f;
```
