# Thành phần 04 — Sparks (tia lửa) · nháp v0 (2026-11-02)

> Trạng thái: **NHÁP.** Kiểu đã chọn: **A Streak + lớp phụ C Ember** (art lead, 2026-11-02).
> - Đã dựng thử 3 prefab `CMP_SPK_Air/Dir/Ground_01` ở `Assets/VFX/_Components/Sparks/` (`SparksComponentsBuild.BuildBatch`).
> - Preview ở `Docs/VFX/_Components/Sparks/<ID>/`. `Preview_combo` ghép cùng Impact + Glow + Ring.
> - Texture + ảnh so sánh sinh bằng `scripts/spark_sheet.py`. Đã kiểm tra trong preview Dir: đầu tia nằm phía xa, đuôi hướng về điểm trúng, đúng hướng.
> - Màu đã dựng: Core → Mid → Outer chia đều (Mid ở 0.5). Ember: Lifetime 0.6–1.2, Drag 2.5, Gravity 0.2 (Ground) / 0 (Air, Dir).

**Vai trò:** các tia nhỏ bắn toả từ điểm trúng. Sparks cho thấy **lực và tốc độ** của đòn, đồng thời làm VFX "sống" lâu hơn chớp va chạm một chút (0.4–0.6 s).
- Là chi tiết nhỏ, nhiều hạt, **không tạo khối**. Không được che Impact.
- Nhanh lúc đầu, chậm dần (lực cản), rồi co lại và tắt.

Ảnh các kiểu: [spark_options.png](spark_options.png). Đây là ảnh mô phỏng 2D, chưa phải Unity: texture + Air / Dir / Ground ở camera 3/4.

---

## 1. Kiểu tia (chọn 1 làm mặc định)

| Kiểu | Hình | Mặt phẳng | Hợp với |
|---|---|---|---|
| **A · Streak (vệt sao chổi)** | Đầu tròn sáng, đuôi thon mềm | Stretched Billboard | Bán thực, đòn kim loại, lửa |
| **B · Toon (kim nhọn)** | Hình thoi dài, mép sắc, lõi sáng | Stretched Billboard | Anime/toon, đọc rõ ở màn hình nhỏ |
| **C · Ember (đốm lửa)** | Đốm tròn, lõi sáng | Billboard | Tàn lửa bay chậm, sống lâu hơn. Đề xuất làm **lớp phụ** đi kèm A hoặc B, không làm kiểu chính |

Texture (theo chuẩn mục "Texture Stretch"):
- A, B: **256×64, nằm ngang**. **Đầu sáng ở mép TRÁI** (= hướng bay), đuôi ở mép phải.
- C: 64×64.
- Cả 3 đều để RGB trắng, hình nằm ở alpha (material Additive).

> Shader có sẵn `VFX/FX/Spark` (FireballImpact L5) vẽ **đầu ở +X = mép phải**. Theo kiểm chứng 2026-10-31, mép phải là đuôi, nên shader này có thể đang vẽ ngược. Thành phần này dùng texture (1 sample, màu lấy từ ô màu chung) nên không bị ảnh hưởng. Shader cũ cần kiểm tra lại riêng.

---

## 2. Chọn biến thể theo ngữ cảnh

| Biến thể | Khi nào | Hình toả |
|---|---|---|
| `SPK_Air` | Trúng giữa không, nổ toả cầu | Toả **cầu** đều mọi hướng, gần như không rơi |
| `SPK_Dir` | Đòn có hướng (chém, đâm, bắn trúng) | **Nón hẹp ~28°** theo hướng đòn, nhanh hơn, tia dài hơn |
| `SPK_Ground` | Chạm đất, đập đất | Toả **nửa trên** (nghiêng 15–75° so với mặt đất), **trọng lực mạnh**: bắn lên rồi rơi thành vòng cung |

---

## 3. Thông số Particle System

Chung (A/B):
- **Main:** Looping tắt · Duration 0.6 · Simulation Space **World** (tia không đi theo vật trúng) · Start Color trắng (màu do Color over Lifetime).
- **Emission:** Burst 1 lần tại 0 s.
- **Limit Velocity over Lifetime:** **Drag 1.6**: nhanh lúc đầu, chậm dần. Đây là chỗ tạo cảm giác "lực".
- **Size over Lifetime:** 1 → 0 (co lại = kiểu kết thúc `shrink`).
- **Color over Lifetime:** Core (0) → Mid (0.4) → Outer (1). Alpha 1 tới 60%, về 0 ở 100%.
- **Renderer:** **Stretched Billboard** · Length Scale **2** · Speed Scale **0.045** (tia dài khi bay nhanh, ngắn lại khi chậm) · **Pivot (0,1,0)**: đuôi nằm ở hạt, đầu vươn ra trước. Pivot 0 làm đuôi tia (dài 0.5–0.8 m lúc mới bắn) chọc ngược qua điểm trúng ở các frame đầu (art lead phát hiện 2026-11-02, ảnh [spark_pivot_fix.png](spark_pivot_fix.png)) · Max Particle Size 3 · Sorting **2** (trên Glow/Ring, ngang Impact).
- **Material:** Mobile/Particles/Additive.

| Module | `SPK_Air` | `SPK_Dir` | `SPK_Ground` |
|---|---|---|---|
| Burst (số hạt) | 22 (random 18–26) | 18 (14–22) | 20 (16–24) |
| Start Lifetime | 0.35–0.6 | 0.3–0.5 | 0.4–0.6 |
| Start Speed | 3–9 | **6–13** | 3–9 |
| Start Size (bề ngang tia) | 0.05–0.13 m | 0.05–0.13 m | 0.05–0.13 m |
| Size by Speed (độ to theo tốc độ) | range 3–9 · curve 0.7 → 1 (60%) → 1.6 | range 3–13 · cùng curve | như Air |
| Gravity Modifier | 0.1 | 0.15 | **1.2** |
| Shape | Sphere r 0.1 | Cone góc **28°**, r 0.05, trục = hướng đòn | Cone góc 70°, r 0.2, hướng lên. Đặt tại y 0.05 |
| Collision (tuỳ chọn) | — | — | Plane đất, Bounce 0.3, Lifetime Loss 0.3. **Mặc định tắt** vì tốn chi phí |

Lớp phụ **C · Ember** (nếu dùng):
- Billboard · Size 0.08–0.3 m · Speed ×0.6 · Lifetime 0.6–1.2 s.
- **Noise** strength 0.5, frequency 1.5: tàn lửa bay lượn nhẹ.
- Khoảng 6–8 hạt.

Ngân sách: tối đa ~30 hạt (kèm Ember ~38), 1 texture 256×64.

---

## 4. Khung `component.json`

```json
{
  "id": "SPK_Ground_01",
  "role": "sparks",
  "context": "ground",
  "style": "streak",
  "technique": "particle",
  "blend": "add",
  "plane": "stretch",
  "envelope": { "peak": 0.1, "fadeStart": 0.6, "end": 1.0 },
  "end": "shrink",
  "colorSlots": ["Core", "Mid", "Outer"],
  "defaults": { "delay": 0, "duration": 0.6, "size": 1, "intensity": 1, "count": 20, "speed": 6 },
  "extra": { "gravity": 1.2, "ember": false, "collision": false },
  "budget": { "particles": 30, "samples": 1, "texture": 256 },
  "status": "draft"
}
```

---

## 5. Câu hỏi cho art lead

1. Kiểu mặc định: **A Streak**, **B Toon**, hay cả hai làm 2 biến thể (`_01` / `_02`)?
2. Có thêm lớp phụ **C Ember** (tàn lửa bay chậm) mặc định không?
3. `SPK_Ground`: có bật **Collision** (tia nảy trên đất) không, hay để tia rơi xuyên đất rồi tắt?
4. Số hạt ~20 có hợp mobile và tầm nhìn trong game không?
