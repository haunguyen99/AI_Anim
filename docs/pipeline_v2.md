# Quy trình diễn hoạt bằng AI — v2 (Blender-first, animator-first)

*Bản thiết kế lại sau các vòng thử: MediaPipe, fit silhouette, tool key tự viết, layer trong keys.json, và cuối cùng là key Idle_Breath trong Blender qua MCP.*

## 0. Rút kinh nghiệm: vì sao các bản trước chưa đạt

| Hướng đã thử | Vấn đề gốc |
|---|---|
| MediaPipe / pose estimation | Chỉ dùng được cho người. Boss gorilla cầm chùy thì không nhận ra. |
| Fit silhouette mỗi frame | Coi ref là mocap. Ref AI/vẽ tay tự nó đã lệch tỉ lệ và rung, nên fit càng khớp pixel thì anim càng "máy". Kết quả: rung, mất feel. |
| Tool key tự viết (keys.json + viewer three.js) | Không có rig thật, không có graph editor, constraint tự viết hay vỡ (tay xuyên đầu, chùy ngược). Mỗi lần sửa phải bake lại. Người dùng không tự chỉnh tay được. |
| Key trong Blender (Idle_Breath) | **Đúng hướng:** có control rig, IK chân và tay, chùy gắn vai, người dùng bấm Space là xem được và chỉnh tay được. Chỗ còn thiếu: chưa có quy trình. Mình nhảy thẳng vào key spline, chưa có bước duyệt blocking, và chưa có QA tự động. |

**Kết luận:** AI không nên là "máy tracking" mà phải là **animator dùng công cụ thật**. Ref là *acting reference*: lấy ý đồ, timing và biên độ từ đó, không lấy pixel.

## 1. Nguyên tắc

1. **Hiểu trước, key sau.** Mọi clip bắt đầu bằng bản *phân tích chi tiết từng bộ phận* (tổng quan hành động + từng bộ phận), có số đo đi kèm.
2. **Blender là môi trường làm việc duy nhất.** Mình điều khiển qua MCP, người dùng xem và chỉnh tay trong cùng một file. Không còn bake qua lại giữa các công cụ.
3. **Animate trên control rig, không trên xương deform.** IK, follow space và prop được dựng tự động, có kiểm tra.
4. **Pose-to-pose như studio:** Blocking (stepped) → duyệt → Spline → Polish → duyệt. Sửa ở blocking rẻ hơn sửa ở polish rất nhiều.
5. **Layer bằng NLA.** Pose gốc, nhịp thở và cú liếc là các lớp riêng, dùng chung giữa các clip (Idle_LookAround tái dùng lớp thở của Idle_Breath).
6. **Đo những gì đo được, mắt người cho những gì còn lại.** QA tự động bắt lỗi kỹ thuật (trượt chân, xuyên, khựng loop, rung). Feel thì do người dùng duyệt.
7. **Mỗi góp ý của người dùng đều thành dữ liệu:** frame, bộ phận, vấn đề, cách sửa. Bài học chung được ghi vào skill.

## 2. Quy trình 7 bước, 3 cổng duyệt

```
 1 Intake ─► 2 Đọc ref & Brief ─►[DUYỆT 1]─► 3 Rig & Scene ─► 4 Blocking ─►[DUYỆT 2]
          ─► 5 Spline & Layer ─► 6 QA tự động + Playblast ─►[DUYỆT 3]─► 7 Export
                      ▲                                          │
                      └──────────── góp ý (frame/bộ phận) ◄──────┘
```

### Bước 1 — Intake (checklist, 5 phút)
- Model + rig (FBX), ref các góc, fps, xác nhận tên góc (góc nào là trái/phải của *nhân vật*).
- Engine đích (Unity), camera game, cách chia clip (loop hay one-shot, in-place hay root motion).
- Ref là AI, vẽ tay hay render? Ref AI/vẽ tay thì chỉ dùng cho timing và ý đồ.
- **Tên góc nghiêng:** xác định bằng hướng mặt nhân vật trong file, không theo tên file. Nhân vật nhìn sang **phải** màn
  hình nghĩa là camera đang thấy **sườn phải** của nó. Với playblast Gaygor: `_left.mov` là camera bên phải nhân vật,
  `_right.mov` là camera bên trái. Ghi vào `refs.json` (khóa `left`/`right` = phía của nhân vật) và thêm cả `top`.
- **Mỗi clip một file Blender, mỗi file một cổng MCP** (người dùng chọn 2026-10-20): cổng lưu trong scene
  (`scene.blendermcp_port`, `blendermcp_auto_start_server`), mỗi cửa sổ tự bật server khi mở file; thêm một server vào
  `.mcp.json` cho mỗi cổng (Idle 9876 = `blender`, Attack 9877 = `blender_attack`), khởi động lại phiên Claude Code để nạp.
  Nhờ vậy cửa sổ đang có thay đổi chưa lưu của clip khác không bị đụng tới. Việc dựng file nặng thì chạy `blender -b` (nền).
- **Đầu ra:** `work/<job>/intake.json`.

### Bước 2 — Phân tích ref chi tiết đến từng bộ phận  ▸ **DUYỆT 1**
Đây không còn là một bản brief ngắn. AI đọc ref như một animator đang *break down* shot: xem từng bộ phận ở mọi góc, qua từng đoạn của clip.

**Cách đọc**
- Contact sheet mọi góc, xem trọn clip, sau đó **zoom từng bộ phận**: crop quanh bộ phận đó ở 4 góc, ghép thành dải theo thời gian (mỗi 2–3 F một ô).
- **Đo song song (thuật toán):** dùng optical flow theo *vùng* trên ref (khung chậu, ngực, từng vai, đầu, cẳng/bàn tay, đầu gối, bàn chân, prop) để ra đường cong cao/thấp, trái/phải và trước/sau. Từ đó tự tìm extreme, hold, biên độ (cm/độ) và độ trễ giữa các vùng. Đo trên ref là ổn vì ref có texture; không đo trên render workbench.
- Mắt (Claude) đọc cái thuật toán không đọc được: hướng xoay, trục xoay, twist, cách bàn tay nắm, độ căng hay thả lỏng, ý đồ. Số đo dùng để chốt frame và biên độ.
- **Số đo đáng tin trên playblast cùng rig** (Attack): đỉnh silhouette theo frame; dải tiếp đất (hàng pixel sát sàn) ở 3 góc
  để biết bàn chân nào bước, bước bao xa, frame nào nhấc và đặt; độ rộng từng hàng ở góc top/góc bên để biết prop chĩa đi đâu
  và xa bao nhiêu. Optical flow theo hộp cố định cho số vô lý khi người nằm sấp, nên bỏ.
- **Đọc bằng ảnh lớn**: mỗi pose then chốt một ảnh 5 góc độ phân giải cao (`analysis/poses/pNN.png`). Không đọc góc từ crop nhỏ
  (bản v3 sai 20–40°). Ghi nhãn nguồn cho mọi số: **[đo]** / **[mắt]** / **[chưa đo]**.

**Đầu ra 1: Tổng quan hành động** (`analysis.md`, phần A)
- Anim là gì: loại (idle, attack…), loop hay one-shot, in-place hay root motion, độ dài, cách chia clip.
- Nhân vật đang làm gì và vì sao (bối cảnh, động cơ), **feel** (trọng lượng, tâm trạng, tính cách).
- Các **pha** của hành động trên timeline, mỗi pha một dòng: frame bắt đầu–kết thúc, chuyện gì xảy ra, bộ phận nào dẫn dắt.
- Trọng tâm và cân bằng: trọng lượng dồn vào đâu và di chuyển thế nào qua các pha.
- Những gì **không** chép: rung pixel, lệch tỉ lệ, lỗi của video AI hoặc vẽ tay.

**Đầu ra 2: Hành động chi tiết của từng bộ phận** (`analysis.md`, phần B, kèm `analysis.json`)

Đi lần lượt theo chuỗi, từ gốc ra ngọn:

| Nhóm | Bộ phận |
|---|---|
| Thân | Root/khung chậu → bụng (Spine1) → ngực (Chest) → cổ → đầu (cả hàm và mắt nếu rig có) |
| Tay trái / phải | Xương bả vai → cánh tay trên → khuỷu và cẳng tay → cổ tay và bàn tay → ngón |
| Chân trái / phải | Hông → đùi → gối → cổ chân → bàn chân và ngón |
| Prop / phụ kiện | Vũ khí, áo choàng, tóc, đuôi, tai, vạt áo/khố, dây đeo, mặt vòng… |

**Kiểm kê phụ kiện trước khi phân tích** (góp ý người dùng, 2026-10-20): chạy `legacy/blender/rig_inventory.py` để liệt kê
mọi xương ngoài thân/tay/chân (chain tóc, đuôi, tai, áo choàng, vạt vải, đồ treo) và mọi mảnh mesh rời gắn cứng (giáp, trang sức).
Nhận diện từng cái bằng vùng mesh nó điều khiển và ảnh model, không tin tên xương. Với mỗi cái ghi: số đốt (1 đốt = xoay một khối,
nhiều đốt = cần overlap theo chuỗi), chuyển động thấy trên ref, độ trễ so với xương cha, tác động trọng lực, chỗ dễ xuyên mesh
(vạt khố ↔ đùi khi nhấc chân, đồ treo ↔ ngực khi gập người). Chuyển động phụ không có trong ref thì ghi là đề xuất để người dùng chọn.

Mỗi bộ phận ghi theo cùng một mẫu:
1. **Trạng thái ở pose gốc P0:** hướng, góc gập, độ căng hay thả lỏng, quan hệ với bộ phận khác (ví dụ: tay trái nắm cán chùy cách đầu chùy 1/3, lòng bàn tay úp).
2. **Chuyển động theo từng pha:** xoay quanh trục nào của nhân vật, theo hướng nào; tịnh tiến bao nhiêu; frame bắt đầu, đỉnh và kết thúc; biên độ (độ/cm, đo được hoặc ước lượng, có ghi rõ là loại nào).
3. **Vai trò:** chủ động (tự sinh chuyển động), bị động (bị kéo theo, follow-through) hay ổn định (bù ngược để giữ yên, như đầu giữ ánh mắt).
4. **Quan hệ thời gian:** trễ hay sớm bao nhiêu frame so với bộ phận dẫn; overlap; settle sau khi dừng.
5. **Chất lượng chuyển động:** ease-in/out, arc, overshoot, giữ (hold) hay trôi (moving hold).
6. **Ràng buộc:** điểm tiếp xúc phải cắm cố định (bàn chân, tay trên cán), giới hạn khớp, chỗ dễ xuyên mesh.
7. **Ghi chú animator:** điều cần giữ, điều cần bỏ so với ref, và độ tin cậy (thấy rõ ở góc nào, góc nào bị che).

`analysis.json` là bản số của phần B, để các bước sau dùng trực tiếp:
```jsonc
{"clip": "Idle_Breath", "frames": 30, "phases": [{"name": "exhale", "f": [1, 20]}, ...],
 "parts": {
   "Root_M":  {"role": "active", "P0": "...",
               "motion": [{"ch": "loc.z", "keys": {"1": 0, "7": 0.5, "25": -1.7}, "unit": "cm", "src": "measured"}]},
   "Chest_M": {"role": "follow", "lag_of": "Root_M", "lag_f": 2,
               "motion": [{"ch": "rot.x", "keys": {"9": 0.8, "17": 2.0, "28": 0}, "unit": "deg", "src": "eye"}]},
   "Weapon":  {"role": "passive", "attached": "Scapula_L", "constraint": "hand_L on shaft"}
 }}
```

- Người dùng duyệt **cả hai phần** trước khi đụng vào rig. Sửa phân tích rẻ hơn sửa key rất nhiều.

### Bước 3 — Rig & Scene (tự động + tự kiểm tra)
- **Hiệu chỉnh camera bằng lưới nền của ref** (nếu có): đo khoảng cách lưới (px/ô = px/m), giao điểm lưới làm gốc tọa độ, đường lưới làm sàn. Không dùng chiều cao nhân vật để suy ra tỉ lệ. Bài học Idle: ước theo chiều cao ra 206 px/m, lưới cho đúng 201 px/m; sai 2.5% và 8 px này làm hỏng mọi bước sau. Kiểm chứng: dùng một anim đã biết (nếu có) phải đạt IoU ≥ 0.95.
- `setup_scene.py`: nạp model, camera ortho Ref_* đã hiệu chỉnh, ref làm background, MCP tự khởi động.
- `build_ctrl_rig.py` (tổng quát hóa từ bản Boss), cấu hình bằng `rig_profile.json` (chuỗi chân, chuỗi tay, prop gắn vào đâu, tay nào nắm prop):
  - chân IK + foot cắm sàn + knee pole;
  - prop có follow space chuyển được (vai, ngực, tay, world);
  - tay nắm prop dùng IK tới điểm grip nằm trên prop;
  - ẩn helper, tô màu control, gom bone collection (Body / IK / Prop / FK).
- **Khai báo trục và giới hạn khớp cho từng model** (đề xuất của người dùng, bắt buộc ngay sau khi dựng rig), lưu ở `work/<job>/joint_limits.json`:
  - **Trục:** trục dọc xương, trục bản lề, trục phụ. Với rig FBX kiểu Maya này, trục dọc là −X, khuỷu/gối là bản lề quanh **Z** (đo lại ở Attack: phần xoay thêm của khuỷu
    nằm đúng trục Z), ngón cong quanh Y; trục Y của Blender **không** nằm dọc xương. Gập khuỷu trái là −Z, khuỷu phải +Z.
  - **Giới hạn mỗi khớp:** xoắn (twist), gập theo trục bản lề, gập theo trục phụ. Ví dụ: khuỷu là bản lề, xoắn ±50, gập phụ ±10; cổ tay gập ±75, lệch ngang ±45, xoắn ±50; gối là bản lề.
  - `legacy/blender/joint_limits.py` báo mọi khớp vượt giới hạn ở từng key. Lỗi xoắn 169° ở khuỷu trái của Idle là thứ bước này bắt được ngay.
  - Khi đặt tay hay chân bằng IK, dùng `fk_left_arm` trong `grip_set.py`: độ xoay bắp tay suy từ mặt phẳng gập, khuỷu là bản lề thuần, độ ngửa/sấp chia đều cho khuỷu và cổ tay. Không ép hướng bàn tay bất chấp cẳng tay.
- **Tự kiểm tra rig:** độ lệch khi dựng < 0.5 cm / 1°; hạ hông 4 cm thì chân trượt 0 cm; cổ tay trượt trên prop 0 cm; không có vertex của thân nằm trong prop ở pose gốc.

**Clip mới của một nhân vật đã có P0 được duyệt (cách làm Attack v4):**
1. Hiệu chỉnh camera **riêng cho clip** từ lưới của chính ref đó (mỗi playblast có thể khác zoom/vị trí). Kiểm chứng: đỉnh
   silhouette P0 trùng ref, sàn lệch ≤ 3 px, và tâm tính ra ở 2 góc đối diện phải trùng nhau (front/back, left/right).
2. Dựng scene bằng `blender -b` từ file đã duyệt, không mở đè cửa sổ đang làm việc (`work/blender/build_attack_v4.py`):
   copy rig CTRL + P0, đặt lại camera Ref_* theo lưới, gắn ref (cả Ref_top), action mới chỉ chứa P0, CONSTANT.
3. So P0 với frame 1 của ref (`legacy/blender/sil_render.py` + `legacy/blender_tools/sil_compare.py`). Nếu cần, so 2 ref với nhau trên cùng lưới
   để biết frame đầu của clip có đúng là P0 cũ không.
4. Sửa rig theo nhu cầu clip, trong file của clip: prop bay quanh người hay nằm trên đất → `CTRL_weapon` sang không gian
   world (`rig_attack_v4.py`); tay thứ hai nắm prop → thêm IK (`add_arm_ik_R.py`, influence key 0/1). Chuỗi IK dựng từ tay gần
   duỗi thẳng không có mặt phẳng gập → căn roll CTRL theo trục bản lề khuỷu và khóa IK quanh trục đó
   (`rig_attack_v4_armR_hinge.py`). Kiểm tra: P0 với IK bật lệch ≤ 0.1 cm; ở một pose gập mạnh, phần xoay thêm của khuỷu chỉ
   quanh trục bản lề.
5. **Kiểm tra chiều gập của rig ở rest** cho từng tay/chân: rig Gaygor gập khuỷu trái về **sau** trong rest (khuỷu phải về
   trước), nên "xoắn vai trái so với rest" lệch ~180° theo quy ước. Ghi vào `joint_limits.json`; đừng tin bảng góc xoắn
   cho tay trái.
6. **Vệ sinh dữ liệu pose**: kênh scale không có key nên mọi sai số do gán ma trận (trộn scale 0.01 của object FBX) tích luỹ
   qua các lần dựng → quaternion 0 → người lật 180°. Đặt lại scale = 1 sau mỗi lần gán ma trận xương, làm sạch scale ở P0
   (giữ nguyên vị trí/hướng) rồi key lại f1. Xoá key thì xoá luôn f-curve rỗng (curve rỗng đọc ra 0). Kiểm tra scale = 1
   và không có quaternion 0 trước khi lưu.

### Bước 4 — Blocking (interpolation CONSTANT)  ▸ **DUYỆT 2**
- **P0 dựng từ dưới lên: thế đứng trước.** Đo vị trí từng bàn chân (trước/sau, trong/ngoài), hướng hông và hướng ngực ở góc top và góc nghiêng, rồi mới tới cột sống, đầu, tay, prop. Không mặc định là đứng chính diện. Bài học Idle: bản gốc xoay hông 20°, chân so le 50 cm, còn P0 của mình đứng chính diện, nên mọi sửa chữa sau đó chỉ là bù sai (xem `work/idle/original/report.md`).
- Key pose gốc P0 trước, đối chiếu overlay ở 4 góc (`live_render` + `blender_overlay`).
- Key các *extreme* và *breakdown* theo `analysis.json` (từng bộ phận, từng pha), để **stepped**: người dùng thấy rõ từng pose và timing, chưa bị spline che lỗi.
- Playblast stepped kèm ref ở bên cạnh → người dùng duyệt pose và timing.
- **Công cụ đã có (chạy lần đầu trên Idle):**
  - `legacy/blender/solve_keys.py`: giải 19 kênh animator cho mỗi key (hông, cúi/ngả, xoay thân, quay/ngẩng/nghiêng đầu, nghiêng cổ, bả vai, tay phải, xoay và dời chùy), sao cho điểm trên model đi giống vùng tracking trên ref. Dùng damped Gauss-Newton.
  - `legacy/blender/sil_refine.py`: tinh chỉnh bằng silhouette ref, có số hạng riêng cho chùy (đỉnh `_VK` lọt ra ngoài mask).
  - `legacy/blender/head_refine.py`, `legacy/blender/photo_refine.py`: thử nghiệm cho đầu, gồm silhouette đầu ở góc nghiêng và so gradient ảnh. Chưa đáng tin.
  - `legacy/blender_tools/playblast_compose.py`: ghép video ref | anim ở 4 góc.
- **Nhìn bằng mắt trước, tối ưu sau** (góp ý của người dùng): đặt REF cạnh ANIM ở **cả góc top và góc game** nếu có. Góc front và góc nghiêng che mất lỗi theo chiều sâu. Ở Idle, góc top lộ ra ngay rằng chùy nằm sau vai và bàn tay lơ lửng cách cán 11 cm. Công cụ: `legacy/blender/eye_pose.py` + `legacy/blender_tools/eye_compare.py` (đặt cạnh nhau), `legacy/blender/eye_part.py` + `legacy/blender_tools/eye_outline.py` (viền riêng một bộ phận lên ref), `legacy/blender_tools/eye_blend.py` (chồng cạnh). Đặt tay cầm tường minh bằng `legacy/blender/grip_set.py`, theo trục cán đo từ mesh chùy chứ không theo xương.
- **Bài học cũ:** kiểm tra **P0 bằng silhouette trước tiên**. Ở Idle, chùy trong P0 dựng bằng mắt lệch khoảng 15–17 cm, nên mọi key đều kế thừa sai số này.
- Bước này rẻ: đổi một pose chỉ là key lại một frame.

**Dựng từng pose blocking (cách làm Attack v4, `work/blender/attack_pose.py`):**
- **Chế độ dựng pose:** trong lúc dựng, action được tháo ra để không gì ghi đè pose chưa key (render, đo, đổi frame đều làm
  Blender tính lại animation). `goto(f)` đọc pose đã key thẳng từ f-curve; `key_pose(f)` gắn action, key, tháo lại;
  `unkey(f)` xoá key (và curve rỗng); `done()` ở cuối **mỗi** lần gọi MCP để trả file về trạng thái bình thường cho người dùng.
  Mỗi pose là một hàm dựng (`work/attack/pose_fNN.py`) bắt đầu bằng `from_p0(f)` (frame f nhưng mang pose P0), vì các phép
  xoay/dời đều tương đối: dựng trên pose đã key sẽ cộng dồn. Kiểm tra: dựng lại = pose đã key (lệch 0).
- **Thứ tự** (mỗi bước so REF | ANIM 5 góc bằng `eye()` + `tools/eye_side.py`, có `--band` để zoom chân; ảnh chồng 2 màu
  `tools/eye_diff.py` cho biết HƯỚNG sai, `tools/extent_cmp.py` cho biết sai bao nhiêu mét theo từng hàng/cột):
  1. Chân + hông: vị trí bàn chân lấy từ dải tiếp đất [đo]; hướng hông đọc bằng mắt (góc nào thấy mặt trước/sau của khố).
  2. Prop: trục và vị trí **đo** từ phần prop ló ra khỏi thân ở góc top và góc bên (`set_weapon(hướng, điểm giữa)` theo trục mesh,
     không theo xương); kiểm lại bằng độ rộng từng hàng ref so với anim.
  3. Thân + đầu: độ cao đo được (`body_top`: đỉnh đầu từ vertex của đầu) chốt độ gập; xoắn đọc bằng mắt từng góc
     (camera nào thấy ngực, camera nào thấy lưng). Silhouette không phân biệt được xoắn thân (18 thử nghiệm, IoU 0.64–0.67).
  4. Tay trên prop: **giải, không ép** — `solve_grip` (điểm nắm trượt quanh/dọc cán, khuỷu bản lề, cổ tay chỉ lệch nhỏ
     quanh tư thế nắm P0, khuỷu ở ngoài thân, gợi ý từ ref như "tay trái đỡ dưới, khuỷu thấp"), rồi chấm lại các phương án tốt
     nhất bằng độ giãn da thật (`arm_strain`, so với P0). Tay phải gần duỗi thẳng mới với tới → dời vai (xoắn/nghiêng ngực,
     đầu bù) chứ không bẻ tay.
  5. Nhìn cận từng tay (`closeup`, camera ortho tạm, 4 hướng) đặt cạnh bản trước; chỉ gửi người dùng khi không còn khớp véo,
     xoắn kiểu giấy kẹo, cổ tay gập quá hay giáp bị vặn.
- **Gửi duyệt từng pose một**, kèm: ảnh REF | ANIM 5 góc, ảnh cận 2 tay, IoU từng góc, đỉnh đầu so với ref, độ giãn da so với P0,
  các khớp vượt giới hạn và lý do giữ lại. Ghi mọi lần thử sai vào `analysis.md` mục E.

### Bước 5 — Spline & Layer
- Chuyển sang Bezier. Loop dùng **F-curve Cycles modifier** (tiếp tuyến ở chỗ nối tự khớp, không còn phải "f31 = f1" bằng tay).
- Cấu trúc NLA:
  ```
  Track "Base"    : P0 (pose giữ, 1 frame)
  Track "Breath"  : Breath_cycle  (Additive, cyclic)    ← dùng chung cho mọi idle
  Track "Look"    : Look_A        (Additive)            ← chỉ có trong Idle_LookAround
  ```
- **Công cụ "đạo diễn" (mới), thao tác trên curve thay vì key lại:**
  - `offset_chain(bones, frames)`: dời pha để tạo overlap/follow-through (hông → ngực → vai → tay).
  - `scale_amp(bones, k)`: tăng hoặc giảm biên độ ("thở sâu hơn 20%").
  - `ease(bones, frame, in/out)`, `hold(bones, f0, f1)`, `overshoot(bones, frame, deg)`.
  - Góp ý kiểu "vai nhấc mạnh quá" hay "đầu quay chậm hơn" được dịch thẳng ra một lệnh, không phải viết lại cả script key.

- **Bài học polish (Idle):**
  - Overlap là **dời key** theo chuỗi (`direct.py offset_bone`, quấn vòng loop), lấy độ trễ từ bản phân tích ref.
  - Đừng bake thành key từng frame rồi cộng chuyển động thêm, vì sẽ giật.
  - Chỉnh hằng số (ví dụ xoắn khiên) bằng phép nhân quaternion trên key gốc, và giữ dấu quaternion nhất quán giữa các key.
  - Sau mỗi lần đổi giá trị key phải gọi lại `match_seam`, nếu không chỗ nối loop sẽ có gai.
  - Đo độ giật bằng gia tốc/jerk và so với bản gốc khi có.

### Bước 6 — QA tự động + Playblast  ▸ **DUYỆT 3**
`qa_report.py` chạy trong Blender live và in ra bảng PASS/FAIL:

| Kiểm tra | Ngưỡng |
|---|---|
| Trượt chân (vị trí ankle world, mọi frame) | < 0.3 cm |
| Tay rời prop | < 0.3 cm |
| Xuyên mesh: thân ↔ prop, tay ↔ đầu (BVH) | 0 vertex sâu > 1 cm |
| Nối loop: vị trí và vận tốc ở frame N → 1 | Δv < 5% |
| Rung: gia tốc góc bất thường | không có spike |
| Timing và biên độ từng bộ phận so với `analysis.json` | peak lệch ≤ 2 F, biên độ trong khoảng 70–130% (ý đồ, không phải pixel) |
| Arc: đường đi của đầu, tay và đầu prop | không gãy góc |
| Giải phẫu tay: độ giãn da vai/khuỷu/cổ tay (`arm_strain`, p95) + nhìn cận từng tay | không vượt P0 đã duyệt quá 10%; không thấy véo/vặn |
| Dữ liệu pose: scale mọi xương, quaternion | scale = 1; không có quaternion 0; không có f-curve rỗng |

- **Playblast** (render nhanh): ref | anim ở 4 góc + camera game, xuất **WebM** (VP9, nhẹ hơn mp4 khoảng 5 lần) → `review.webm`.
- **Trang review cho team** (artifact kiểu SyncSketch, `work/review_page/`): mỗi version mới được thêm vào danh sách
  clip. Người review tua từng frame, kéo timeline, zoom, vẽ khoanh, ghi chú theo **frame, bộ phận, vấn đề**,
  sửa/xoá ghi chú của mình, rồi bấm **"Gửi feedback cho AI"** để chốt vòng review.
- **Chu kỳ lắng nghe** (quy định của người dùng):
  1. Đưa version lên trang review → **bật lắng nghe**: kiểm tra trang 10 phút một lần (vòng `rounds` có trạng thái "sent").
  2. Nhận được vòng feedback → **tắt lắng nghe**, chuyển vòng sang "AI đang sửa" kèm ghi chú đang sửa gì.
  3. Sửa theo ghi chú (nhìn bằng mắt trước, đo, sửa, QA), playblast, đưa version mới lên trang, đánh dấu ghi chú
     "Đã sửa", chuyển vòng sang "AI đã sửa xong" kèm tóm tắt, trả lời trong thread comment.
  4. Quay lại bước 1 với version mới.
  Mở phiên mới thì kiểm tra ngay các vòng "sent" còn tồn và bật lại lắng nghe nếu có version đang chờ review.
- Trước khi gửi bản sửa, tự xem lại tác dụng phụ: làm chậm pha này có thể làm nhanh pha khác. Báo tốc độ tối đa của từng
  bộ phận trước/sau khi sửa.

### Bước 7 — Export Unity
- Bake NLA thành một action cho mỗi clip, chỉ giữ xương deform, rồi xuất FBX (mỗi clip một take, hoặc chung một file kèm danh sách clip).
- Kiểm tra lại: import lại FBX và so từng frame với bản trong Blender (lệch < 0.1 cm).

## 2B. Quy trình B — từ blocking của người dùng (duyệt 2026-10-23)

Khi người dùng hoặc team đưa FBX đã có blocking của chính rig đó (không có video ref), file blocking là chuẩn về pose và
timing. AI không dựng lại pose mà làm tiếp từ đó:

```
 1 Nạp FBX → Pose Lab ─►[KHỚP FILE]─► 2 Phân tích nhân vật + đòn ─►[DUYỆT PHÂN TÍCH]─► 3 Sửa lỗi blocking
   ─► 4 Pose chuyển tiếp ─► 5 Trọng lượng ─►[DUYỆT 75%]─► 6 Spline + polish (nướng, QA, playblast) ─►[DUYỆT POLISH]─► 7 FBX
```

Chi tiết từng bước, lệnh và các luật rút ra: `.claude/skills/ai-animation/knowledge/details/user_blocking.md`. Clip mẫu:
Gaygor Attack 50 Blocking (`work/gaygor_attack_50_blocking/`). Không dùng Blender: Pose Lab là nơi xem và chỉnh pose,
Review Lab là nơi xem chuyển động, FBX được ghi bằng cách thay đường cong trong chính file của team.

## 2C. Quy trình C — chỉ có yêu cầu bằng lời (thêm 2026-10-24)

Không có ref, không có blocking, chỉ có yêu cầu kiểu "Gaygor bị đánh trúng". Mọi pose và nhịp đều là thiết kế, nên các cổng
duyệt sớm và rẻ (chữ, ảnh tĩnh) đứng trước chuyển động:

```
 C1 Intake gộp ─► C2 Bản thiết kế + bảng timing ─►[DUYỆT THIẾT KẾ]─► C3 Pose kể chuyện 10% (Pose Lab) ─►[DUYỆT POSE]
   ─► C4 Blocking 25–50% ─►[DUYỆT BLOCKING]─► nhánh B bước 3–7 (sửa lỗi, pose chuyển tiếp, trọng lượng, polish, FBX)
```

Chi tiết, luật thiết kế và các phần còn thiếu: `.claude/skills/ai-animation/knowledge/details/text_brief.md`.

## 3. Phân vai

| Việc | Ai làm |
|---|---|
| Đo timing, biên độ, độ trễ từ ref | Thuật toán (optical flow theo vùng) |
| Hiểu ý đồ, phân tích từng bộ phận, chọn pose | Claude (vai Senior Animator) |
| Dựng rig, kiểm tra rig | Script tự động |
| Key blocking, spline, layer | Claude qua MCP |
| Bắt lỗi kỹ thuật | `qa_report.py` |
| Duyệt feel, timing, pose | **Người dùng**, ở 3 cổng duyệt |
| Chỉnh tay bất kỳ lúc nào | Người dùng trong Blender. Claude đọc lại key và không ghi đè. |

## 4. File và công cụ

```
legacy/blender/
  setup_scene.py      (có sẵn)     scene + camera Ref_* + background ref
  build_ctrl_rig.py   (tổng quát hóa) control rig theo rig_profile.json
  anim_helpers.py     (có sẵn)     rotate_char / move_char / key
  live_render.py      (có sẵn)     render qua Ref_*
  direct.py           (MỚI)        offset_chain, scale_amp, ease, hold, overshoot
  nla_layers.py       (MỚI)        dựng Base/Breath/Look, bake clip
  qa_report.py        (MỚI)        bảng QA
  playblast.py        (MỚI)        review.mp4 (ref | anim, 4 góc + game cam)
  export_unity.py     (MỚI)        bake + FBX + kiểm tra import lại
  rig_inventory.py    (Attack)     kiểm kê xương phụ + mảnh mesh rời trước khi phân tích
  sil_render.py       (Attack)     render silhouette qua Ref_* (chạy nền)
  eye_views.py        (Attack)     render 5 góc pose hiện tại (live)
tools/ref_timing.py   (MỚI, từ motion_compare2)  ref → số đo từng vùng cho analysis.json
tools/part_strips.py (MỚI)        crop từng bộ phận ở 4 góc thành dải theo thời gian
legacy/blender_tools/sil_compare.py  (Attack)     IoU + overlay silhouette anim/ref
tools/eye_side.py     (Attack)     REF | ANIM cùng khung, viền anim trên ref, IoU, --band để zoom
tools/sweep_score.py  (Attack)     chấm các thử nghiệm render thấp phân giải
work/blender/attack_pose.py (Attack) chế độ dựng pose: goto/key_pose/unkey/done, eye, closeup, body_top, set_weapon,
                      solve_grip/apply_grip, arm_strain, clean_scales — dùng lại cho clip mới (đổi ACTS)
work/blender/build_attack_v4.py, rig_attack_v4*.py  dựng scene + sửa rig cho clip mới từ file đã duyệt
work/<job>/ intake.json, analysis.md, analysis.json, rig_profile.json, qa.json, review.mp4
```

Các công cụ cũ (keyanim, fit/*, viewer three.js) được giữ làm lưu trữ, không còn nằm trong quy trình chính.

## 5. Áp dụng ngay cho Boss Idle

0. Làm lại Bước 2 cho ref Idle theo mẫu mới: tổng quan hành động + phân tích từng bộ phận (`work/idle/analysis.md`, `analysis.json`) → Duyệt 1.
1. Idle_Breath hiện có → tách thành lớp NLA `Breath_cycle` (Additive + Cycles modifier).
2. Viết `qa_report.py` và chạy trên Idle_Breath để có số liệu nền (trượt chân, xuyên chùy, nối loop).
3. Nhận góp ý của bạn cho Idle_Breath, rồi sửa bằng `direct.py`.
4. Idle_LookAround: tái dùng `Breath_cycle` cộng lớp `Look_A`, chạy đủ các bước Blocking → Duyệt 2 → Spline → QA → Duyệt 3.
5. Export cả hai clip cho Unity.
