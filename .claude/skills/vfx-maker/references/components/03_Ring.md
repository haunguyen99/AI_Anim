# Thành phần 03 — Ring (vòng xung kích) · nháp v0 (2026-11-02)

> Trạng thái: **NHÁP.** Kiểu đã chọn: **B · Sóng xung kích** (art lead, 2026-11-02).
> - Đã dựng thử 3 prefab ở `Assets/VFX/_Components/Ring/`.
> - Preview ở `Docs/VFX/_Components/Ring/<ID>/`, có `Preview_combo` ghép cùng Impact + Glow.
> - Sheet sinh bằng `scripts/ring_sheet.py` (`--thick 1.5` cho Dir).

**Vai trò:** một vòng mảnh nở nhanh ra xa điểm trúng. Ring cho người chơi thấy **sức lan và vùng ảnh hưởng** của đòn.
- Là điểm nhấn phụ: sáng nhưng **mảnh**, không che Impact.
- Đi xa hơn mọi thành phần khác (4–5 m) và tắt khi vươn tới mép.

**Khác với lớp Flat của Impact Ground:**
- Flat là hình toả đặc ngay tâm (Impact09), to khoảng 3 m, sống 0.2 s.
- Ring chỉ là **một đường viền** chạy ra xa và vẫn còn sau khi Flat đã tắt.
- Hai lớp dùng chung được, không trùng vai.

Ảnh các kiểu: [ring_options.png](ring_options.png), 8 frame nở vòng cho mỗi kiểu.

---

## 1. Kiểu vòng (chọn 1 làm mặc định)

| Kiểu | Hình | Hợp với |
|---|---|---|
| **A · Nét mảnh** | Một đường tròn sắc, mỏng dần khi nở | Gọn, đòn nhanh, effect nhỏ |
| **B · Sóng xung kích** | Viền sáng + lòng mờ dần vào trong (vệt sóng đi qua) | Nổ, đập đất, đòn nặng |
| **C · Toon đứt đoạn** | Vòng méo nhẹ, đứt thành nhiều đoạn dày mỏng khác nhau | Anime; tránh hình tròn đều (shape-language) |

## 2. Cách cho vòng nở (quan trọng)

Nếu chỉ phóng to texture vòng (Size over Lifetime), nét vòng cũng **dày lên** theo tỉ lệ: vòng 4 m có nét dày gấp 10 lần lúc 0.4 m, trông như cái đĩa. Có 3 cách:

| Cách | Mô tả | Chi phí | Ghi chú |
|---|---|---|---|
| **1 · Flipbook** *(đề xuất)* | Sheet 4×2: mỗi frame là vòng to hơn **trong cùng một ô**. Quad giữ cố định = đường kính lớn nhất. Độ dày nét điều khiển từng frame. | 1 sample | Nét đúng ý muốn, nhẹ cho mobile, sinh bằng script, chỉnh được trong Shape Lab |
| 2 · Shader `VFX/FX/Blast` + `_RING_ONLY` | Đã có trong project (FireballImpact L3). Vòng vẽ bằng toán, nét đều tuyệt đối | 2 sample + Custom Data | Không có kiểu đứt đoạn (C); cần custom vertex stream |
| 3 · Phóng to texture | Size over Lifetime 0.1 → 1 | 1 sample | Chỉ dùng cho vòng rất ngắn (< 1.5 m), vì nét sẽ dày lên |

Sheet flipbook:
- `T_RNG_<Kiểu>_4x2.png`, 1024×512 (ô 256), trắng–xám.
- Bán kính trong ô tăng kiểu **ease-out**: nhanh lúc đầu, chậm dần.
- Nét mỏng dần, 2 frame cuối mờ đi.
- Vòng chạm mép ô ở frame cuối (phủ ~92%).

---

## 3. Chọn biến thể theo ngữ cảnh

| Biến thể | Khi nào | Mặt phẳng |
|---|---|---|
| `RNG_Ground` | Chạm đất, đập đất, nổ dưới chân | **Nằm đất**: Billboard + Render Alignment **Local**, GameObject xoay X 90°, cao 0.03 m |
| `RNG_Air` | Nổ giữa không, phép toả cầu | **Quay về camera**: Billboard (View) |
| `RNG_Dir` | Đòn có hướng mạnh (đâm, bắn, đấm xuyên) | Billboard + Render Alignment Local, vòng **nghiêng ~50°** so với hướng đòn (không vuông góc hẳn), kiểu "vòng phá âm" |

**Với camera 3/4 nhìn xuống 40°:**
- Vòng Ground hiện thành bầu dục dẹt khoảng 0.64 lần. Như vậy là đúng, vì mắt đọc là vòng trên mặt đất.
- Vòng Dir: nếu vuông góc hẳn (90°) với đòn đi ngang thì camera nhìn thấy từ cạnh, vòng thành **một vạch dọc**. Lỗi này giống nét nhấn đã bị bỏ ở Impact (đã thử 2026-11-02).
  - Vì vậy vòng xoay **50°** thay vì 90°, nghiêng về phía camera, hiện thành bầu dục bao quanh mũi nhọn.
  - Nét dày hơn 1.5× (sheet `T_RNG_ShockThick_4x2`).
  - Trong game, góc nghiêng nên tính theo camera: pháp tuyến vòng = hướng đòn trộn với hướng nhìn camera.

---

## 4. Thông số Particle System (theo cách 1 · Flipbook)

Chung:
- **Main:** Looping tắt · Start Speed 0 · Gravity 0 · Simulation Space Local · Scaling Mode Hierarchy.
- **Emission:** Burst 1.
- **Shape:** tắt.
- **Material:** Additive · màu ô **Mid** (vòng sáng ấm). Kiểu A/C có thể dùng **Core** nếu cần nổi hơn.
- **Texture Sheet Animation:** Grid 4×2 · Frame over Time 0 → 1 (đường thẳng, `LinearFrames`) · Cycle 1.
  - **Ngoại lệ luật flipbook** (art lead: flipbook chỉ cho khói, lửa, điện; loop 4×2, không loop 4×4): chuỗi frame này có trước luật, cần làm lại theo luật (texture đơn + module particle) khi sửa thành phần.
- **Renderer:** Max Particle Size 3 · Sorting **2** (Air / Dir: trên Glow 0–1, dưới Sparks 3 và Impact 5–6) · **−3** (Ground: lớp nằm đất, dưới khói Dust).
- **Kết thúc:** nét mỏng dần trong sheet + alpha giảm ở 25% cuối.

| Module | `RNG_Ground` | `RNG_Air` | `RNG_Dir` |
|---|---|---|---|
| Delay | 0.02 s (ngay sau chớp) | 0.02 s | 0 |
| Start Lifetime | **0.45** | 0.3 | 0.25 |
| Start Size (đường kính lớn nhất) | **4.5 m** | 3.5 m | 2.5 m |
| Start Rotation | 0–360° (Local, quanh pháp tuyến) | 0–360° | 0–360° |
| Size over Lifetime | (0, 0.9) → (1, 1.0) — chỉ nhích nhẹ, sheet lo phần nở | như Ground | như Ground |
| Color over Lifetime | alpha 1 tới 75%, về 0 ở 100% | như Ground | như Ground |
| Vị trí / xoay | y 0.03 · xoay X 90° | tại điểm trúng | dời **0.3 m** về phía trước theo hướng đòn · xoay Y **50°** khi hướng đòn = +X (90° bị nhìn từ cạnh) |
| Vòng vọng (tuỳ chọn) | Hạt thứ 2: delay 0.08 s, size 0.7×, alpha 0.6 | — | Hạt thứ 2: delay 0.05 s, dời thêm 0.4 m, size 0.8× |

---

## 5. Khung `component.json`

```json
{
  "id": "RNG_Ground_01",
  "role": "ring",
  "context": "ground",
  "style": "shockwave",
  "technique": "particle-flipbook",
  "blend": "add",
  "plane": "ground",
  "envelope": { "peak": 0.3, "fadeStart": 0.75, "end": 1.0 },
  "end": "thin+fade",
  "colorSlots": ["Mid"],
  "defaults": { "delay": 0.02, "duration": 0.45, "size": 4.5, "intensity": 1 },
  "extra": { "echo": false },
  "budget": { "particles": 2, "samples": 1, "texture": 1024 },
  "status": "draft"
}
```

---

## 6. Câu hỏi cho art lead

1. ~~Kiểu mặc định~~ → đã chọn **B**.
2. Cách nở: **Flipbook** (đề xuất), hay dùng lại shader Blast?
3. Có làm **vòng vọng** (vòng thứ 2 trễ hơn) mặc định không?
4. `RNG_Dir` (vòng phá âm vuông góc hướng đòn) có cần không, hay chỉ Ground + Air?
5. Ground 4.5 m (≈ 2.2 người) có hợp tầm đòn trong game không?

## 7. Ghi chú kỹ thuật (2026-11-02)

- **Thân sóng** (bức tường sáng sau viền) là thứ làm nên chất "sóng xung kích".
  - Bản đầu quá nhạt (~45%), nhìn chỉ như nét mảnh.
  - Giờ thân sóng dài ≈ 55% → 25% bán kính, sáng tới 90%.
- **Texture cho material Additive phải để RGB trắng, hình nằm ở alpha.** `Mobile/Particles/Additive` nhân màu với alpha (Blend SrcAlpha One). Nếu lưu hình vào cả RGB lẫn alpha thì độ sáng **bị bình phương**: 45% hiện ra chỉ còn ~20%.
