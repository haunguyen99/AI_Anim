# Kho dữ liệu chung của các Lab

Bước 1 của kế hoạch gộp Rig / Pose / Review thành một ứng dụng: các Lab lưu vào **file thật trong dự án** thay vì chỉ vào db của artifact claude.ai.

## Cách hoạt động

- **Home server** (`tools/home/server.py`, cổng 8780) phục vụ `/api/store/...` (`tools/home/store.py`). Dữ liệu nằm ở `work/store/<ns>/<collection>/<id>.json`; `<ns>` là tên trang (tiêu đề, vd `gaygor_walk_pose_lab`; đổi bằng `?ns=`).
- **Lớp `localdb.js`** (`tools/home/localdb.js`) giả giao diện db của artifact (`doc` / `collection`, `get` `set` `update` `delete` `add` `onSnapshot`), nên mã Lab không phải đổi. Nhúng vào ba master bằng `work/patch_localdb.py` (`--refresh` khi sửa `localdb.js`).
- **Thứ tự chọn nơi lưu:** db claude.ai (khi mở trên claude.ai) → kho trên máy (khi Home server đang chạy) → trình duyệt / tải file `.json` như cũ.
- **Nút Lưu trữ** (icon cơ sở dữ liệu, góc trên phải mỗi Lab): cho biết nơi lưu đang dùng (chấm xanh = có kho, vàng = chưa), **Xuất file** (`<ns>_<ngày>.json`, định dạng `ddc-store-v1`) và **Mở file** (ghi lại vào kho; tải lại trang để thấy). Hoạt động cả khi lưu bằng db claude.ai.

## File cảnh `.aas` (chuyển cả nhân vật sang máy khác)

Studio **Tệp → Lưu cảnh…** (Ctrl+Shift+S) tải một file `<nhân vật>_<ngày>.aas`, giống `.ma` / `.blend`: zip gồm `manifest.json` (định dạng `ai-anim-scene-v1`, mục sổ `work/clips.json` của nhân vật, anim, dự án, dòng POSES) và file thật dưới `files/work/...`:

- `work/rig_lab/chars/<id>.json`, `chars/<id>/` (mesh gốc cm, texture), thư mục tham chiếu (`ref_dir`, `names_from`), trang Rig `work/rig_lab/pages/<id>/`.
- Kho `work/store/<nhân vật>_mesh_lab`, `_rig_lab`, `_studio`; với mỗi anim: kho Pose (`<tiêu đề>_pose_lab`), `<anim>_studio`, model glTF các phiên bản (`work/pose_lab/models/`), file chữ (md, json, txt) trong thư mục anim.
- **Không gói:** video ref, playblast, FBX gốc, kho Review. Cần thì chép tay.

**Tệp → Mở cảnh…** (Ctrl+Shift+O, cũng có ở ô Cảnh trống) đọc manifest trước, báo nếu máy đã có nhân vật đó (sẽ ghi đè), rồi chép file, gộp sổ, thêm dòng POSES còn thiếu và build lại trang Pose / Review. Chỉ nhận đường dẫn trong `work/` (chặn `..`, `work/store/_sys`, file ở gốc `work/`). Mã: `tools/home/scene_file.py` (có CLI `save` / `open --dry`), `tools/studio/modules/scene.js`.

## Cho Claude

Ghi chú review và vòng gửi của `/check_fb` khi chạy cục bộ nằm ở `work/store/<ns>/notes/` và `rounds/`; Pose Lab ở `adjusts/`, `keys/`, `anims/`, `rounds/` (Studio thêm `props/<clip>-<version>`: vật thể phụ của phiên bản, `modules/props.js`); Rig Lab ở `rig/` (`landmarks`, `skin`, `gates`). Đọc trực tiếp các file đó.

## Chưa làm

- Vỏ ứng dụng một cửa sổ, nối dữ liệu Mesh → Rig → Pose → Review, trang Mesh (bước 2–4).
- Xuất FBX/GLB từ kho (Pose Lab đã tự xuất FBX riêng).
- `localStorage` của Rig Lab cho cấu hình không qua kho (chỉ landmarks, skin, gates qua kho).

## Cài đặt Studio (2026-10-29)

Bố cục, panel, cỡ panel, tab dock, Gate, lưới, camera và cài đặt lõi Pose (khoá `studio:`, `poselab:`, `pl:`, `plsec:`) lưu ở `work/store/studio_prefs/prefs/local.json` qua Home server (`core/app.js` nạp đồng bộ lúc mở, ghi lại sau mỗi thay đổi). localStorage chỉ là bản đệm, nên mở bằng `localhost` hay `127.0.0.1`, hay trình duyệt khác trên cùng máy đều nhận cùng cài đặt. Mỗi máy (mỗi Home) một bộ.

Góc camera viewport (mọi khung, kể cả persp đang ortho) lưu cùng chỗ, khoá `studio:view:<workspace>:<nhân vật>`, dò thay đổi mỗi giây. Mở lại / đổi workspace dùng góc đã lưu thay vì tự căn (mesh `loaded`, lõi Pose `setCam("right")`); đổi phiên bản anim giữ nguyên camera.
