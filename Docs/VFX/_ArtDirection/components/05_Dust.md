# Thành phần 05 — Dust (khói bụi sau va chạm) · nháp v0 (2026-11-02)

> Trạng thái: **NHÁP.** Kiểu đã chọn: **A Toon puff** (art lead, 2026-11-02).
> - Đã dựng thử 3 prefab `CMP_DST_Ground/Air/Dir_01` ở `Assets/VFX/_Components/Dust/` (`DustComponentsBuild.BuildBatch`).
> - Preview ở `Docs/VFX/_Components/Dust/<ID>/`. `Preview_combo` ghép cùng Impact + Glow + Ring + Sparks.
> - Texture `T_DST_ToonPuff_4x4` là **bản sao trung tính** của sheet SmokeStylized: sheet gốc ám tím và tối, nên tông được chuyển về xám rồi nâng sáng (bóng 0.45, sáng 1.0). Script: `scripts/dust_sheet.py`. Sheet gốc giữ nguyên.
> - Tạm theo đề xuất cho các câu chưa trả lời: ô màu **Dust `#CDBBA6`** (đã thêm vào `ComponentKit.Dust`), Ground chỉ có vòng cuộn ngang, 12 cụm.
> - Đã kiểm tra thứ tự vẽ: vòng Ring (Add) đi qua cụm bụi thì cộng sáng lên trên bụi, đúng ý.
> - Ảnh so sánh kiểu sinh bằng `scripts/dust_options.py` (mô phỏng 2D).
> - **Sửa 2026-11-02**: art lead góp ý "frame đầu khói không nên tách rời nhau". Đã sửa:
>   - sheet bắt đầu từ **frame 4** (Frame over Time 0.25 → 1), vì frame 0 của sheet nguồn chỉ chiếm ~16% ô;
>   - Ground radius 0.3 → **0.15**;
>   - Ground thêm lớp **Core**: 2 cụm 1.6–2.0 m ở tâm, bay 0.3–0.8 m/s.
>
>   Giờ lúc đầu khói là một khối liền rồi mới loang thành vòng. Ảnh trước/sau: [dust_start_fix.png](dust_start_fix.png).
> - **Sửa 2026-11-02 (2)**: thêm Color over Lifetime, alpha 1 → (45%) 1 → (80%) 0.45 → 0, cho cả Puffs và Core, để khói mờ dần về 0 thay vì chỉ thủng lỗ. Ảnh so sánh: [dust_fade_compare.png](dust_fade_compare.png).

**Vai trò:** cụm bụi/khói cuộn ra sau cú trúng. Dust là **lớp Alpha duy nhất** trong bộ Impact.
- Cho cú đánh có **trọng lượng** và kéo dài cảm giác dư âm (0.8–1.2 s) sau khi các lớp sáng đã tắt.
- Nằm **dưới** mọi lớp Add (Glow, Ring, Impact, Sparks). Lớp sáng phủ lên trên, bụi làm nền tối cho chúng nổi.
- Ra trễ hơn chớp một chút (0–0.08 s) và nở chậm dần.

Ảnh các kiểu: [dust_options.png](dust_options.png).

---

## 1. Kiểu khói (chọn 1 làm mặc định)

| Kiểu | Texture nguồn | Hình | Kết thúc | Hợp với |
|---|---|---|---|---|
| **A · Toon puff** | `Assets/VFX/SmokeStylized/Textures/T_SmokeStylized3D_Puff_4x4.png`: 16 frame bake từ shader cụm cầu (art lead đánh giá "tạm ổn" 2026-10-23). Phương án khác: `smoke_smoke04` (Shape Lab, 4×4) | Cụm thuỳ tròn, 2 tông sáng/tối, **tự nở + ăn mòn thủng lỗ** trong sheet | dissolve mép→lõi (có sẵn trong sheet) | Toon/anime, đồng bộ với Ring/Impact kiểu toon |
| **B · Soft** | `smoke_smoke_01…10` (Shape Lab, 1 frame mỗi ảnh, chọn random) | Mây mềm nhiều chi tiết, mép nhoè | fade | Bán thực, đất cát, nổ thật |
| **C · Toon phẳng** | `smoke_cloud_hardshadow` (Shape Lab, 2×2 biến thể) | Khối mây phẳng, viền bóng cứng, không chi tiết | shrink | Casual/chibi, rất sạch, nhẹ mắt |

> Phương án kỹ thuật khác: shader `VFX/FX/Smoke` (FireballImpact L4) ăn mòn bằng noise, 2 tông. Nhưng shader này tốn 2 sample, không đổi được hình theo Shape Lab, và **live nặng hơn** flipbook. Chỉ dùng khi cần tan mượt hơn sheet 16 frame.

**Quy tắc texture cho Alpha Blend** (khác Add):
- **RGB = tông** (sáng/bóng), **Alpha = hình**.
- Các ảnh Shape Lab đang ở dạng xám 1 kênh (L), nên khi đưa vào Unity phải tách:
  - **B:** alpha = L, RGB gần trắng.
  - **C:** alpha = vùng khác đen, RGB = L để giữ viền bóng.
- Sheet A đã có sẵn RGBA.

---

## 2. Chọn biến thể theo ngữ cảnh

| Biến thể | Khi nào | Hình chuyển động |
|---|---|---|
| `DST_Ground` | Chạm đất, đập đất, nổ dưới chân | **Vòng bụi cuộn ngang** ra xa tâm (≈ 2–3 m), hơi bốc lên. Đây là biến thể chính |
| `DST_Air` | Nổ giữa không | Cụm khói toả cầu chậm, trôi lên nhẹ |
| `DST_Dir` | Đòn có hướng | Bụi bị đẩy theo hướng đòn (nón 35°), cụm phía trước |

Mặt phẳng: **Billboard** (cụm khói quay về camera). Không dùng Horizontal Billboard. Nếu cần thêm lớp bụi nằm sát đất thì dùng Billboard + Local như Ring.

---

## 3. Thông số Particle System

Chung:
- **Main:** Looping tắt · Duration 1.2 · Simulation Space **World** · Start Rotation 0–360° · Start Color = ô màu **Dust** (xem câu hỏi 2).
- **Emission:** 2 burst: phần lớn tại 0 s, phần còn lại tại 0.06 s. Cụm ra lệch nhau một chút, không bật cùng lúc.
- **Limit Velocity over Lifetime:** **Drag 3**: bụi bắn ra nhanh rồi gần như đứng lại, đúng kiểu bụi.
- **Velocity over Lifetime:** Y +0.3…0.4 (bốc lên chậm).
- **Rotation over Lifetime:** ±20°/s (cuộn nhẹ).
- **Renderer:** Billboard · Max Particle Size 3 · Sorting **−1** (dưới Glow 0–1). Thứ tự: Scorch → **Dust** → Glow → Ring → Impact/Sparks.
- **Material:** Mobile/Particles/Alpha Blended.

| Module | `DST_Ground` | `DST_Air` | `DST_Dir` |
|---|---|---|---|
| Delay | 0.03 s | 0.03 s | 0.02 s |
| Số cụm (burst 0 s + 0.06 s) | 8 + 4 | 6 + 3 | 6 + 3 |
| Start Lifetime | 0.8–1.2 | 0.8–1.1 | 0.7–1.0 |
| Start Speed | 2.5–4.5 | 1.2–2.5 | 2.5–4.5 |
| Start Size | 1.2–1.8 m | 1.0–1.6 m | 1.0–1.5 m |
| Shape | **Circle** r 0.3 nằm ngang (xoay X 90°), toả theo bán kính, đặt y 0.15 | Sphere r 0.2 | Cone 35°, r 0.1, trục = hướng đòn |

Theo kiểu:

| | A Toon puff | B Soft | C Toon phẳng |
|---|---|---|---|
| Texture Sheet | Grid 4×4, Frame over Time 0 → 1 (sheet tự nở + tan) | 1 ảnh / atlas random frame | 2×2, random frame |
| Size over Lifetime | gần phẳng: 0.9 → 1.05 | 0.5 → 1.4 (ease-out) | 0.55 → 1.15 (25%) → 1 → 0 (40% cuối) |
| Color over Lifetime (alpha) | **1 tới 45% → 0.8 → 0 ở cuối** (art lead 2026-11-02: giảm opacity dần về 0, chạy cùng sheet tự tan) | 1 tới 30%, giảm về 0 | 1 suốt đời |

Ngân sách: tối đa 12 cụm (Ground). Khói Alpha to nên **overdraw** là chi phí chính trên mobile, vì vậy giữ số cụm thấp và Max Particle Size 3.

---

## 4. Khung `component.json`

```json
{
  "id": "DST_Ground_01",
  "role": "dust",
  "context": "ground",
  "style": "toon-puff",
  "technique": "particle-flipbook",
  "blend": "alpha",
  "plane": "billboard",
  "envelope": { "peak": 0.35, "fadeStart": 0.5, "end": 1.0 },
  "end": "dissolve-edge-to-core",
  "colorSlots": ["Dust"],
  "defaults": { "delay": 0.03, "duration": 1.2, "size": 1.5, "intensity": 1, "count": 12, "speed": 3.5 },
  "extra": { "rise": 0.35 },
  "budget": { "particles": 12, "samples": 1, "texture": 1024 },
  "status": "draft"
}
```

---

## 5. Câu hỏi cho art lead

1. Kiểu mặc định: **A Toon puff**, **B Soft**, hay **C Toon phẳng**?
2. **Màu:** thêm ô màu riêng **Dust** không? Đề xuất sáng `#CDBBA6` (nâu xám đất), tông bóng lấy từ texture. Hay để bụi ăn theo bảng nguyên tố, ví dụ lửa thì khói xám đen?
3. `DST_Ground`: chỉ **vòng bụi cuộn ngang**, hay thêm 1–2 cụm **bốc thẳng lên** ở tâm?
4. Số cụm (~12 ở Ground) và độ to (1.2–1.8 m) có ổn với tầm camera trong game không?

## 8. Biến thể lửa (2026-11-02) — CHUẨN

Art lead: "đổi màu phần khói xem có thể làm lửa từ khói không" (trên DST_Ground_01). Cùng hình, cùng chuyển động, cùng sheet; chỉ đổi màu và thêm lớp sáng:

| Biến thể | Lớp Alpha (Color over Lifetime) | Lớp phát sáng `_Glow` (Additive, cùng seed nên trùng khít) |
|---|---|---|
| `DST_Fire_Ground_01` | Core → Mid (25%) → Outer (60%) → mờ | Core → Mid → Outer, alpha 0.55 → 0.4 (45%) → 0 (85%) |
| `DST_FireSmoke_Ground_01` | Core → Mid (12%) → Outer (28%) → muội `#4A403A` (45%) → Dust (70%) → mờ | alpha 0.55 → 0.45 (15%) → 0 (32%): tắt đúng lúc lửa nguội thành khói |

- Không có lớp sáng thì bản lửa chỉ như khói màu cam (Alpha Blended không cộng sáng). Có lớp sáng thì lửa rực thật sự.
- Lớp sáng lúc đầu 0.85 làm cả cụm cháy trắng thành mảng, nên hạ xuống 0.55 để giữ thùy (luật "trắng chỉ ở lõi").
- Ảnh: [dust_fire_looks.png](dust_fire_looks.png) (chưa có sáng), [dust_fire_glow.png](dust_fire_glow.png) (có sáng).
- Build trong `DustComponentsBuild` (`Look.Fire` / `Look.FireSmoke`, hàm `AddGlow`).
- **Art lead chốt giữ cả hai làm biến thể chuẩn** (2026-11-02):
  - `DST_Fire_Ground_01` (lửa);
  - `DST_FireSmoke_Ground_01` (lửa → khói, cú nổ).
- Ô màu: lửa dùng Core / Mid / Outer (đổi nguyên tố theo bảng màu), khói nguội dùng muội + Dust.
- Ngân sách: gấp đôi số hạt của Dust thường (lớp Alpha + lớp Glow), tối đa khoảng 24 hạt, cùng 1 texture.
- `component.json`: thêm `"look": "dust" | "fire" | "fire2smoke"`; với 2 bản lửa, `blend` là `"alpha+add"`.
