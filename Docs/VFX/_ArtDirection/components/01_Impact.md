# Thành phần 01 — Impact (chớp va chạm) · nháp v0 (2026-10-31)

> Trạng thái: **NHÁP, chờ art lead duyệt.** Số liệu là đề xuất ban đầu, sẽ chỉnh sau khi xem preview.

**Vai trò:** khoảnh khắc trúng đòn. Người chơi phải đọc được "đã trúng, trúng ở đâu" trong 0.1–0.2 s. Đây là phần sáng và tương phản nhất của cả VFX. Các thành phần khác (glow, ring, sparks, bụi) chỉ phụ hoạ quanh nó.

Ảnh các shape: [impact_shapes.png](impact_shapes.png) (11 shape Impact trong thư viện Shape Lab).

---

## 1. Chọn biến thể theo ngữ cảnh

Hỏi 2 câu:
1. **Trúng vào đâu?** Vào người/vật/khiên giữa không trung → **Air**. Vào mặt đất (đập đất, đáp đất, đạn rơi xuống nền) → **Ground**.
2. **Đòn có hướng rõ không?** Có (chém, đâm, đấm, đạn bay ngang) → **Dir**. Không (nổ, phép nổ tại chỗ) → **Air**.

| Biến thể | Khi nào dùng | Hình dáng | Shape trong thư viện |
|---|---|---|---|
| `IMP_Hit_Air` | Trúng giữa không, không có hướng | Sao/nổ **toả đều** mọi phía, lõi đặc, gai nhọn | **Impact03** (2×2, 4 kiểu sao), **Impact07** (sao 7 gai), **Impact05** (sao lệch), lõi **Impact06** (sao 4 cánh có glow) |
| `IMP_Hit_Dir` | Đòn có hướng: chém, đâm, đấm | **Kéo dài theo hướng đòn**, đầu nhọn chỉ hướng lực, đuôi rách | **Impact08** (mũi nhọn), **Impact01** (2×2, chuỗi tan) |
| `IMP_Hit_Ground` | Chạm đất | Hai lớp: **bắn ngược lên** từ mặt đất (đứng, Stretched Billboard) + **toả tròn** sát đất (nằm, Billboard + Render Alignment Local/World) | Đứng: **Impact04** (chuỗi 8 frame bắn lên rồi tắt), **Impact02** (6×1, vệt đứng). Cả hai phải **xoay ngang** trước khi dùng (xem 2c). Nằm: **Impact09** (vành toả rỗng giữa), **Impact07** |
| *(đặc biệt)* `IMP_Hit_Bite` | Đòn cắn, kẹp | Hàm răng khép lại | **Biting** (2×1: mở → khép) |

**Vì sao Ground phải tách riêng:** hình sao toả đều đặt ở mặt đất sẽ có nửa dưới cắm xuống đất, trông như bị lơ lửng hoặc bị cắt. Chạm đất thì năng lượng chỉ thoát **lên trên và ra hai bên**. Vì vậy cần hình có đáy phẳng (Impact04) và một lớp nằm đất toả tròn.

**Với camera 3/4 nhìn xuống 40°:**
- Lớp nằm đất đọc rất rõ, còn lớp đứng trông thấp hơn thực tế. Vì vậy lớp đứng cần cao ~1.2× so với khi nhìn ngang.
- Lớp Air/Dir là billboard nên luôn đọc rõ.
- Lớp đứng dùng Stretched Billboard: quad xoay quanh trục dọc để quay về camera. Camera nhìn **thẳng từ trên xuống** (90°) thì lớp này bị dẹt hẳn. Game top-down thuần nên bỏ lớp đứng, hoặc thay bằng lớp nằm to hơn.

**Không dùng Horizontal Billboard / Vertical Billboard** (art lead, 2026-10-31): một số game không render các chế độ này. Thay bằng:
- **đứng thẳng:** Stretched Billboard;
- **nằm đất:** Billboard + Render Alignment **Local** hoặc **World**.

---

## 2. Thông số Particle System

Chung cho mọi biến thể:
- **Main:** Looping tắt · Play On Awake bật · Start Speed 0 · Gravity 0 · Simulation Space **Local** · Scaling Mode **Hierarchy** (tool mix phóng to được).
- **Emission:** Rate 0, chỉ dùng **Burst**.
- **Shape:** tắt (sinh tại tâm).
- **Material:** Additive (`Mobile/Particles/Additive`, hoặc `SH_VFX_Particle` của skill nếu cần HDR). Ô màu **Core**.
- **Renderer:** Max Particle Size **3** (mặc định 0.5 sẽ làm hình bị thu nhỏ khi lại gần camera). Order in Layer cao nhất trong VFX.
- **Nhịp kiểu anime:** bật lên gần như tức thì, giữ hình, rồi tắt gọn. Không fade mờ dần lâu.

### 2a. `IMP_Hit_Air`

| Module | Giá trị |
|---|---|
| Main | Duration 0.3 · Start Lifetime **0.12–0.18** · Start Size **1.6–2.0 m** · Start Rotation **0–360°** · Flip Rotation 0.5 · Max Particles 4 |
| Emission | Burst t=0: **1**. *(tuỳ chọn "nhịp đôi")* Burst t=0.04: 1, nhỏ hơn và xoay khác |
| Size over Lifetime | (0, 0.6) → (0.15, **1.05**) → (0.35, 1.0) → (1, 0.7) — nảy to rồi giữ |
| Color over Lifetime | Alpha 1 tới 60% đời, về 0 ở 100% |
| Texture Sheet Animation | Impact03: Grid 2×2 · **Start Frame ngẫu nhiên 0–3 · Frame over Time = 0** (4 ô là 4 kiểu, không phải chuỗi). Impact05/07: tắt |
| Renderer | Billboard |
| Lớp lõi (tuỳ chọn) | Particle thứ 2: Impact06, size 0.8 m, life 0.08 s, không xoay — làm chấm sáng chói giữa tâm |

### 2b. `IMP_Hit_Dir`

| Module | Giá trị |
|---|---|
| Main | Start Lifetime **0.15–0.2** · **3D Start Size** X **2.2** / Y **1.3** m (kéo dài theo hướng) · Start Rotation = **hướng đòn** (tham số `rotation`, do tool/gameplay đặt) **±10°** ngẫu nhiên · Max Particles 3 |
| Emission | Burst t=0: 1 |
| Size over Lifetime | Tách trục: X (0, 0.5) → (0.2, 1.1) → (1, 1.2) — vươn tiếp theo hướng; Y (0, 1) → (1, 0.5) — mỏng dần |
| Color over Lifetime | Alpha 1 tới 50%, về 0 ở 100% |
| Texture Sheet Animation | Impact01: Grid 2×2 · **Frame over Time 0 → 1** (chuỗi 4 frame: đặc → rách → vụn). Impact08: tắt |
| Renderer | Billboard · **Pivot X ≈ 0.3** (dời quad về phía trước: **gốc ở điểm trúng, đầu nhọn vươn theo hướng lực**; dấu kiểm bằng chấm đỏ trong preview) |
| Nét nhấn | **Không dùng.** Đã thử vệt Impact10 vuông góc rồi dọc theo hướng đòn; art lead bỏ hẳn (2026-10-31). Mũi nhọn tự mang hướng. |

### 2c. `IMP_Hit_Ground` (2 particle system trong cùng thành phần)

| Module | Lớp đứng `Splash` | Lớp nằm `Flat` |
|---|---|---|
| Render Mode | **Stretched Billboard** | **Billboard** · Render Alignment **Local** (mặc định) hoặc **World** |
| Main | Start Lifetime **0.4** · Start Size **1.2 m** bề ngang (×1.2 nếu camera 3/4) → cao = Size × Length Scale ≈ 2.9 m · Start Speed **0.05** (chỉ để có hướng, gần như đứng yên) · Max 2 | Start Lifetime **0.22** · Start Size **3 m** · Max 2 · Local: Start Rotation 0–360° (xoay quanh pháp tuyến mặt đất). World: bật **3D Start Rotation**, X = 90°, Y = 0–360° |
| Hướng | Shape: Cone, Angle **0**, Radius 0, xoay để trục bắn chỉ **+Y** (lên trời). Hướng bay = hướng kéo dài | Local: **xoay GameObject X = 90°** để quad nằm sát mặt phẳng. Thành phần sẽ nghiêng theo bề mặt nếu VFX được xoay theo pháp tuyến chỗ trúng (dốc, tường, khiên). World: luôn nằm ngang dù cha xoay thế nào |
| Emission | Burst t=0: 1 | Burst t=0: 1 |
| Size over Lifetime | (0, 0.8) → (0.2, 1.0) → (1, 1.05) | (0, 0.4) → (0.3, 1.0) → (1, 1.15) — toả ra |
| Color over Lifetime | Alpha 1 tới 80%, về 0 ở 100% | Alpha 1 tới 40%, về 0 ở 100% |
| Texture Sheet Animation | Sheet đã xoay ngang: **Grid 2×4 · Frame over Time 0 → 1** (8 frame ≈ 20 fps) | Impact09/07: tắt |
| Renderer | Speed Scale **0** · Length Scale **2** (ô 2:1; độ dài chỉ phụ thuộc Size, không theo tốc độ) · Freeform Stretching tắt · **Pivot (0, 1, 0)** → đáy chạm đất · Flip Y 0.5 (lật trái/phải ngẫu nhiên) | Vị trí cao 0.02 m trên mặt đất (tránh z-fighting) |

**Chuẩn texture cho Stretched Billboard (Unity):** đã kiểm chứng bằng bài thử ngày 2026-10-31 (`stretch_test.png`).
- Unity kéo dài quad theo **trục X (ngang) của texture**, nên texture phải **nằm ngang**.
- **Hướng bay = mép TRÁI của texture.** Vị trí hạt nằm ở mép trái, phần còn lại kéo dài ra phía sau (về bên phải ảnh).
  - Với lớp Splash bắn lên: **ngọn ở bên trái, đáy (mặt đất) ở bên phải**.
- **Pivot trong Stretched Billboard:**
  - Pivot X dời quad **sang ngang**.
  - Pivot Y dời quad **theo hướng bay**: Y × chiều dài quad.
  - Splash dùng **Pivot (0, 1, 0)** để đáy luôn chạm đất, kể cả khi quad đổi kích thước.
- **Độ dài quad** = Start Size × Length Scale. Ô sheet 256×128 (2:1) nên dùng Length Scale **2**; khi đó Start Size là **bề ngang** (1.2 m × 1.2 = 1.44 m, cao ~2.9 m).
- Impact04 gốc là ảnh đứng, 4×2 ô 128×256.
  - Không xoay nguyên tấm, vì thứ tự frame sẽ sai.
  - Phải **xoay từng frame 90° ngược chiều kim đồng hồ** (ngọn sang trái), rồi xếp lại thành sheet 2×4, ô 256×128, giữ thứ tự frame theo hàng.
  - Impact02 xử lý tương tự.
- Tên: `T_IMP_GroundSplash_2x4.png`. Shape Lab nên có nút "Xuất cho Stretched Billboard" làm việc này tự động.
- Lưu ý: shader `VFX/FX/Spark` (FireballImpact) đang ghi "đầu ở +X". Có thể bị ngược so với quy ước này, cần kiểm lại khi làm thành phần Sparks.
