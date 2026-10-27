# AI Anim Studio — gộp Mesh / Rig / Pose Lab thành một ứng dụng

**Đã duyệt 2026-10-27** (user: "Duyệt thiết kế theo các đề xuất (Studio chạy cục bộ, giữ thao tác Maya). Bắt đầu S1 + S2."). S1 + S2 xong cùng ngày, xem mục 7. Yêu cầu của user: "Gộp mesh lab, Rig lab, Pose lab thành một ứng dụng giống Maya hoặc Blender. Có viewport chung cùng các menu công cụ. Mesh lab, Rig lab, Pose lab bây giờ chỉ là những workspace được cấu hình sẵn."

## 1. Hiện trạng (khảo sát mã)

| | Mesh Lab | Rig Lab | Pose Lab |
|---|---|---|---|
| File | `work/mesh_lab/template.html`, 915 dòng | `work/rig_lab/template.html`, 1 878 dòng | `work/pose_lab/index.html`, 5 260 dòng |
| Đơn vị | cm | cm | m (glTF) |
| Dữ liệu vào | chèn lúc build (`/*DATA*/`) | chèn lúc build + kéo `mesh/edit` | mảng `POSES` cứng + GLTFLoader |
| Mô hình | mảng đỉnh/tam giác | landmark → xương tự tính, skin LBS riêng | THREE.SkinnedMesh/Bone |
| Undo | snapshot 40 | snapshot `{LM,TW}` + undo skin riêng | snapshot 60 |

Chung: three.js r128 (script global), OrbitControls + TransformControls, trục Y lên, kho `window.claude` → `localDB` → localStorage.
Lặp lại 3 lần: renderer/camera, điều hướng kiểu Maya, gizmo, chọn + marquee, undo, chế độ cảm ứng, channel box (Mesh và Pose có hai bản khác nhau). Chỉ Rig Lab có Outliner. Đoạn mã chung được dán vào từng trang bằng khoảng 30 `patch_*.py`.
Chuyển dữ liệu: Home gọi `DDC` trong iframe (Rig → Pose qua file `models/<clip>_rig_vN.json`, Pose → Review qua playblast). Mesh → Rig là Rig tự kéo bản lưu của Mesh.

Hạn chế chính: mỗi Lab là một thế giới riêng. Muốn sửa mesh khi đang pose phải sang tab khác, gửi, build lại. Công cụ chung phải sửa ba lần.

## 2. Mục tiêu

- **Một ứng dụng, một viewport, một cảnh.** Nhân vật (mesh, xương, skin, anim) là một đối tượng duy nhất, sống trong bộ nhớ.
- **Workspace = cấu hình sẵn**: bố cục panel, bộ công cụ trên toolbar, mặt nạ chọn (đỉnh / khớp / control), những gì hiện trong cảnh. Đổi workspace không tải lại gì.
- **Menu công cụ chung** như Maya/Blender. Lệnh nào cũng gọi được từ menu, phím tắt, hoặc tìm lệnh (phím Space/F3).
- Workspace tự tạo được: kéo panel, lưu thành workspace mới.
- Review Lab giữ nguyên là trang riêng (để người duyệt xem trên claude.ai).

## 3. Giao diện

```
┌ Menu: File  Edit  Select  Mesh  Rig  Skin  Animate  Physics  Display  Window  Help ─── [Mesh|Rig|Pose|+] ┐
├ Shelf: icon công cụ theo workspace (đổi theo tab) ─────────────────────────────────────────────────────┤
│Tool │                                                         │ Outliner                               │
│ Q W │            Viewport (1 / 2 / 4 khung,                    ├────────────────────────────────────────┤
│ E R │            persp / front / side / top / cam game)       │ Channel Box / Attribute                │
│ ... │                                                         │ (tab: Thuộc tính | Công cụ | Lớp)      │
├─────┴─────────────────────────────────────────────────────────┴────────────────────────────────────────┤
│ Timeline + key lane (ẩn ở Mesh, thu nhỏ ở Rig để thử pose)          ▶ ⏮ ⏭  khung  fps                │
└ Dòng trạng thái: đối tượng chọn · số đỉnh/khớp · gợi ý thao tác ───────────────────────────────────────┘
```

Theo `docs/ui_guidelines.md`: nút là icon + tooltip, ít chữ, một nút chính mỗi panel.

### Menu (lệnh cũ chuyển vào đâu)

| Menu | Lệnh |
|---|---|
| File | Mở nhân vật / clip, Lưu, Phiên bản, Nhập FBX/glTF, Xuất OBJ / glTF / FBX, Gửi Review (playblast) |
| Edit | Undo/Redo (một lịch sử chung), Copy/Paste key, Duplicate, Delete, Preferences |
| Select | Chế độ Object / Vertex / Face / Joint / Control, Mở rộng, Đối xứng, Pickwalk |
| Mesh | Tách, gộp, hàn, dọn, lật pháp tuyến, làm mượt, mirror X, đặt sàn, chiều cao |
| Rig | Landmark tự động, Dựng xương, Twist, Ngón tay, Kiểm tra xương, cổng duyệt |
| Skin | Auto skin, Cọ vẽ weight, Island, Hammer, Pose thử, Self-test |
| Animate | Key, Breakdown, Stepped/Spline, Timing, IK/FK, Pole, Foot lock, Fit theo ref, Chân chạm sàn, AI self-review |
| Physics | AutoPhysics, Spring, Impact, Ragdoll, Va chạm thân, Cân bằng, Ngã |
| Display | Wireframe, X-ray, Ghost, Motion trail, Lưới, Ref, Camera game |
| Window | Outliner, Channel Box, Attribute, Timeline, Ref, Ghi chú vẽ, Lưu bố cục |

### Ba workspace sẵn

| | Mesh | Rig | Pose |
|---|---|---|---|
| Chọn | đỉnh / mặt / khối | landmark / khớp | control / khớp |
| Cảnh | mesh đặc + wireframe, ẩn xương | mesh mờ + xương + landmark | mesh skin + control + IK + ghost |
| Panel phải | danh sách mesh, Channel Box | các bước rig + cổng duyệt, Outliner | phiên bản, Channel Box, Physics |
| Dưới | ẩn | timeline ngắn để thử pose | timeline + key lane + Timing |

## 4. Kiến trúc

```
studio/
  index.html            vỏ: menu, dock panel, viewport
  core/                 dùng chung, viết một lần
    viewport.js         renderer, camera, điều hướng Maya, chia khung, camera sẵn
    scene.js            Character: meshes, skeleton, skin, anim (một nguồn dữ liệu)
    select.js           chọn + marquee, theo mặt nạ của workspace
    gizmo.js            TransformControls trên pivot (dùng cho đỉnh, landmark, bone)
    history.js          undo/redo chung (lệnh có do/undo, gộp snapshot cũ)
    commands.js         sổ lệnh: id, tên, icon, phím, menu, điều kiện bật
    store.js            localDB / window.claude / localStorage, một namespace theo nhân vật
    panels/             outliner, channel box, timeline, attribute
  modules/
    mesh/  rig/  pose/  physics/  export/   (mã cũ tách ra, đăng ký lệnh + panel)
  workspaces/*.json     bố cục + shelf + mặt nạ chọn + hiển thị
```

- **Đơn vị**: cảnh chung tính bằng mét (như glTF và Unity). Module Mesh và Rig giữ số liệu cm bên trong, đặt dưới một nhóm scale 0,01, nên ngưỡng cũ không phải đổi.
- **Một Character trong bộ nhớ**: sửa mesh ở workspace Mesh thì Rig và Pose thấy ngay. Skin của Rig chuyển thẳng thành SkinnedMesh cho Pose (thay cho vòng file `rig_vN.json`). Vẫn lưu phiên bản để có lịch sử và git.
- **Dữ liệu tải lúc chạy**, không chèn lúc build: Home server thêm `/api/char/<id>` (mesh, landmark, skin) và `/api/clip/<id>` (phiên bản, key, ref). Một ứng dụng mở được mọi nhân vật / clip; bỏ dần `build_mesh.py`, `build_page.py`, `split_pages.py` và các `patch_*.py`.
- **three.js**: giữ r128 dạng script ở giai đoạn đầu để chuyển mã cũ nhanh; nâng bản sau khi gộp xong.
- **Chạy ở đâu**: trong Home (`/studio/<nhân vật>/<clip>`), thay cho các tab iframe Mesh/Rig/Pose. Review vẫn là tab riêng.

## 5. Lộ trình (mỗi bước dùng được ngay, Lab cũ giữ đến khi bản mới đủ chức năng)

| Bước | Nội dung | Xong khi |
|---|---|---|
| S1 | Vỏ + core: menu, dock, viewport 1/4 khung, chọn, gizmo, undo chung, Outliner, Channel Box, đổi workspace, `/api/char` | mở được Gaygor, xoay/chọn/di chuyển, đổi 3 workspace |
| S2 | Workspace Mesh: chuyển toàn bộ Mesh Lab | làm đủ các thao tác của Mesh Lab cũ trên Gaygor và Zom1 |
| S3 | Workspace Rig: landmark, xương, skin, cọ, cổng duyệt, self-test | ra cùng rig/weight như Rig Lab cũ (so số liệu) — **xong 2026-10-27**, mục 8 |
| S4 | Workspace Pose phần lõi: phiên bản, key, timeline, IK/pole, Channel Box, foot lock, ref, FBX | xuất FBX một clip đã duyệt, so khớp từng khung với bản cũ |
| S5 | Pose phần còn lại: physics, fit theo ref, AI self-review, playblast → Review | đủ chức năng Pose Lab cũ, tắt tab Mesh/Rig/Pose cũ |
| S6 | Workspace tự tạo, nâng three.js, dọn patch cũ | |

Ước lượng: S1–S2 khoảng 1 phiên làm việc dài; S3 1 phiên; S4–S5 là phần nặng nhất (Pose Lab 5 000 dòng), 2–3 phiên.

## 6. Cần user chọn

1. **Trang claude.ai**: hiện mỗi anim có trang Pose Lab đăng lên claude.ai. Studio chạy cục bộ trong Home (cần server để tải dữ liệu). Đề xuất: Studio chỉ chạy cục bộ; claude.ai chỉ còn trang Review.
2. **Phong cách thao tác**: theo Maya (Alt + chuột xoay, Q/W/E/R, Channel Box) như các Lab hiện tại. Đề xuất: giữ Maya.
3. **Bắt đầu**: S1 + S2 trước (vỏ + Mesh, phần nhỏ nhất) để duyệt giao diện trước khi chuyển Rig và Pose.

## 7. Đã làm: S1 + S2 (2026-10-27)

Mở: `http://127.0.0.1:8780` vào thẳng Studio với cảnh trống (user: "sao không mở một file trống"; ô giữa viewport: Nhập FBX, Mở nhân vật, mở nhanh; Tệp → Cảnh mới = Ctrl+N) (từ 2026-10-27, user: "bây giờ là tool tổng hợp… mở phát ra viewport luôn"; Home chuyển sang `/home`, về Home bằng chữ Studio góc trái hoặc Tệp → Dự án, Ctrl+H). Mở nhân vật cụ thể: `http://127.0.0.1:8780/studio/<nhân vật>` (`gaygor`, `zom1_map1`), hoặc trong Home: anim → tab **Studio** (đầu thanh tab, nạp `?clip=<anim>`). Không có nhân vật trong đường dẫn thì hiện hộp Mở nhân vật.
Tham số: `?ws=mesh|rig|pose` (workspace mở đầu), `?ns=<kho>` (lưu vào kho riêng để thử, không đụng bản sửa thật).

| File | Nội dung |
|---|---|
| `tools/studio/index.html`, `studio.css` | Vỏ: menu, shelf, hộp công cụ, viewport, dock (Outliner + tab), timeline, dòng trạng thái |
| `tools/studio/core/app.js` | `ST`: sự kiện, icon, lịch sử undo chung (`ST.hist`, owner `{snap, restore}`), sổ lệnh (`ST.cmd`), kho (`ST.store(ns)` → `/api/store`, dự phòng localStorage), workspace, khởi động |
| `tools/studio/core/viewport.js` | Một renderer, 1 / 4 khung (top, persp, front, side), OrbitControls dùng chung đổi camera theo khung dưới chuột, gizmo chung, chọn click / khung kéo, chế độ cảm ứng. Cảnh = mét; `ST.view.cm` = nhóm scale 0,01 cho module cm |
| `tools/studio/core/ui.js` | Menu từ sổ lệnh, shelf / toolbox theo workspace, Outliner (module trả dòng), Channel Box chung (module trả provider), tìm lệnh F3, phím tắt, kéo đổi cỡ dock |
| `tools/studio/modules/mesh.js` | Mesh Lab chuyển sang: đủ thao tác cũ (chọn mesh/điểm/mặt/khối, mềm + đối xứng, Free Transform, tách gộp nhân bản lật mượt hàn dọn, sàn, chiều cao, kiểm tra, OBJ, mesh_cm.json, về gốc) |
| `tools/studio/modules/later.js` | Workspace Rig / Pose tạm: dùng chung cảnh, panel trỏ Rig Lab / Pose Lab cũ, menu ghi bước sẽ chuyển |
| `tools/studio/workspaces.js` | Cấu hình 3 workspace |
| `tools/home/server.py` | `/studio/...`, `/api/chars`, `/api/char/<id>` (mesh gốc cm, cùng nguồn `build_mesh.py`), `labs.studio` |

Ghi chú kỹ thuật:
- Bản sửa mesh lưu vào đúng kho của Mesh Lab cũ (`<nhân vật>_mesh_lab`, doc `mesh/edit`), nên Rig Lab cũ vẫn đọc mesh đã sửa và hai bản dùng thay nhau được.
- TransformControls gắn vào một div ẩn; viewport tự gọi `pointerHover/Down/Move/Up` với toạ độ của khung đang dùng (bản gốc tính chuột theo cả canvas nên sai khi chia 4 khung).
- Undo giữ vùng chọn điểm / mặt khi số điểm không đổi.
- Đã thử trên trình duyệt (kho thử `studio_test_*`, đã xoá): chọn điểm, gizmo dời, Channel Box, Free Transform, undo/redo, 4 khung + nhìn toàn bộ, mọi lệnh Mesh, đổi 3 workspace, Zom1, tab Studio trong Home.

Còn lại: S3 Rig, S4–S5 Pose, S6 workspace tự tạo + nâng three.js. Mesh Lab cũ (`/lab/mesh/...`) giữ đến khi user thôi dùng.

### Nhập FBX (2026-10-27, user: "Không có import file FBX à")

**Tệp → Nhập FBX…** (Ctrl+Shift+I, nút trên shelf Mesh). Studio gửi file lên Home: `POST /api/fbx/parse` (`tools/home/fbx_import.py`, chạy `work/rig_lab/extract_fbx.py` + `fbxread`, không Blender), đổi về cm (UnitScaleFactor; cao < 10 cm thì coi là mét ×100) và trục Y lên (theo UpAxis/FrontAxis/CoordAxis). Hộp thoại liệt kê từng mesh (số điểm, chiều cao, số xương skin, trùng tên hay không), chọn:
- **Thay mesh trùng tên**: thay mesh cùng tên trong nhân vật đang mở, mesh mới thì thêm. Có undo, lưu như mọi sửa mesh (bản gốc không đổi).
- **Thêm vào cảnh**: thêm mọi mesh đã chọn.
- **Tạo nhân vật mới**: `POST /api/fbx/new-char` ghi `work/rig_lab/ref_<id>/` (ref_mesh.json kèm skin, ref_skeleton.json, đã đổi cm/Y), `chars/<id>.json` (body = mesh nhiều mặt nhất, còn lại ở `extra`, ghi nguồn), `chars/<id>/mesh_cm.json`, rồi mở `/studio/<id>`. Trùng id thì từ chối.
Chỉ đọc FBX binary. Mesh skin vào xương hiện ở tư thế bind của file (vd súng map06 skin vào `slingshot_*` nằm dưới sàn), xương và skin dùng ở workspace Rig/Pose (S3–S4).
Đã thử: FBX rig Gaygor (thay 2 mesh trùng tên), FBX map06 (tạo nhân vật thử, đã xoá), file hỏng → báo lỗi.

### Xương trong Outliner (2026-10-27, user: "Trong outliner không hiển thị joint à")

`/api/char/<id>` trả thêm `skeleton` [{name, parent, pos cm}] từ `work/rig_lab/<ref_dir>/ref_skeleton.json` (× `scale` của nhân vật; joint thiếu bind lấy vị trí cha). `tools/studio/modules/skel.js`: vẽ joint (chấm xanh) + đoạn cha → con trong viewport, nhóm **Skeleton** trong Outliner dạng cây mở / gập (nhớ theo nhân vật), bấm joint để tô cam và xem toạ độ ở dòng trạng thái, F nhìn joint đang chọn, Hiển thị → Xương bật / tắt. Chỉ xem; sửa xương là S3. Zom1 là model tĩnh nên không có xương.

### Outliner bên trái, không lớp nhóm (2026-10-27, user: "Đưa Outliner sang bên trái giống maya. Bỏ lớp tên nhân vật với nhóm Mesh đi", "Ẩn các lớp này đi")

Outliner là cột riêng giữa hộp công cụ và viewport (kéo mép phải để đổi rộng, Cửa sổ → Outliner bật / tắt); dock phải chỉ còn Channel Box / Công cụ / Kiểm tra. Không còn dòng nhân vật, nhóm Mesh, nhóm Skeleton: mesh và joint gốc nằm ngay cấp đầu; mắt ở joint gốc ẩn / hiện cả bộ xương; nút khoá chỉ hiện khi rê chuột hoặc đang khoá.

## 8. S3: workspace Rig (2026-10-27, user: "làm S3 đi")

Lõi Rig Lab chạy thẳng trong viewport Studio, không viết lại thuật toán: `tools/studio/port_rig.py` lấy phần lõi từ `work/rig_lab/template.html` (khớp, xương, twist, kiểm tra, skin cotan "cấp cao", cọ / khối rời / hammer, pose thử + bộ pose căng, tự kiểm, xuất rig.json / weights / glTF, dùng xương + skin khách) và sinh `tools/studio/modules/rig_engine.js`, chỉ thay chỗ chạm vào renderer, camera, canvas, gizmo, undo, kho lưu, thanh bước. Mỗi phép thay có assert: template đổi thì chạy lại `python tools/studio/port_rig.py` sẽ báo ngay chỗ lệch. Không sửa tay `rig_engine.js`.

`tools/studio/modules/rig.js` nối lõi vào Studio:
- 5 bước của Rig Lab = 5 tab dock (1 Mesh · 2 Khớp · 3 Xương · 4 Skin · 5 Thử) + tab Channel; phím 1–5, nút số ở hộp công cụ; cổng Duyệt / Cần sửa giữ nguyên.
- Bước 2: click / kéo khung chọn khớp (khung nào cũng được), Q/W/E/R + gizmo chung, đối xứng R→L, Channel Box nhập toạ độ khớp (cm).
- Bước 4–5: click joint trong viewport, cọ / khối rời chặn chọn khung, thanh xoay joint nằm đầu panel.
- Undo chung: khớp / twist và từng nét tô skin là một bước trong Sửa → Hoàn tác.
- Outliner: mesh của rig (ẩn / hiện) + cây xương đang dựng (bấm để chọn khớp ở bước 2, chọn xương ở bước 4–5).
- Mesh: dùng mesh đang sửa ở workspace Mesh (thay theo tên, dời landmark nếu thân đổi cỡ), như MESHLINK của Rig Lab.
- Lưu cùng kho với Rig Lab cũ (`<nhân vật>_rig_lab`: rig/landmarks, rig/gates, rig/skin) nên hai bản dùng thay nhau được.
- Rig → Gửi rig sang Pose…: chọn anim của nhân vật → `POST /api/rig/to-pose` (như nút ➤ của Home cũ).

Server: `tools/home/rig_data.py` — `GET /api/rigdata/<id>` lấy DATA nhúng trong `work/rig_lab/pages/<id>/index.html` (đúng bản Rig Lab đang dùng); nhân vật nhập FBX đã rig thì điền lại vị trí xương khách + skin khách (build_char.py để trống) để "Đặt khớp theo xương khách" / "Dùng skin khách" chạy. `POST /api/rig/build` cho nhân vật chưa có dữ liệu rig: suy cấu hình (ngón, đốt, toes, headEnd…) từ tên xương khách rồi chạy `build_char.py` (cần xương kiểu Advanced Skeleton; model tĩnh chưa hỗ trợ).

Đã thử (kho thử `studio_test_*`, đã xoá; kho rig thật không đổi): Gaygor bước 1–5 (chọn + dời khớp, đối xứng, undo; 7 kiểm tra xương đạt; tính skin ~1 s; cọ tô + undo; pose "Giơ tay lên" căng 4,5%), Gragas (dựng dữ liệu rig từ FBX, dùng xương + skin khách, "Ngồi xổm" căng 3%), Zom1 (tính skin, dựng glTF 29 xương). Chưa thử: Gửi rig sang Pose thật (ghi phiên bản vào anim), chuột thật trên gizmo khớp.
Giới hạn: template ngón tối đa 3 đốt (Gragas có đốt 4 + Cup: báo thiếu ở bước 3, không ảnh hưởng skin khách).
