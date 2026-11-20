# Ghép VFX từ thành phần chuẩn (auto mix + Mix Lab) — mục 9 SKILL.md

Tích hợp 2026-11-03 (art lead chốt). Chuẩn đầy đủ: [components/STANDARD.md](components/STANDARD.md). Spec từng thành phần: `components/01_Impact.md` … `05_Dust.md`.

## 1. Thư viện thành phần (project VFX_LIb)

| Nhóm | ID (Air / Dir / Ground) | Vai trò | Thứ tự vẽ |
|---|---|---|---|
| Impact | `IMP_Hit_*_01` | chớp trúng, frame hero | flat nằm đất −4 · chớp 5 · lõi 6 |
| Glow | `GLW_*_01` | quầng sáng nền | vũng đất −5 · quầng 0 / lõi 1 |
| Ring | `RNG_*_01` | vòng sóng xung kích | Ground −3 · Air/Dir 2 |
| Sparks | `SPK_*_01` | tia lửa (Streak + Ember) | 3 |
| Dust | `DST_*_01`, `DST_Fire_Ground_01`, `DST_FireSmoke_Ground_01` | khói bụi / cụm lửa / lửa → khói | khói −2 / lớp sáng −1 |

- Prefab ở `Assets/VFX/_Components/<Nhóm>/Prefabs/CMP_<ID>.prefab`. Build script ở `.../Editor/<Nhóm>ComponentsBuild.cs`.
- Nhóm Scorch, CodeFX (làm bằng codefx) và Lightning vẫn có trong project nhưng không thuộc skill: không đưa vào auto mix. Scorch −9/−8 và Lightning −7/4 vẫn giữ ô số thứ tự vẽ (bảng ở `ComponentKit`).
- Hàm dùng chung `ComponentKit.cs` (bản trong skill: `assets/components/_Kit/`):
  - ô màu Core / Mid / Outer / Dust;
  - `LinearFrames` (Frame over Time phải thẳng);
  - `GroundFlat`, `Save`, `Capture`.

**Luật bắt buộc khi ghép** (art lead):
- **Một effect = một ngữ cảnh** (Ground / Air / Dir) **+ một chớp va chạm**. Không trộn chớp khác hướng.
- **Thứ tự vẽ xếp theo mặt phẳng trước rồi mới tới độ sáng:** lớp nằm đất < khói đứng < lớp sáng < tia < chớp. Không có hai thành phần trùng số `sortingOrder`. Thành phần mới phải lấy một ô số còn trống trong bảng (ghi ở `ComponentKit`).
- Danh sách lớp (recipe, Mix Lab) xếp **lớp trước mặt ở trên cùng**, giống After Effects.
- Không dùng Horizontal / Vertical Billboard.

## 2. Auto mix (mặc định)

Art lead: "Claude tự mix thành phần theo thông tin ban đầu, có vấn đề tôi yêu cầu đổi."

1. **Không gian** (mục 1a): chưa rõ ngữ cảnh thì hỏi.
2. **Brief** → `python -I "D:/Game_prj/VFX_LIb/.claude/skills/vfx-maker/mix/auto_mix.py" <brief.json | -> --project <project>`
   ```json
   {"name": "IceSlam_Ground", "context": "ground", "element": "ice", "weight": "heavy", "smoke": "auto"}
   ```
   - `element`: fire / ice / poison / lightning / arcane / holy / physical. Mỗi nguyên tố có sẵn bảng màu.
   - Script in **lý do từng lớp** và ghi `Docs/VFX/_Recipes/<name>.json`.
3. **Dựng:**
   `Unity -batchmode -projectPath <project> -executeMethod VfxEffects.MixRecipeBuild.BuildBatch -recipe Docs/VFX/_Recipes/<name>.json`
   → `Assets/VFX/Mixes/<name>/Prefabs/VFX_<name>.prefab`, preview ở `Docs/VFX/<name>/`.
4. Xem preview, dựng lại Review Lab (mục 5b), rồi báo art lead **kèm lý do các lựa chọn**.
5. Art lead yêu cầu đổi thì sửa recipe hoặc brief rồi dựng lại. Luật nào bị sửa nhiều lần thì cập nhật vào `auto_mix.py`.

**Luật trong `auto_mix.py`:**
- luôn có: Chớp (0 s), Quầng (0 s), Tia (0.02 s);
- Vòng từ đòn vừa (0.03 s); đòn nặng thêm vòng vọng (0.13 s, 0.7×);
- khói: đòn nhẹ không có khói; lửa tại đất dùng lửa → khói; còn lại dùng khói bụi theo ngữ cảnh (0.05 s);
- không có vết đất (Scorch đã bỏ khỏi skill); brief có `mark` khác `auto`/`none` thì script báo lỗi;
- độ to: nhẹ 0.8 / vừa 1 / nặng 1.25; thời lượng: nhẹ ×0.85 / nặng ×1.15;
- trên không và có hướng: độ cao 1.1 m.

## 3. Recipe → Unity (`MixRecipeBuild.cs`)

| Trường | Áp vào |
|---|---|
| `id` | chép rồi unpack `CMP_<id>` |
| `delay` | cộng vào Start Delay (× speed) |
| `duration` | simulationSpeed = độ dài gốc / duration |
| `size` / `rotation` / `offset` | scale / xoay Y / vị trí (m) |
| `intensity` | nhân alpha |
| `palette` | thay đúng màu ô `ComponentKit` trong Start Color + gradient |

Màu chỉ đổi qua ô màu: thành phần phải tô bằng đúng màu ô `ComponentKit` (texture trắng–xám). Texture có màu vẽ sẵn thì palette không đổi được.

## 4. Mix Lab (xem / tinh chỉnh trên web)

- **Online:** https://claude.ai/artifact/CMFUvsBJ6YeqapsMZoNwbt
- **Nguồn:** `<project>/Docs/VFX/_ArtDirection/tools/mix_lab/`. Bản chép trong skill ở `mix/mix_lab.html`.
- **Tính năng:**
  - thành phần có tên tiếng Việt, lọc theo ngữ cảnh, kéo thả vào timeline;
  - thanh kéo có giải thích; nút độ cao Mặt đất / Ngang ngực / Ngang đầu;
  - preset bảng màu;
  - khoá một ngữ cảnh và một chớp, cảnh báo kèm nút dọn khi mix bị lẫn;
  - "Copy recipe" để art lead dán vào chat.
- **Dữ liệu web:**
  - Menu `VFX/Components/Mix Lab - Capture Data` (`MixCapture.cs`) chụp mỗi thành phần 30 fps từ 2 camera, **mỗi `sortingOrder` một sheet** (`data/<id>_<q|s>_o<order>.png`), kèm `mix_data.js`.
  - **Chụp lại sau mỗi lần thêm hoặc sửa thành phần**, rồi đăng lại trang + js + data, mỗi lần không quá ~35 file.

## 5. Thêm thành phần mới

1. Viết spec `components/NN_<Tên>.md`:
   - không gian;
   - đưa 2–3 kiểu bằng ảnh so sánh để art lead chọn;
   - thông số Particle System.
2. Viết build script `<Nhóm>ComponentsBuild.cs`. Dùng `ComponentKit`, lấy một ô số thứ tự vẽ còn trống, Frame over Time dùng `LinearFrames`.
3. Có preview + `Preview_combo` ghép với các thành phần cùng ngữ cảnh, rồi đưa lên Review Lab.
4. Chụp lại dữ liệu Mix Lab và cập nhật luật trong `auto_mix.py` nếu cần.
