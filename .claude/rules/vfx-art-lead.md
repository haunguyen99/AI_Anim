# Luật art lead (luôn áp dụng)

Đây là luật đã chốt. Luật art lead thắng mọi nguồn nghiên cứu / thư viện. Thêm luật mới vào skill chỉ khi art lead nói "chốt".

## Không gian (mọi VFX, kể cả bằng code)
- Chốt không gian trước khi viết code: ngữ cảnh (air / ground / dir), mặt phẳng, camera (mặc định 3/4, nhìn xuống 40°), quy mô (m, so với nhân vật 2 m), neo, nền, timing.
- Brief thiếu thông tin thì **hỏi** (≤ 2 vòng, không hỏi lại điều đã nói, đánh dấu phần mình đoán là *đề xuất*).
- **Không dùng Horizontal / Vertical Billboard.**
  - Dựng đứng: Stretched Billboard, texture nằm ngang, hướng bay = mép TRÁI.
  - Tia / vệt có Speed Scale > 0: pivot (0,1,0).
  - Nằm đất: Billboard + Render Alignment Local (GameObject xoay X 90°) hoặc World.

## Mix thành phần (đòn trúng / nổ)
- Claude **tự mix** bằng `auto_mix.py` từ brief, báo lý do từng lớp. Art lead yêu cầu đổi sau.
- Một effect: **một ngữ cảnh, một chớp Impact**.
- `sortingOrder` không trùng, theo mặt phẳng trước rồi tới độ sáng (bảng ở `ComponentKit`).

## Texture (2026-11-04)
- Mọi skill, khi cần texture: lấy từ **`Assets/Library/`** trước. Cây chia theo vai trò `<nhóm>/<vai trò>/<nhóm>_<vai trò>_NNN` (art lead 2026-11-09); chọn theo `Docs/VFX/_Library/LIBRARY.md`, nguồn ở `library_index.csv`.
- Xem ảnh rồi mới chọn. Chỉ tạo texture mới khi Library không có hình hợp, và nói lý do.
- **Quy trình chọn (2026-11-10, bắt buộc; chi tiết ở `LIBRARY.md` mục "Luật chọn")**: (1) viết yêu cầu của thành phần (hình, đứng/nằm, blend, đơn/sheet, xám/màu) → (2) tra bảng `LIBRARY.md` ra thư mục → (3) **xem cả thư mục bằng contact sheet** (`python -I tools/library_props.py --contact <nhóm>/<vai trò>`, rồi Read PNG), tên thư mục không đảm bảo vai trò từng ảnh → (4) lọc theo `library_props.csv` (kind / color / edge_touch / warn) → (5) chốt 1 ảnh + 1–2 ảnh dự phòng, ghi vào kế hoạch: đường dẫn, lý do, ảnh đã loại → (6) sau khi dựng, xem ảnh trong preview / Review Lab đúng hình đã định chưa, sai thì quay lại (3). Không chọn theo tên file hoặc số thứ tự.
- **Hai loại sheet: có hướng / không hướng**. Có hướng (đầu đuôi rõ: lửa thổi một phía, sao chổi, tia, vệt) thì **không spam**: dùng đơn / vài hạt to, đặt đúng hướng, không xoay ngẫu nhiên. Không hướng (mây, khói, puff, glow) thì được spam, xoay và khung ngẫu nhiên. Phân loại trước khi gán; chi tiết ở `Docs/VFX/_Library/LIBRARY.md`. **Ảnh mới thêm vào Library**: chạy `python -I tools/library_props.py`; ảnh nào còn `chua_xet` thì **xem ảnh và gán nhãn vào `library_direction.csv` trước khi dùng** (cột `direction_nhap` chỉ là gợi ý).
- Ảnh phát hiện sai thư mục / sai vai trò: ghi vào mục "Sai vai trò đã biết" của `LIBRARY.md`, báo art lead trước khi di chuyển.
- File trong Library dùng chung: chỉ `LoadAssetAtPath`, không đổi import setting. Cần setting khác thì copy ảnh sang `Assets/VFX/<Effect>/Textures/`.
- Luật chỉ định texture cụ thể (khói mặc định, khói vụ nổ, `_MaskTex` của slash) vẫn giữ.

## Hình dáng
- Hình hình học (vòng phép, rune, vòng tròn): vẽ bằng script là tốt.
- Hình hữu cơ (lửa, khói, thân vụ nổ): không tin preset script. Đưa 2–3 phương án ảnh trước, ưu tiên nguồn của art lead.
- Khói mặc định: `Assets/VFX/fx_t_smoke_02.png` + shader mobile mặc định của Unity, tô màu bằng Start Color.
- **Khói vụ nổ** (art lead 2026-11-04) làm theo GroundBlast v5c, không dùng billboard: một khối mesh cầu ăn mòn, shader `VFX/FX/Erode Sphere`.
  - Thiết lập: `SM_VFX_SphereUV`, ~30 cầu, Cone lên, mép sần `_Lumps`. Shader ít thuộc tính; Custom1 = x lúc khói tan, y lúc lửa tắt, z độ mờ viền.
  - Custom1: cháy → gân → than xám → tan thành sợi.
  - Lấy số từ `GroundBlastBuild.cs` mục 3b. Mask `_TEMP` lấy từ video, không ship.
- Flipbook chỉ cho khói / lửa / điện. Frame over Time **tuyến tính** (`ComponentKit.LinearFrames`, không dùng `VfxBuildKit.Curve`).

## Slash
- Slash = **mesh + UV** (texture chạy theo UV trên mesh cung / vòng), không dùng billboard.
- Chỉ dùng bộ shader Coloso (`VFXLib/ColosoShaderAdditive|Alpha|AlphaCutOut_Optimized`): texture xám, màu từ ramp / Color over Lifetime, `_MaskTex` = `T_VFX_Gradient_01`, stream `Custom1XYZW`. Không viết shader slash riêng.
- Giữ texture slash ở bố cục UV gốc (nguyên khung, đúng tỉ lệ).
- Texture chạy UV của slash (`_MainTex`) lấy trong **`Assets/Library/Slash/Main_tex(Uvmesh)/`** (ảnh xám; cách chọn ở `vfx-shader/references/coloso.md`).
- Mesh: lấy từ `Assets/VFX/_Imported/Mesh/` trước.

## Khác biệt giữa các effect
- Effect mới / biến thể: đổi **ít nhất hai** trong: mesh, bố cục-vị trí, timing, lớp phụ. Không chỉ đổi màu.
- Biến thể **vẫn là cùng hiệu ứng** (cùng hành vi, số mảnh, lớp, tính chất hình học). Không tự biến thành effect khác.
- **Giữ tạo hình cốt lõi (art lead 2026-11-10)**: khác biệt phải **thực chất** (đổi chất liệu / mesh / bố cục / timing / lớp phụ) **mà vẫn nhận ra là cùng hiệu ứng**. Đổi màu hoặc đổi texture mà mất hình xương sống (ví dụ aura ôm vật → bông khói, cột sét → laser mờ, thân tornado → khói be) là **hỏng**, kể cả khi đã "khác ít nhất hai".
- **Tạo hình trước khi làm**: mọi effect / biến thể bắt đầu bằng `Docs/VFX/_Anatomy/<loại>.md` (cấu trúc, **Bất biến**, Được đổi, Lỗi đã gặp) + `materials.md` (hình đặc trưng theo chất liệu). Chép "Bất biến" vào kế hoạch. **Chưa có file hoặc chưa hiểu đối tượng → research trước** (prefab tham chiếu → ảnh / video art lead → web → Plan cũ; cách làm ở `_Anatomy/README.md`), hỏi art lead nếu vẫn mơ hồ, **lưu thành file mới + dòng chỉ mục** để lần sau tra thẳng, không research lại. Sau build đối chiếu preview với "Bất biến"; thiếu một cái là chưa xong. Gặp lỗi mới thì thêm vào "Lỗi đã gặp".
- Chất liệu quyết định hình: băng cứng nên gai dài được; đất xốp nên ngắn (~1–2 m), thô, đỉnh vỡ.

## Quy trình bàn giao (art lead chốt 2026-11-13)
- VFX / biến thể mới: làm xong → `tools/check_texture_plan.py` pass → **agent khác review theo luật** → sửa đến khi đạt → **chuyển art lead review lần cuối**. Brief mẫu + thứ tự: `Docs/VFX/_ArtDirection/agent-review.md`. Không tự chốt "đạt"; không thêm vào `Included` khi art lead chưa duyệt.

## Skill
- `vfx-code` tách hẳn khỏi `vfx-maker`; điểm chung duy nhất là Review Lab.
- Mỗi effect mới: prefab `VFX_<Tên>.prefab` trong `Prefabs/`, thêm vào `Included` của `VfxShowcaseBuild.cs` (khi art lead duyệt), chạy lại **VFX → Showcase → Build Scene**.
