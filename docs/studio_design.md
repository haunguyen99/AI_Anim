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
- **Một Character trong bộ nhớ**: sửa mesh ở workspace General thì Rig và Pose thấy ngay. Skin của Rig chuyển thẳng thành SkinnedMesh cho Pose (thay cho vòng file `rig_vN.json`). Vẫn lưu phiên bản để có lịch sử và git.
- **Dữ liệu tải lúc chạy**, không chèn lúc build: Home server thêm `/api/char/<id>` (mesh, landmark, skin) và `/api/clip/<id>` (phiên bản, key, ref). Một ứng dụng mở được mọi nhân vật / clip; bỏ dần `build_mesh.py`, `build_page.py`, `split_pages.py` và các `patch_*.py`.
- **three.js**: giữ r128 dạng script ở giai đoạn đầu để chuyển mã cũ nhanh; nâng bản sau khi gộp xong.
- **Chạy ở đâu**: trong Home (`/studio/<nhân vật>/<clip>`), thay cho các tab iframe Mesh/Rig/Pose. Review vẫn là tab riêng.

## 5. Lộ trình (mỗi bước dùng được ngay, Lab cũ giữ đến khi bản mới đủ chức năng)

| Bước | Nội dung | Xong khi |
|---|---|---|
| S1 | Vỏ + core: menu, dock, viewport 1/4 khung, chọn, gizmo, undo chung, Outliner, Channel Box, đổi workspace, `/api/char` | mở được Gaygor, xoay/chọn/di chuyển, đổi 3 workspace |
| S2 | Workspace Mesh: chuyển toàn bộ Mesh Lab | làm đủ các thao tác của Mesh Lab cũ trên Gaygor và Zom1 |
| S3 | Workspace Rig: landmark, xương, skin, cọ, cổng duyệt, self-test | ra cùng rig/weight như Rig Lab cũ (so số liệu) — **xong 2026-10-27**, mục 8 |
| S4 | Workspace Pose phần lõi: phiên bản, key, timeline, IK/pole, Channel Box, foot lock, ref, FBX | xuất FBX một clip đã duyệt, so khớp từng khung với bản cũ — **chuyển cả lõi (gồm phần S5) 2026-10-27**, mục 9 |
| S5 | Pose phần còn lại: physics, fit theo ref, AI self-review, playblast → Review | đủ chức năng Pose Lab cũ, tắt tab Mesh/Rig/Pose cũ |
| S6 | Workspace tự tạo, nâng three.js, dọn patch cũ | |

Ước lượng: S1–S2 khoảng 1 phiên làm việc dài; S3 1 phiên; S4–S5 là phần nặng nhất (Pose Lab 5 000 dòng), 2–3 phiên.

## 6. Cần user chọn

1. **Trang claude.ai**: hiện mỗi anim có trang Pose Lab đăng lên claude.ai. Studio chạy cục bộ trong Home (cần server để tải dữ liệu). Đề xuất: Studio chỉ chạy cục bộ; claude.ai chỉ còn trang Review.
2. **Phong cách thao tác**: theo Maya (Alt + chuột xoay, Q/W/E/R, Channel Box) như các Lab hiện tại. Đề xuất: giữ Maya.
3. **Bắt đầu**: S1 + S2 trước (vỏ + Mesh, phần nhỏ nhất) để duyệt giao diện trước khi chuyển Rig và Pose.

## 7. Đã làm: S1 + S2 (2026-10-27)

Mở: `http://127.0.0.1:8780` vào thẳng Studio với cảnh trống (user: "sao không mở một file trống"; ô giữa viewport: Nhập FBX, Mở nhân vật, mở nhanh; Tệp → Cảnh mới = Ctrl+N) (từ 2026-10-27, user: "bây giờ là tool tổng hợp… mở phát ra viewport luôn"; Home chuyển sang `/home`, về Home bằng chữ Studio góc trái hoặc Tệp → Dự án, Ctrl+H). Mở nhân vật cụ thể: `http://127.0.0.1:8780/studio/<nhân vật>` (`gaygor`, `zom1_map1`), hoặc trong Home: anim → tab **Studio** (đầu thanh tab, nạp `?clip=<anim>`). Không có nhân vật trong đường dẫn thì hiện hộp Mở nhân vật.
Tham số: `?ws=general|rig|pose` (workspace mở đầu; `mesh` cũ tự thành `general`), `?ns=<kho>` (lưu vào kho riêng để thử, không đụng bản sửa thật).

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

### Chọn và sửa joint trong viewport (2026-10-27, user: "Người dùng không thể chọn được joint trong viewport và translate")
Workspace General, chế độ chọn mesh: click gần joint (≤ 10 px, cảm ứng 26 px) thì chọn joint (joint vẽ đè lên mesh nên ưu tiên joint), click chỗ khác hoặc chọn mesh thì bỏ chọn. Joint đang chọn nhận gizmo (W dời, E xoay, R scale) và Channel Box (TX/TY/TZ = vị trí joint, cm; xoay / scale tính quanh vị trí joint lúc chọn); mọi joint con đi theo như Maya. Undo chung. Lưu tự động ở doc `skel/edit` (`{joints: {tên: [x,y,z] cm}}`) của kho `<nhân vật>_mesh_lab`, cạnh `mesh/edit`; mở lại nhân vật thì nạp bản sửa. Code: `tools/studio/modules/skel.js` (pickAt, select, gz*, channel) + `mesh.js` chuyển click / gizmo / Channel Box sang joint khi có joint đang chọn. Chưa có: workspace Rig / Pose chưa dùng vị trí joint đã sửa ở General.

### Mesh skin đi theo joint (2026-10-27, user: "FBX hiện tại đang có Skin, sao khi xoay joint trong General mesh không đi theo")
`/api/char` gửi kèm `weights` của FBX (`{xương: [[đỉnh], [w]]}`, trong `chars/<id>/mesh_cm.json`). `mesh.js` gắn skin cho mesh trùng tên và cùng số đỉnh với bản gốc (4 ảnh hưởng mạnh nhất / đỉnh, chuẩn hoá). Mỗi joint giữ `D` = biến đổi từ bind tới hiện tại (cm, world); dời / xoay / scale joint nhân D cho joint đó và mọi joint con. Mesh hiển thị = Σ w·D·v_bind (LBS trên CPU, ~4k đỉnh tức thì); `o.pos` vẫn là mesh bind nên `mesh/edit` và Rig không bị pose làm hỏng. Skin → **Về Bind Pose** đưa joint + D về bind. Khi xương đang pose, mesh có skin bị khoá sửa đỉnh (gizmo / Channel Box / chế độ điểm-mặt) cho tới khi về bind pose. `skel/edit` v2 lưu thêm `D` (chỉ joint khác bind). Sửa topology (xoá mặt, tách, hàn) thì mesh đó mất skin.

### Ẩn / hiện kiểu Maya (2026-10-27)
Ctrl+H ẩn mesh đang chọn, Shift+H hiện mesh đang chọn (chọn mesh ẩn trong Outliner), Ctrl+Shift+H hiện tất cả (menu Hiển thị).

### Cầu nối Claude ↔ Studio (2026-10-27, user: "có cách nào tối ưu hơn không" / "làm thử và test xem cách cũ với mới chênh lệch như nào")
Trang Studio long-poll `GET /api/studio/poll` (server `tools/home/studio_bridge.py`), Claude gửi `POST /api/studio/cmd {op, args}` qua `tools/studio_cmd.py`, trang làm rồi `POST /api/studio/result`. Lệnh đi tới tab đang xem có nhân vật, poll gần nhất; tab báo đổi nhân vật / workspace / ẩn hiện bằng `/hello`, đóng tab gửi `/bye`. Lệnh (`modules/bridge.js`): state, vis, select, joint {t, r, s}, bindPose, ws, run {id}, open. An toàn: không có eval; `/cmd`, `/result` chỉ nhận `application/json` và Origin rỗng hoặc 127.0.0.1 / localhost (chặn trang web lạ).
Đo trên Boss_Gragas (ẩn/hiện một mesh): cách cũ (công cụ trình duyệt của Claude chạy JS bấm nút Outliner) ~170 ms mỗi lần gọi, ~340 ms nếu chờ cập nhật, chỉ dùng được trong trình duyệt của app. Cầu nối: trong trang 2–5 ms, khứ hồi HTTP trung vị 3,7 ms (20 lần); một lệnh lẻ qua `studio_cmd.py` ~160 ms (phần lớn là khởi động Python), qua curl ~60 ms; 6 lệnh gộp một lần chạy 185 ms. Dùng được ở Chrome của người dùng.

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
- Mesh: dùng mesh đang sửa ở workspace General (thay theo tên, dời landmark nếu thân đổi cỡ), như MESHLINK của Rig Lab.
- Lưu cùng kho với Rig Lab cũ (`<nhân vật>_rig_lab`: rig/landmarks, rig/gates, rig/skin) nên hai bản dùng thay nhau được.
- Rig → Gửi rig sang Pose…: chọn anim của nhân vật → `POST /api/rig/to-pose` (như nút ➤ của Home cũ).

Server: `tools/home/rig_data.py` — `GET /api/rigdata/<id>` lấy DATA nhúng trong `work/rig_lab/pages/<id>/index.html` (đúng bản Rig Lab đang dùng); nhân vật nhập FBX đã rig thì điền lại vị trí xương khách + skin khách (build_char.py để trống) để "Đặt khớp theo xương khách" / "Dùng skin khách" chạy. `POST /api/rig/build` cho nhân vật chưa có dữ liệu rig: suy cấu hình (ngón, đốt, toes, headEnd…) từ tên xương khách rồi chạy `build_char.py` (cần xương kiểu Advanced Skeleton; model tĩnh chưa hỗ trợ).

Đã thử (kho thử `studio_test_*`, đã xoá; kho rig thật không đổi): Gaygor bước 1–5 (chọn + dời khớp, đối xứng, undo; 7 kiểm tra xương đạt; tính skin ~1 s; cọ tô + undo; pose "Giơ tay lên" căng 4,5%), Gragas (dựng dữ liệu rig từ FBX, dùng xương + skin khách, "Ngồi xổm" căng 3%), Zom1 (tính skin, dựng glTF 29 xương). Chưa thử: Gửi rig sang Pose thật (ghi phiên bản vào anim), chuột thật trên gizmo khớp.
Giới hạn: template ngón tối đa 3 đốt (Gragas có đốt 4 + Cup: báo thiếu ở bước 3, không ảnh hưởng skin khách).

## 9. S4: workspace Pose (2026-10-27, user: "Bắt đầu S4: chuyển Pose Lab vào workspace Pose của Studio")

Như S3, không viết lại: `tools/studio/port_pose.py` sinh từ `work/pose_lab/index.html` (bản gốc có mọi clip):
- `modules/pose_engine.js`: toàn bộ lõi Pose Lab (key, spline / bậc thang, IK tay chân, pole, khóa chân, Timing, copy / paste, Channel Box, vật lý: AutoPhysics, lò xo, tác động, ragdoll, va chạm thân, cân bằng, ngã; khớp ref, chân chạm sàn, vẽ ghi chú, AI tự xem, FBX, playblast) bọc trong `ST.poseEngine(POSES, host)`; chỉ thay renderer / camera / canvas / OrbitControls / TransformControls / vòng vẽ / kho lưu bằng của Studio; nút tải FBX tải thẳng về máy (Pose Lab cũ chỉ tải được trên claude.ai). `ST.POSE_HTML` = giao diện Pose Lab, `ST.poseDB(ns)` = kho Home (có onSnapshot).
- `pose.css`: CSS Pose Lab khoanh trong `.pz` (biến màu dùng của Studio).
`modules/pose.js` đặt giao diện vào vỏ: thanh công cụ → shelf; Khớp / Vật lý / Ghi chú / Phiên bản → tab dock (tab Phiên bản có ô chọn anim); timeline (key, lane, Timing, transport, Xuất FBX) → vùng timeline; HUD, nút camera, ref, vẽ ghi chú → lớp phủ viewport. Viewport vẽ thêm cảnh + lớp phủ của Pose (`V.extra`), 1 hoặc 4 khung. Outliner = cây khớp của model. Phím: workspace Pose tự xử lý (Space phát, 1–7 camera, Q/W/E…), Studio chỉ giữ phím chung (Ctrl+O/H/N, F1, F3). Sửa → Hoàn tác gọi undo của Pose. Animate → Quay playblast và gửi sang Review (như nút 🎞 Home cũ), Đổi anim…, Mở Pose Lab cũ.
Một anim mỗi lần: `?clip=<anim>` (từ Home, lần trước, hoặc anim đầu của nhân vật); đổi anim = tải lại trang. Mở được cả anim không có nhân vật trong Studio (SDR): `/studio/?ws=pose&clip=sdr_idle`. Kho: đúng kho Pose Lab cũ (`<tiêu đề trang>_pose_lab`), `?ns=` để thử.
Server: `tools/home/pose_data.py` — `GET /api/poses?char=<id>` (anim có Pose của nhân vật), `GET /api/poses/<anim>` (phiên bản lấy từ bản gốc, như split_pages.py).

Đã thử (kho thử, đã xoá): Gaygor Die (goal_v1 72 F): chọn khớp từ Outliner, xoay bằng gizmo, đặt key F30 + Sửa → Hoàn tác, phát / dừng, tab Phiên bản / Vật lý, Xuất FBX (zip 0,8 MB, không tải), đổi General ↔ Rig ↔ Pose; SDR Idle không nhân vật, 4 khung. Chưa thử: playblast → Review thật, khớp ref, AI tự xem, vật lý chạy thật trên trang Studio.

## 10. W1: workspace chỉ là layout (2026-10-28, user: "General là một workflow tổng có thể làm mọi việc… mỗi WorkSpace chỉ là một layout chứa các công cụ thuận tiện cho một nhiệm vụ")

Studio là môi trường làm việc chung của người và AI: mọi công cụ dùng được ở mọi nơi, workspace chỉ đổi bố cục.

- **Workspace = layout**: panel nào mở sẵn (tab dock), shelf có nút gì, hộp công cụ, Outliner / dock / timeline bật tắt, kích thước, và module được **focus** mặc định. Đổi workspace không khoá lệnh, không đổi dữ liệu, không đổi vùng chọn.
- **Focus** (`ST.focus`, thay cho "module của workspace"): module đang được sửa: `mesh` (mesh + xương), `rig`, `pose`. Focus đổi khi bấm vào thứ của module đó: dòng Outliner, panel / tab dock, shelf / timeline của module, lệnh của module, hoặc click trúng đồ của module trong viewport (`hit`). Chuột, gizmo, Channel Box, phím tắt, Hoàn tác đi theo focus.
- **Lớp** (`ST.layerOn`): `scene` (mesh + xương), `rig` (bản rig đang dựng), `anim` (model của anim đang mở). Ba lớp là ba bản của cùng một nhân vật nên bật một lớp thì hai lớp kia tự ẩn (Shift + bấm mắt để hiện chồng). Lớp nạp lười: bật lần đầu mới tải dữ liệu rig / anim. Focus vào module có lớp đang ẩn thì lớp đó hiện.
- **Lệnh**: bỏ `ws:`; lệnh có `mod` (module chủ). Lệnh chỉ mờ khi thiếu dữ liệu. Chạy lệnh của module khác thì focus chuyển sang module đó (trừ lệnh hiển thị). Phím tắt: lệnh của module đang focus trước, rồi lệnh chung; phím của module khác không chạy (1–5, B, I trùng nhau giữa Mesh / Rig).
- **Panel** (`ST.PANELS` trong `workspaces.js`): `channel`, `mesh:tool`, `mesh:check`, `rig:s1`…`rig:s5`, `pose:joint|phys|notes|versions`. Cửa sổ → Panel… mở / đóng panel bất kỳ trong workspace đang dùng (lưu theo workspace, "Bố cục mặc định" trả lại).
- **Outliner**: mesh + cây xương ở cấp đầu như cũ; thêm nút **Rig** và **Anim · <clip>** (gập được, có mắt = bật lớp) khi có nhân vật / anim. Dòng mờ = lớp đang ẩn.
- Shelf / timeline của module (thanh công cụ + timeline Pose Lab) là một khối của module: workspace khai báo `shelf: "@pose"`, timeline lấy của module có timeline.
- Cầu nối: `joint` không đổi workspace nữa (focus mesh); thêm `focus`, `layer`, `cmds`; `state` báo focus + lớp.

Mở: W2 (cầu nối đầy đủ cho AI), W3 (một bản nhân vật chung cho Mesh / Rig / Pose).

## 11. W2: cầu nối đầy đủ cho AI (2026-10-28, user: "Làm W2")

AI làm việc trong Studio đang mở như người dùng: không cần trình duyệt của Claude, không chụp màn hình, người dùng thấy ngay trên trang. Mọi lệnh qua `tools/studio_cmd.py` (server `tools/home/studio_bridge.py`, trang `modules/bridge.js`), chỉ lệnh có tên.

- `state`: nhân vật, workspace, focus, lớp, tab, công cụ, trạng thái lưu, bước Hoàn tác kế; mesh; xương (joint chọn, pose); **rig** (bước, khớp chọn, có skin chưa, cổng duyệt, lưu); **anim** (anim, phiên bản, frame / tổng, khớp chọn, key, đang phát, khớp đã sửa chưa key).
- Chung: `undo`, `redo`, `save`, `view` (1 / 4 khung, khung persp / top / front / side, nhìn toàn bộ / vùng chọn), `snap` (ảnh viewport PNG lưu ra file: để AI tự kiểm, không gửi người dùng nếu họ không hỏi).
- Rig: `rig` với `lms` (danh sách khớp + toạ độ cm), `lm <tên> x,y,z` (đặt khớp, theo đối xứng nếu bật), `sel <tên…>`, `step <1–5>`.
- Anim: `frame <f>`, `play on|off`, `jsel <khớp…>`, `rot <khớp> x,y,z` (xoay thêm theo trục local của khớp, độ; `--abs`: đặt góc local XYZ tuyệt đối), `pos <khớp> x,y,z` (dời thêm, cm, trục Blender X, Y, Z lên; hông / cổ chân / cổ tay theo IK như Channel Box), `key` / `unkey` (frame hiện tại), `keys`, `read [khớp…]` (góc local + vị trí thế giới), `versions`, `version <tên>`. Sửa khớp ở bản dạng key thì Auto key đặt key luôn (như kéo gizmo trên trang).
- Lõi Pose mở thêm `ai` (sinh trong `port_pose.py`, không sửa tay `pose_engine.js`). Nhìn toàn bộ khi focus Pose dùng khung của lõi Pose.

Đã thử (kho thử, đã xoá): Gaygor: view 1 / 4 khung + nhìn toàn bộ, snap (ảnh đúng cảnh mesh và cảnh Anim), rig step / sel / lm (đối xứng) + undo, anim info / versions / frame / read / rot (góc local Z +15° đúng) / pos hông / key / unkey / undo (lõi Pose) / đổi phiên bản, báo lỗi khớp sai tên và key trên bản nướng sẵn. Lõi Rig / Pose nạp lười: lệnh đầu chờ 1–2 s.

## 12. W3: một nhân vật chung cho Mesh / Rig / Pose (duyệt 2026-10-28, user: "Duyệt, làm W3a")

Ba bản cùng một nhân vật: lớp Cảnh (mesh đã sửa + khớp + skin của Rig, đã là bản gốc), lõi Rig (bản sao mesh để đặt khớp / tô skin), lớp Anim (mỗi phiên bản Pose trỏ tới một model glTF chụp lúc tạo). Lộ trình: **W3a** anim dùng nhân vật hiện tại · **W3b** Rig vẽ khớp / skin lên chính mesh của lớp Cảnh, bỏ bản sao · **W3c** Outliner một cây, một khớp dùng chung (General sửa bind, Anim sửa pose của frame).

### W3a: anim dùng nhân vật hiện tại (2026-10-28)
- Phiên bản dạng key có model xuất từ rig Studio (`models/<clip>_rig_vN.json` của "Gửi rig sang Pose", hoặc `model: "live"` trong POSES) của nhân vật đang mở: lõi Pose nạp model dựng trực tiếp bằng lõi Rig (`buildGltf`: mesh đã sửa + khớp + skin hiện tại), không dùng file chụp. Rig nạp lười, ẩn lớp vẫn dựng được.
- Key vẫn lưu theo model chụp của phiên bản (Pose Lab cũ đọc đúng): khi hiện, vị trí xương = vị trí nghỉ của rig mới + phần dời thêm so với model chụp, góc xoay giữ nguyên (xương của rig Studio không có góc nghỉ nên góc local áp thẳng được); khi lưu đổi ngược lại. Không còn file chụp trên máy thì chỉ hông (`root`, `Root_M`) giữ vị trí của key.
- Chọn model theo phiên bản: Animate → "Model: nhân vật hiện tại" (doc `studio/model` trong kho Pose, chung mọi máy). Mặc định: sống, trừ anim đã xuất (stage `export`) giữ model chụp. Không có file chụp trên máy thì không chuyển sang chụp được.
- Rig / mesh đổi (lưu khớp, tô / tính skin, sửa mesh) → quay lại lớp Anim hoặc focus Pose thì model dựng lại.
- Phiên bản có model từ FBX / Blender (mọi anim Gaygor, SDR) giữ model của chúng: hướng xương có thể khác rig Studio.
- FBX xuất ra từ phiên bản đang dùng nhân vật hiện tại là bản chụp của lúc xuất; chưa ghi model đó lại vào phiên bản.
- Lõi: `port_pose.py` (`host.liveModel`, `liveIn` / `liveOut`, `reopen`, `isLive`); Studio: `modules/pose.js`; `/api/poses/<anim>` trả thêm `stage`. Cầu nối: `anim info` có `model: live|snap`.

Đã thử (kho thử chép từ Boss_Gragas, đã xoá): rig_v1 (file chụp không có trên máy) chạy trên rig hiện tại sau khi tính skin; xoay khuỷu −40° + key, dời cổ tay trong Rig (cẳng tay 37 → 51 cm) → quay lại Anim tự dựng lại, khuỷu vẫn −40°, cổ tay theo đúng hướng, xa hơn; tải lại trang key còn nguyên; Gaygor Hit vẫn dùng model riêng.

### W3b: Rig là chế độ sửa của nhân vật, không còn lớp riêng (2026-10-28, user: "Làm W3b")
Lõi Rig vẽ mesh theo kiểu riêng từng bước (thân mờ khi đặt khớp, màu trọng số khi tô, biến dạng khi thử khớp, quần áo bám thân), nên không vẽ thẳng lên mesh của Cảnh mà đổi cách coi: **Rig là chế độ sửa của nhân vật trong Cảnh**.
- Hai lớp: `scene` (nhân vật: mesh + xương + rig) và `anim`. `rig` chỉ còn là tên cũ của `scene` (link, cầu nối `layer rig` vẫn chạy).
- Focus Rig: lõi Rig vẽ nhân vật, mesh + xương của Cảnh ẩn. Rời Rig: lõi Rig ẩn, Cảnh vẽ lại (mesh đã sửa, skin + khớp của Rig). Trên màn hình luôn một nhân vật.
- Ẩn / hiện mesh (mắt Outliner, Ctrl+H, cầu nối `vis`) là của mesh trong Cảnh, áp sang lõi Rig theo tên (thân, quần áo, prop). Bỏ ba lệnh Hiển thị → Rig: thân / quần áo / prop.
- Outliner: mesh chỉ một dòng ở cấp đầu; nút Rig không có mắt (bấm = sửa rig), con là cây xương đang dựng.
- Còn lại: lõi Rig vẫn giữ bản dữ liệu mesh riêng để tính (cọ, biến dạng) và dựng lại khi mesh đổi (lần focus Rig sau). W3c: một khớp dùng chung giữa General và Rig.

Đã thử (kho thử, đã xoá): Gaygor General ↔ Rig ↔ Pose, mesh / xương / rig hiện đúng một bản; ẩn vũ khí ở General thì Rig cũng ẩn, hiện lại từ Outliner lúc đang ở Rig thì Rig hiện ngay; cầu nối `layer rig on` + `focus rig`.

### W3c: một bộ khớp dùng chung (2026-10-28, user: "Tiếp đi")
- **Một cây khớp trong Outliner**: cây xương của nhân vật (khớp của Rig nếu đã rig, chưa thì xương khách) ở cấp đầu, một lần. Nút Rig / Anim không lặp lại cây riêng; chỉ anim không có nhân vật (vd SDR) mới có cây riêng dưới nút Anim.
- **Chọn khớp dùng chung**: bấm khớp trong cây = chọn ở chế độ đang sửa (General: xương Cảnh; Rig: khớp ở bước 2, xương ở bước 4–5; Anim: khớp của model). Khớp chế độ đó không có thì dòng mờ, bấm thì báo, không đổi chế độ. Đổi chế độ (`ST.setFocus`) thì khớp đang chọn đi theo (`ST.jsel`; module có `curJoint / hasJoint / selectJoint`).
- Vai trò giữ như kiểu Maya: General = xoay / dời thử (mesh skin đi theo, không key), Rig = vị trí khớp gốc (bind), Anim = pose có key. (Đề xuất cũ ghi "General sửa bind": đổi lại vì General đang là chỗ thử pose có skin.)
- Cầu nối: `state` có `jointSel` (khớp đang chọn của chế độ đang sửa).

Đã thử (kho thử, đã xoá): Gaygor chọn Elbow_R ở General → Rig bước 2 → Anim vẫn là Elbow_R; ở Anim bấm Head_M trong cây chung → chọn Head_M, vẫn ở Anim; 6 khớp model anim không có (vd `root`) mờ, bấm chỉ báo.

### Chạy thử trọn vòng Gaygor qua cầu nối (2026-10-28, user: "hãy chạy thử một nhân vật với app mới xem sao")
Bản sao kho Gaygor, General (xoay vai có skin, bind pose) → Rig (bước 2 chọn khớp, tính skin, bước 5) → Anim (Walk, Hit: đọc, xoay + key, hoàn tác, phát / dừng, đổi anim) → chọn khớp đi theo. Lệnh trong trang 3–300 ms, Rig nạp lần đầu ~2 s, Anim ~5 s. Lỗi tìm ra và đã sửa:
- `snap` ra ảnh 0×0 khi trang ẩn (khung trình duyệt thu nhỏ): giờ tự vẽ ra 1280×720 (`offscreen: true`) rồi trả canvas như cũ; "nhìn toàn bộ" khi khung 0 px dùng tỉ lệ 16:9.
- Camera trực giao (trên / trước / bên) vẽ cả vật sau lưng (near −100): tấm ref của Pose đè kín khung thành màu cam. Near 0,05, far 200.
- Anim "nhìn toàn bộ": khung trực giao dùng bounds; bounds lấy mẫu đỉnh mesh đã pose (chùy vươn 1,5 m ngoài khớp), vùng chọn theo khớp.
- Cầu nối thiếu đổi anim: thêm `anim clips`, `anim clip <id>`. `open` / `anim clip` từng tải lại trang trước khi gửi kết quả (báo hết giờ): giờ gửi xong mới đổi trang.
- Hai trang Studio cùng mở: cầu nối gửi tới trang đang hiện, có thể không phải trang định thử: thêm `--cid` (xem `clients`).
- `select joint` không chạy khi đang ở Anim: giờ tự về General. Rig vào bước 2 / 4–5 mà chưa chọn khớp thì lấy khớp dùng chung.

### Vẽ ghi chú lên viewport (2026-10-28, user: "Ô bạn bỏ tính năng vẽ lên viewport để fb rồi ạ" → "Thêm nút vẽ")
Rig Lab cũ chưa từng có; Pose Lab có "✎ Vẽ" (lưu vào điều chỉnh của Pose, vẫn còn ở chế độ Anim). Studio thêm `modules/notes.js` cho mọi chế độ:
- Nút ✎ góc dưới trái viewport (và shelf General / Rig, Cửa sổ → Vẽ ghi chú): khoá camera, vẽ tay (4 màu, bỏ nét, xoá), gõ một dòng, Lưu (Enter) / Huỷ (Esc).
- Lưu vào kho `<nhân vật>_studio`: `notes/<id>` = chữ, trạng thái, nét (toạ độ 0..1), ngữ cảnh (workspace, chế độ, tab, khớp đang chọn, bước Rig + khớp chọn, anim + phiên bản + frame, camera: khung, vị trí, hướng, tâm, zoom); `noteimg/<id>` = ảnh JPEG khung nhìn kèm nét (≤1600 px).
- Panel dock "Ghi chú vẽ" (mặc định trong General và Rig; không đổi chế độ sửa): ảnh nhỏ, Xem (về đúng chế độ, bước / frame, góc camera, hiện lại nét), Đã sửa / Mở lại, Xoá.
- Claude: `studio_cmd.py notes [nhân vật] [--all] [--out DIR]` đọc thẳng file trong `work/store/*_studio`, ghi ảnh, kèm `strokes_cm` (khung trực giao: nét → toạ độ cm theo camera + `aspect` lưu trong ngữ cảnh); `note-done <id> [--open]`.
- **Gửi cho AI** (panel Ghi chú vẽ, 2026-10-28, user: "tôi nhớ trước đây có nút gửi fb cho AI"): đánh dấu ghi chú đang mở `sent`, chép sẵn `/check_fb` để dán vào chat (trang không tự gọi được Claude); skill `/check_fb` đọc ghi chú Studio trước Review Lab.
- **Tự nhận khi bấm Gửi** (user: "trước đây tôi ấn nút gửi FB trong app là AI đọc được luôn"): `tools/notes_watch.py` chạy nền trong phiên chat (chỉ đọc thư mục `work/store/*_studio/notes` mỗi 2 s, không tốn lượt AI), thoát khi có ghi chú đã gửi chưa nhận và đánh dấu `picked` → Claude được gọi dậy, sửa, `note-done`, bật lại. Panel tự đọc lại mỗi 4 s khi có ghi chú đang chờ: "đã gửi AI" → "AI đã nhận, đang sửa" → "AI đã sửa".
- **Tự bật bộ canh khi Studio mở** (user: "hãy tự khởi động vòng canh nhỏ, khi studio được mở"): `notes_watch.py` ghi nhịp tim `work/store/_sys/watch/notes.json` mỗi 2 s (`--status` = running/stopped, không chạy trùng). Hook dự án `.claude/settings.json` (SessionStart + UserPromptSubmit) chạy `tools/notes_watch_hook.py`: có trang Studio nối (`/api/studio/clients`) mà nhịp tim cũ hơn 10 s thì nhắc Claude bật bộ canh nền. Panel Ghi chú vẽ hiện "● Claude đang canh" / "○ Claude không canh". Giới hạn: chỉ phiên chat đang mở mới bật được; trang không tự gọi Claude khi không có phiên.
Đã thử (kho thử, đã xoá): Gaygor General vẽ vòng quanh tay + chữ, ảnh + nét + khớp đang chọn đúng; Xem đưa camera về; nút có ở Rig và Anim; đọc + đánh dấu xong qua studio_cmd.
