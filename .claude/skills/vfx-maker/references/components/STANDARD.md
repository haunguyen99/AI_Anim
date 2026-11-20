# Chuẩn thành phần VFX (bản nháp v0 2026-10-31, chốt 2026-11-03)

> Trạng thái: **ĐÃ TÍCH HỢP vào `/vfx-maker`** (2.2.0, art lead chốt 2026-11-03). Bản trong skill: `references/components/`; bản làm việc trong project: `Docs/VFX/_ArtDirection/components/`.
> Từ 2.3.0 (2026-11-03) skill gồm 5 nhóm Impact / Glow / Ring / Sparks / Dust. Scorch và CodeFX (làm bằng codefx) đã bỏ khỏi skill; Lightning đang làm trong project, chưa vào skill. Các nhóm này vẫn giữ ô thứ tự vẽ trong bảng dưới để không trùng số.

Ý tưởng: không làm cả một VFX một lần nữa. Làm từng **thành phần** nhỏ (Flash, Ring, Sparks...), chuẩn hoá để thành phần nào cũng ghép được với thành phần nào. Sau đó dùng **tool mix** ghép lại thành VFX hoàn chỉnh.

Đã chốt (2026-10-31):
- Kỹ thuật: **cả hai**. Mỗi thành phần chọn cách hợp nhất (particle + texture, hoặc shader) nhưng dùng chung một bộ thông số chuẩn.
- Tool mix: **web + Unity**. Mix và xem trên web, xuất công thức JSON, Unity tự dựng prefab.
- Bắt đầu với: **Impact chung** (dùng được cho mọi nguyên tố).

---

## 1. Thành phần là gì

Một thành phần = **một vai trò thị giác**, ví dụ "chớp sáng lúc chạm" hay "vòng xung kích dưới đất".
- Gồm 1 Particle System (đôi khi 2–3 cái đi chung, ví dụ Flash = lõi + gai) và 1 material.
- Tự chạy được một mình, đặt ở gốc toạ độ (0,0,0) là đúng vị trí.
- Không tự biết mình nằm trong VFX nào. Thời điểm bắt đầu, độ to, màu do tool mix quyết định.

## 2. Chuẩn chung (mọi thành phần phải theo)

| Mục | Chuẩn |
|---|---|
| Kích thước | `size = 1` → lúc to nhất, thành phần rộng **1 m**. Tool mix nhân lên. |
| Thời lượng | Thời lượng chuẩn **1 s** (từ lúc sinh tới lúc tắt hẳn). Tool mix kéo dài/rút ngắn bằng `duration`. |
| Nhịp (envelope) | Mỗi thành phần ghi 3 mốc theo tỉ lệ 0–1: **đỉnh** (to/sáng nhất), **bắt đầu tan**, **tắt**. Tool mix dùng mốc "đỉnh" để canh các thành phần khớp nhau. |
| Màu | Texture/shader **trắng–xám**, không vẽ sẵn màu. Màu lấy từ **3 ô màu chung**: `Core` (sáng nhất) · `Mid` · `Outer` (tối/viền). Mỗi thành phần ghi nó dùng ô nào. Đổi bảng màu là cả VFX đổi theo nguyên tố. |
| Cường độ | `intensity = 1` là mặc định. Nó nhân độ sáng (Add) hoặc độ đục (Alpha). |
| Blend | Ghi rõ **Add** hoặc **Alpha**. Thứ tự vẽ: vết đất → khói (Alpha) → lửa/thân → Add sáng nhất trên cùng. |
| Thứ tự vẽ (sortingOrder, 2026-11-03) | **Xếp theo mặt phẳng trước, rồi mới tới độ sáng.** Mọi lớp nằm trên mặt đất phải ở dưới khối khói đứng, khói ở dưới lớp sáng. Không trùng số giữa các thành phần.<br>Bảng gốc nằm trong `ComponentKit.cs` (bản project là chuẩn).<br>• Nằm đất: *(Scorch thân −9 / sáng −8 · Lightning tia đất −7, chỉ có trong project)* · vũng sáng Glow −5 · Impact Flat −4 · Ring Ground −3.<br>• Đứng: Dust khói −2 / sáng (bản lửa) −1 · Glow quầng + halo 0 / lõi 1 · Ring Air/Dir 2 · Sparks 3 · *(Lightning tia 4, chỉ có trong project)*.<br>• Trước cùng: Impact chớp, splash, spike 5 / lõi 6. Mix Lab và recipe liệt kê lớp **trước mặt ở trên cùng** (như AE). |
| Một effect = một không gian | Mỗi VFX ghép chỉ dùng **một ngữ cảnh** (Ground / Air / Dir) và **một chớp va chạm** (art lead 2026-11-03: lỗi 2 chớp khác hướng trong cùng effect). Mix Lab và auto mix chặn việc trộn. |
| Mặt phẳng | Một trong:<br>• **Billboard**: quay về camera.<br>• **Ground**: nằm đất = Billboard + Render Alignment **Local** (mặc định, nghiêng theo bề mặt) hoặc **World**.<br>• **Stretch**: Stretched Billboard; cũng dùng cho mọi lớp **đứng thẳng**.<br>• **Mesh**.<br>**Không dùng Horizontal / Vertical Billboard**, vì một số game không render được (art lead, 2026-10-31). |
| Texture Stretch | Texture cho Stretched Billboard **nằm ngang**. **Hướng bay = mép TRÁI ảnh**; hạt nằm ở mép trái, quad kéo về phía sau. Pivot X = dời ngang, Pivot Y = dời theo hướng bay (× chiều dài). Sheet đứng phải xoay **từng frame** rồi xếp lại, không xoay nguyên tấm. Đã kiểm chứng 2026-10-31. |
| Hướng | +Y lên trời. Thành phần có hướng (bắn toả, vệt) lấy **+Z là hướng lực**. Tool mix xoay được. |
| Gốc | Tâm va chạm = gốc toạ độ. Thành phần Ground nằm ở y = 0.01. |
| Kết thúc | Ghi kiểu tan: `fade` · `shrink` · `dissolve mép→lõi` · `dissolve lõi→mép` · `thin` (mỏng dần). |
| Ngân sách | Ghi số particle tối đa, số texture sample (shader), kích thước texture (≤ 512, sheet ≤ 1024). |
| Ngẫu nhiên | Có `seed`. Cùng seed thì preview giống hệt nhau, để so sánh A/B. |

### Thông số mọi thành phần đều có (tool mix chỉnh được)

`delay` · `duration` · `size` · `intensity` · `colorSlots` · `count` (số hạt, nếu có) · `spread` (độ toả) · `speed` · `rotation` · `seed`.

Thành phần có thể thêm thông số riêng. Ví dụ Ring có `width`, Sparks có `gravity`. Tối đa 3 thông số riêng để tool không rối.

### Preview chuẩn (để so sánh được với nhau)

- 2 góc: **3/4 nhìn xuống 40°** (góc game) và **ngang**.
- Nền tối, có lưới 1 m và hình người cao 2 m làm thước.
- Bảng màu mặc định: lửa cam (Core `#FFF3C4`, Mid `#FF9A3C`, Outer `#C8281E`).
- Xuất: GIF 24 fps + sheet 8 mốc + ảnh lúc đỉnh.

## 3. Gói một thành phần

```
Assets/VFX/_Components/Impact/IMP_Flash_01/
   CMP_IMP_Flash_01.prefab
   M_IMP_Flash_01_Add.mat
   Textures/ (nếu có)
Docs/VFX/_Components/Impact/IMP_Flash_01/
   component.json      ← thông số chuẩn, tool mix đọc file này
   preview.gif, preview_sheet.png, peak.png
```

Tên: `IMP_<Vai trò>_<số biến thể>`. Biến thể = cùng vai trò, khác hình/kiểu (Flash_01 tròn, Flash_02 đa gai).

`component.json` mẫu:

```json
{
  "id": "IMP_Flash_02",
  "role": "flash",
  "group": "impact",
  "technique": "particle",
  "blend": "add",
  "plane": "billboard",
  "envelope": { "peak": 0.15, "fadeStart": 0.3, "end": 1.0 },
  "end": "shrink",
  "colorSlots": ["Core"],
  "defaults": { "delay": 0, "duration": 0.15, "size": 3, "intensity": 1.5, "count": 1 },
  "extra": { "spikes": { "min": 4, "max": 10, "default": 7 } },
  "budget": { "particles": 2, "samples": 1, "texture": 512 },
  "status": "draft"
}
```

`status`: `draft` → `review` → `approved`. Tool mix chỉ hiện `approved` (có nút xem cả bản `draft`).

## 4. Danh mục Impact v1 (đề xuất)

| ID | Vai trò | Mặc định (delay / dài / to) | Mặt phẳng · Blend | Kỹ thuật & nguồn có sẵn | Kết thúc |
|---|---|---|---|---|---|
| `IMP_Hit` → [01_Impact.md](01_Impact.md) | Chớp va chạm, đọc được là "trúng". Biến thể **Air / Dir / Ground** (+ Bite) | 0 / 0.12–0.4 s / 1.8–3 m | Billboard / Ground: Stretch (splash đứng) + Billboard+Local (flat nằm) · Add | Particle + shape Impact01–10, Biting (Shape Lab) | shrink |
| `GLW` → [02_Glow.md](02_Glow.md) | Quầng sáng sau chớp, làm nền. Biến thể **Air / Dir / Ground** (vũng sáng nằm đất) | 0 / 0.35–0.5 s / 3.5–4 m | Billboard / Billboard+Local (Ground) · Add | Particle + texture glow (Soft có sẵn, Toon mới) | shrink (toon) / fade (soft) |
| `RNG` → [03_Ring.md](03_Ring.md) | Vòng xung kích nở ra xa. Biến thể **Ground / Air / Dir** (vòng phá âm) | 0.02 / 0.25–0.45 s / 2.5–4.5 m | Billboard+Local (Ground, Dir) / Billboard · Add | Flipbook 4×2 sinh bằng script (đề xuất), hoặc shader `VFX/FX/Blast` `_RING_ONLY` | thin + fade |
| `SPK` → [04_Sparks.md](04_Sparks.md) | Tia lửa bắn toả. Biến thể **Air / Dir / Ground** (+ lớp phụ Ember) | 0 / 0.4–0.6 s / toả 2–4 m | Stretch · Add | Particle + texture `T_SPK_*` sinh bằng script (shader `VFX/FX/Spark` có thể ngược đầu) | shrink |
| `DST` → [05_Dust.md](05_Dust.md) | Khói bụi cuộn ra sau va chạm. Biến thể **Ground / Air / Dir**, thêm 2 bản lửa (Ground): **Fire** và **FireSmoke** (lửa → khói, có lớp phát sáng Add) | 0.03 / 0.8–1.2 s / 1.2–1.8 m mỗi cụm, toả 2–3 m | Billboard · Alpha · Sorting −2 (khói) / −1 (lớp sáng bản lửa) | Particle + sheet: Toon puff 4×4 (SmokeStylized), smoke_smoke_0x, hoặc cloud_hardshadow (Shape Lab) | dissolve mép→lõi / fade / shrink theo kiểu |
| `IMP_Debris` | Mảnh vụn văng, có trọng lực | 0 / 0.9 s / toả 3 m | Billboard · Alpha | Particle + shape vụn | shrink · *tuỳ chọn* (Explosion đã bỏ) |

**Flipbook:** luật art lead vẫn giữ (flipbook chỉ cho khói, lửa, điện; loop 4×2, không loop 4×4). Chuỗi frame của Impact01 / Impact04 (Impact) và vòng 4×2 (Ring) có trước luật: là **ngoại lệ cần làm lại** khi sửa thành phần đó.

**Cách làm (art lead, 2026-10-31): đi từng thành phần một.**
- Mỗi thành phần có file spec riêng `NN_<Tên>.md` trong thư mục này. File gồm:
  - ngữ cảnh dùng (trên không / tại đất / có hướng...) → chọn shape;
  - hình dáng;
  - thông số Particle System theo từng module;
  - câu hỏi cho art lead.
- Duyệt xong thành phần này mới sang thành phần kế.

Thứ tự: 01 Impact → 02 Glow → 03 Ring → 04 Sparks → 05 Dust → (Debris).

## 5. Tool mix — ĐÃ LÀM: Mix Lab v1 (2026-11-02), xem `tools/mix_lab/README.md`

- **Web:**
  - Danh sách thành phần bên trái.
  - Timeline giữa: mỗi thành phần một track, kéo để đổi `delay`, kéo mép để đổi `duration`.
  - Khung preview ghép, chọn được 2 góc camera.
  - Bảng màu 3 ô.
  - Thông số của track đang chọn bên phải.
  - Preview trên web dùng GIF/sheet của từng thành phần, chỉ gần đúng. Bản chính xác do Unity dựng.
- **Xuất:** `recipe.json` gồm tên VFX, bảng màu và danh sách `{id, delay, duration, size, intensity, rotation, offset, extra}`.
- **Unity:** menu `VFX/Components/Build From Recipe` đọc recipe → copy prefab thành phần, áp thông số → lưu prefab VFX + preview → Review Lab.

## 6. Quy trình làm 1 thành phần

1. Chọn vai trò + biến thể trong danh mục.
2. Làm hình: Shape Lab / script / shader có sẵn (kiểm tra `Docs/VFX/SHADERS.md` trước).
3. Build prefab thành phần theo chuẩn mục 2, ghi `component.json`.
4. Xuất preview chuẩn → Review Lab.
5. Art lead duyệt → `status: approved` → vào thư viện.

## 7. Câu hỏi của bản nháp v0 (tình trạng 2026-11-03)

- Ô màu riêng cho khói/bụi: **đã có** (ô `Dust`).
- Làm thử 3 thành phần đầu: **đã làm** đủ 01–05.
- `IMP_Debris`: giữ ở dạng *tuỳ chọn*, chưa làm.
- Thời lượng chuẩn 1 s và kích thước chuẩn 1 m: **chưa ghi câu trả lời**. Thực tế các thành phần đang dùng thời lượng / kích thước thật của từng vai trò (bảng mục 4), Mix chỉnh bằng `duration` / `size`. Hỏi art lead khi cần chốt.
