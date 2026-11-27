# Thành phần 02 — Glow (quầng sáng) · nháp v0 (2026-10-31)

> Trạng thái: **NHÁP.** Kiểu mặc định đã chọn: A Soft. Đã dựng thử 3 prefab (2026-10-31): `Assets/VFX/_Components/Glow/`. Preview ở `Docs/VFX/_Components/Glow/<ID>/`; `Preview_combo.png` là ảnh ghép cùng Impact tương ứng.

**Vai trò:** quầng sáng sau chớp va chạm. Glow làm nền: chiếu sáng vùng quanh điểm trúng, nối các thành phần lại thành một khối và cho cảm giác "nóng/mạnh".
- Glow **không phải hình chính**. So với Impact, nó to hơn, sống lâu hơn và **tương phản thấp hơn**.
- Nếu Glow sáng bằng Impact thì hình chớp bị chìm và cả VFX thành một đốm trắng.

Ảnh các kiểu texture: [glow_options.png](glow_options.png). Hàng trên là texture, hàng dưới là texture đã tô màu Mid trên nền tối.

---

## 1. Kiểu texture (chọn 1 làm mặc định)

| Kiểu | Hình | Hợp với | Nguồn |
|---|---|---|---|
| **A · Soft** | Mờ dần đều (gaussian), không có mép | Bán thực tế, ánh sáng dịu | Đã có `T_Glow_Soft` (script `glow`) |
| **B · FatDot** | Lõi tròn cứng + viền mềm ngắn | Chấm sáng nhỏ, đạn, lõi | Đã có `T_Glow_FatDot` |
| **C · Toon 3 vệt tròn** | 3 bậc sáng rõ ràng (lõi / giữa / ngoài), mép sắc | Anime/cel-shaded, đồng bộ với lửa 1 tông | Mới, sinh bằng script |
| **D · Toon 3 vệt méo** | Như C nhưng mép **méo nhẹ, không tròn đều** | Anime, tránh hình tròn đều (quy tắc shape-language) | Mới, sinh bằng script |

**Đã chọn mặc định: A · Soft** (art lead, 2026-10-31).
- Kết thúc bằng **fade**.
- Texture `T_GLW_Soft.png` 256 px, phủ 77% ô.
- C/D (toon) giữ làm biến thể sau này.

**Quy tắc texture glow:**
- Hình phủ 75–85% ô (đuôi mờ cần chỗ).
- Trắng–xám, không vẽ màu.
- Toon: 3 bậc sáng ≈ **1.0 / 0.55 / 0.25**, bán kính ≈ **0.3 / 0.55 / 0.85**.

## 2. Hai lớp màu trong một Glow

Material Additive chỉ tô được 1 màu, nên Glow gồm **2 particle** để có chuyển màu theo bảng 3 ô:

| Lớp | Màu | To | Ghi chú |
|---|---|---|---|
| `Outer` | ô **Mid** (cam), alpha ≤ 0.6 | 100% | Quầng lớn |
| `Inner` | ô **Core** (vàng nhạt) | ~40% | Lõi nóng; tắt sớm hơn Outer |

Không dùng ô Core cho lớp lớn, vì Additive chồng lên Impact sẽ cháy trắng.

---

## 3. Chọn biến thể theo ngữ cảnh

Giống Impact: hỏi **trúng vào đâu** và **có hướng không**. Thường dùng cùng biến thể với Impact đi kèm.

| Biến thể | Khi nào | Hình dáng |
|---|---|---|
| `GLW_Air` | Trúng giữa không, không hướng | Quầng tròn (méo nhẹ) quanh điểm trúng, quay về camera |
| `GLW_Dir` | Đòn có hướng | Quầng **bầu dục kéo dài theo hướng đòn**, lệch nhẹ về phía trước |
| `GLW_Ground` | Chạm đất | **Vũng sáng nằm trên mặt đất** (ánh sáng hắt xuống nền) + quầng nhỏ đứng ở chân splash |

Vì sao Ground cần vũng sáng nằm:
- Chạm đất thì mắt đọc "mặt đất sáng lên".
- Quầng tròn quay về camera đặt ở mặt đất bị cắt nửa dưới, giống lỗi của hình sao ở Impact.

---

## 4. Thông số Particle System

Chung:
- **Main:** Looping tắt · Start Speed 0 · Gravity 0 · Simulation Space Local · Scaling Mode Hierarchy.
- **Emission:** Burst t=0: 1.
- **Shape:** tắt.
- **Material:** Additive.
- **Renderer:**
  - Max Particle Size **2** (glow to, gần camera dễ phủ cả màn hình, tốn overdraw).
  - Sorting **dưới** Impact: Outer 0, Inner 1. Impact dùng 2–3.
- **Kết thúc:**
  - Toon (C/D): **shrink**, nhỏ dần và giữ mép sắc. Fade alpha làm các vệt bị đục.
  - Soft (A): **fade**.
- **Mobile:** mỗi lớp chỉ **1 hạt**. Glow to nên overdraw lớn; không burst nhiều hạt glow.

### 4a. `GLW_Air`

| Module | `Outer` | `Inner` |
|---|---|---|
| Main | Start Lifetime **0.35** · Start Size **3.5 m** (≈ 2× Impact) · Start Rotation 0–360° · màu Mid, alpha 0.6 | Start Lifetime **0.2** · Start Size **1.4 m** · Start Rotation 0–360° · màu Core |
| Size over Lifetime | Toon: (0, 0.5) → (0.12, 1.0) → (0.5, 0.95) → (1, 0) · Soft: (0, 0.5) → (0.15, 1) → (1, 1.15) | (0, 0.6) → (0.15, 1) → (1, 0) |
| Color over Lifetime | Toon: alpha 1 tới 90%, về 0 ở 100% · Soft: (0, 0) → (0.05, 1) → (0.3, 0.8) → (1, 0) | alpha 1 tới 80%, về 0 ở 100% |
| Renderer | Billboard | Billboard |

### 4b. `GLW_Dir`

Như Air, khác ở:
- **3D Start Size** Outer: X **4.0** / Y **2.4** m. Inner: X 1.8 / Y 1.1 m.
- **Start Rotation** = hướng đòn (tham số `rotation`, cùng giá trị với Impact Dir), không ngẫu nhiên.
- Renderer **Pivot X ≈ 0.15**: dời quầng về phía trước theo hướng lực (lệch cùng phía mũi nhọn Impact Dir).

### 4c. `GLW_Ground`

| Module | `Pool` (nằm đất) | `Halo` (đứng, tuỳ chọn) |
|---|---|---|
| Render | **Billboard + Render Alignment Local**, GameObject xoay X 90°, cao 0.02 m (giống Impact Flat) | Billboard, tâm cao 0.5 m |
| Main | Start Lifetime **0.5** (ánh sáng trên nền đọng lâu hơn) · Start Size **4 m** · Start Rotation 0–360° · màu Mid, alpha 0.5 | Start Lifetime 0.25 · Start Size 2 m · màu Mid, alpha 0.5 |
| Size over Lifetime | (0, 0.4) → (0.15, 1.0) → (1, 1.1); toon: kết thúc (1, 0) | (0, 0.6) → (0.15, 1) → (1, 0) |
| Color over Lifetime | (0, 0) → (0.05, 0.8) → (0.4, 0.5) → (1, 0) | alpha 1 tới 70%, về 0 ở 100% |

Halo không dùng lõi Inner riêng: lõi nóng đã có ở Splash của Impact Ground.

---

## 5. Khung `component.json`

```json
{
  "id": "GLW_Air_01",
  "role": "glow",
  "context": "air",
  "style": "soft",
  "technique": "particle",
  "blend": "add",
  "plane": "billboard",
  "envelope": { "peak": 0.12, "fadeStart": 0.5, "end": 1.0 },
  "end": "fade",
  "colorSlots": ["Mid", "Core"],
  "defaults": { "delay": 0, "duration": 0.35, "size": 3.5, "intensity": 0.6 },
  "extra": { "inner": true },
  "budget": { "particles": 2, "samples": 1, "texture": 256 },
  "status": "draft"
}
```

Texture glow chỉ cần **256** (hình mềm/đơn giản, không cần 512).

---

## 6. Câu hỏi cho art lead

1. ~~Kiểu mặc định~~ → đã chọn **A Soft**.
2. Có cần lớp **Inner** (lõi màu Core) không, hay để Impact lo phần lõi?
3. Ground: vũng sáng nằm đất **+ Halo đứng**, hay chỉ vũng sáng?
4. Kích thước Glow ≈ 2× Impact (3.5 m) có hợp không?
5. Glow là thành phần riêng (tool mix tự chọn có/không), hay luôn đi kèm Impact?
