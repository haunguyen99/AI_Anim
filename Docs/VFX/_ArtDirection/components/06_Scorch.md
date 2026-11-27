# Thành phần 06 — Scorch (vết cháy / vết nứt trên đất) · nháp v0 (2026-11-02)

> Trạng thái: **NHÁP.** Kiểu đã chọn: **C Burn + Cracks** (art lead, 2026-11-02).
> - Đã dựng `CMP_SCR_Ground_01` ở `Assets/VFX/_Components/Scorch/` (`ScorchComponentsBuild.BuildBatch`, dùng chung `CodeFxComponentsBuild.MakeFlipbook`).
> - Preview + GIF ở `Docs/VFX/_Components/Scorch/SCR_Ground_01/`. `Preview_combo` ghép cùng Impact + Glow + Ring + Sparks + Dust.
> - Hướng vết cố định (Body và Light phải trùng khớp nên chưa random xoay).
> Làm bằng **codefx** (`/vfx-maker` chế độ C): `codefx/scorch.py`. Ảnh so sánh sinh bằng `scripts/scorch_options.py`.

**Vai trò:** dấu vết để lại trên mặt đất sau cú trúng.
- Cho thấy **sức nóng và sức nặng** của đòn.
- Là lớp ở lại lâu nhất (khoảng 2 s): khi chớp, vòng sóng và tia lửa đã tắt, đất vẫn còn vết.
- Thời gian đầu còn nóng đỏ rồi nguội dần. Sau đó giữ một lúc, mờ và tan từ mép vào.

Ảnh các kiểu: [scorch_options.png](scorch_options.png).
- Nhìn từ trên xuống, trên nền màu đất, ở 6 mốc thời gian.
- Cột cuối mô phỏng góc camera 3/4: vết bị dẹt khoảng 0.64 lần.

---

## 0. Không gian (đã xác định từ chuẩn thành phần, không cần hỏi)

| Mục | Giá trị |
|---|---|
| Ngữ cảnh | **chỉ ground** (Air không có vết; Dir dùng chung, có thể kéo dài theo hướng sau) |
| Mặt phẳng | **nằm đất**: Billboard + Render Alignment Local, GameObject xoay X 90°, cao 0.01 m |
| Camera | 3/4 nhìn xuống 40° |
| Kích thước | ~2.6 m (bé hơn vòng Ring 4.5 m, khoảng bằng lớp Flat của Impact) |
| Neo | điểm trên đất (World) |
| Nền | đất nhiều màu nên dùng **Alpha** cho vết tối + lớp **Light** (Add) cho phần còn nóng |
| Thứ tự vẽ | Sorting **−2**: dưới Dust (−1), dưới mọi lớp sáng |

## 1. Kiểu (chọn 1 làm mặc định)

| Kiểu | Hình | Hợp với |
|---|---|---|
| **A · Burn (vết cháy)** | Nhiều lớp:<br>• quầng muội nhạt bên ngoài;<br>• mảng chính viền rách (2 tầng noise), gai dài ngắn khác nhau + 3 tia mảnh rải đều;<br>• 3 vòng tông;<br>• lõi hố có **mép sáng** (trên-trái) và **mép tối**;<br>• giọt bắn hình giọt nước toả ra ngoài + tro lấm tấm.<br>Lõi lúc đầu là than hồng: trắng → cam → đỏ → tối | Lửa, nổ, phép nóng |
| **B · Cracks (vết nứt)** | • 9 vết nứt chính, gần như thẳng, gãy nhẹ, thon nhọn; mỗi vết có **viền nhạt + lõi đen** (độ sâu);<br>• 0–2 nhánh mỗi vết;<br>• vết nứt ngang nối các vết thành mạng quanh hố;<br>• hố tối + 5–8 **đá vụn 2 tông** ở tâm.<br>Mọc trong 0.1 s, sáng theo nhiệt rồi nguội | Đập đất, đòn nặng, đá |
| **C · Burn + Cracks** | A nhạt hơn + B trên cùng | Đòn nặng có lửa (nổ lớn, thiên thạch) |

**v2 (2026-11-02):** art lead góp ý "shape hơi đơn giản quá", nên thêm các lớp chi tiết nêu trên. Đã sửa thêm 2 lỗi: vết nứt bị đốt khúc như đốt tre (giờ vẽ mọi viền trước rồi mới vẽ lõi), và tia dài dồn một góc trông như vết cào (giờ rải đều).

**Nhịp chung** (chạy đều trên mọi kiểu):
- hiện ra trong 0.08 s (ease `out_expo`);
- **nguội trong khoảng 0.7 s**: bậc nhiệt cứng trắng → vàng → cam → đỏ → tối, theo luật `drawCracks` của pixelfx;
- giữ nguyên;
- từ 55% thời lượng: mờ dần, và ăn mòn từ mép vào lõi (mép mềm);
- **tắt hẳn ở 2.0 s**.

Màu than và nứt dùng bộ **SOOT** (nâu đen) cố định, không nhuộm theo ô màu. Phần nóng lấy dải màu từ Core / Mid / Outer, nên đổi nguyên tố thì than đổi màu theo.

## 2. Thông số Particle System (dự kiến, 1 particle chạy cả flipbook)

- **Texture:**
  - `T_CFX_Scorch_Body_4x4.png` (Alpha) + `T_CFX_Scorch_Light_4x4.png` (Add);
  - 16 frame trên 2.0 s, ô 256 → sheet 1024.
- **Main:** Looping tắt · Start Lifetime 2.0 · Start Size 2.6 m · Start Rotation 0–360° (vết không lặp hướng) · Simulation World.
- **Emission:** Burst 1 tại 0 s. Tool mix đặt delay khoảng 0.02 s, ngay sau chớp.
- **Texture Sheet Animation:** 4×4, Frame over Time 0 → 1.
- **Renderer:** Billboard + Render Alignment **Local**, GameObject xoay X 90°, y 0.01 · Sorting −2 (Body), −1 (Light) · Max Particle Size 3.
- Build bằng `CodeFxComponentsBuild` (đọc `space` trong json: plane `ground` → nằm đất).

## 3. Khung `component.json`

```json
{
  "id": "SCR_Ground_01",
  "role": "scorch",
  "context": "ground",
  "style": "burn",
  "technique": "codefx-flipbook",
  "blend": "alpha+add",
  "plane": "ground",
  "envelope": { "peak": 0.05, "fadeStart": 0.55, "end": 1.0 },
  "end": "fade + erode rim->core",
  "colorSlots": ["Core", "Mid", "Outer"],
  "defaults": { "delay": 0.02, "duration": 2.0, "size": 2.6, "intensity": 1 },
  "extra": { "style": "burn|cracks|both", "cracks": 9 },
  "budget": { "particles": 2, "samples": 2, "texture": 1024 },
  "status": "draft"
}
```

## 4. Câu hỏi cho art lead

1. Kiểu mặc định: **A Burn**, **B Cracks**, hay **C Burn + Cracks**? Hoặc giữ cả 3 làm biến thể.
2. Thời gian vết ở lại: **2 s** có đủ không? Trong gameplay có thể cần lâu hơn, ví dụ 4–6 s.
3. Có cần bản **Dir** không? Vết cháy kéo dài theo hướng đòn, như vết trượt.
