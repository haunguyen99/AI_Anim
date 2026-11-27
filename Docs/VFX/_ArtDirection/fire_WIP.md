# Lửa — nháp art direction (CHƯA CHỐT)

Ghi chú làm việc với art lead. Chỉ tích hợp vào skill unity-vfx-maker (references/shape-language.md + make_texture.py) **sau khi art lead chốt**.

Script thử nghiệm (session scratchpad, có thể mất khi hết phiên): fire_tongue.py (lưỡi lửa từ phác thảo), fire_flame.py (lưỡi lửa biên độ cong ngẫu nhiên + ghép), fire_v7.py (ngọn lửa theo line art). Bản sao lưu nằm trong thư mục scripts/ cạnh file này.

## Yêu cầu v1 (2026-10-21)

- Hình khối lửa được **cấu thành từ 3 loại đường cong**:
  1. **Đường cong chữ C**.
  2. **Hình móc câu**: thân vươn ra rồi cuộn lại ở đầu, đầu vót nhọn.
  3. **Đường cong 1/4 hình tròn**: cung khoảng 90° (art lead sửa lại từ "3/4" thành "1/4").
- **Phác thảo của art lead — một lưỡi lửa** ([art/fire_tongue_sketch_v1.png](art/fire_tongue_sketch_v1.png)): silhouette dựng từ 4 đường cong dài, trơn, nối 4 mũi nhọn:
  - mũi trên → mũi phải: **đường cong lồi dài** (C / cung 1/4) làm mép dẫn;
  - mũi phải → mũi phải-dưới: **vết lõm cung 1/4 hình tròn** khoét vào, tạo 2 mũi nhọn ở trên và dưới;
  - mũi phải-dưới → mũi trái: **chữ C lồi lớn** làm đáy (khối nặng nằm dưới);
  - mũi trái → mũi trên: **mép hơi lõm** cong vào trong.
  - Mũi nhọn sinh ra ở chỗ hai đường cong gặp nhau; một đường **vươn quá** đường kia một chút nên mũi quặp lại như **móc câu**.
- **Ảnh chuẩn (ngọn lửa stylized, art lead gửi 2026-10-21)** — cách các thành phần trên kết hợp thành cả ngọn lửa:
  - Cột lửa đứng: đáy rộng có lõi sáng, các lưỡi lửa xếp chồng **nhỏ dần lên trên** (lớn → vừa → nhỏ), trên cùng là vài **mảnh lửa tách rời** nhỏ dần.
  - Mỗi lưỡi lửa là một biến thể của lưỡi lửa phác thảo (xoay, lật, co giãn): mép ngoài là **chữ C**, ngọn **quặp móc câu** (vd mảnh tách rời ở giữa-phải cong như dấu "?"), giữa các lưỡi là **vết lõm cung 1/4** tạo khoảng âm tròn.
  - Các lớp lồng nhau: lưỡi nhỏ hơn, sáng hơn nằm trong lưỡi lớn, tối hơn; khoảng âm tròn tối nằm ở đáy giữa các khối.
  - (Ảnh chuẩn chưa được lưu thành file trong skill; chỉ có mô tả này.)
- **Biên độ cong phải ngẫu nhiên** (art lead xác nhận cách đọc ảnh chuẩn là đúng, rồi bổ sung): không bám cứng theo phác thảo hay ảnh chuẩn. Mỗi đường cong có thể **cong nhiều hơn, cong ít hơn, hoặc đổi chiều cong**; vị trí mũi nhọn cũng xê dịch. Chỉ giữ cấu trúc: chữ C, móc câu, vết lõm cung 1/4 và cách ghép.
- **Không được rối** (art lead nhận xét bản ghép đầu tiên: "các đường cong quá rối"): ít lưỡi lửa, mỗi đường cong dài và trơn; không có răng cưa hay mũi nhọn li ti ở chỗ các lưỡi chồng nhau; không có mảnh vụn nhỏ lọt bên trong thân; không phải lưỡi nào cũng có vết lõm, chỉ vài vết lõm rõ ràng; biên độ ngẫu nhiên vừa phải.
- **Vẽ đè sửa bản ghép** ([art/fire_feedback_overlay_v1.png](art/fire_feedback_overlay_v1.png)): thân lửa chỉ là **vài khối lớn**, mỗi khối viền bằng một đường cong dài liền mạch (lưỡi trên-trái: mũi đỉnh, mép trái hơi lõm; đường lõm cung 1/4 dưới mũi trái; khối giữa mép trên chữ C; đáy chữ C lớn; mép phải thoai thoải). **Chỗ hai khối gặp nhau kết thúc bằng một móc cong nhỏ (hình chữ U)** có chủ đích. Dấu X: **bỏ mọi lỗ thủng / mảnh vụn bên trong thân**. Các đường bên trong là ranh giới chồng lấn giữa các khối (dùng cho lớp sáng tối), không phải vết cắt.
- **Line art chuẩn của art lead** ([art/fire_lineart_v1.png](art/fire_lineart_v1.png)) — tham chiếu chính cho cấu trúc ngọn lửa:
  - Toàn bộ dựng từ **các nét hở**, mỗi nét là C, móc câu hoặc cung 1/4; hình lửa hiện ra từ các nét đó.
  - Viền ngoài: trái là **móc câu** cuộn xuống ở mũi trên-trái nối **chữ C lớn** làm thùy trái; đáy là **chữ C lớn** ôm tròn; phải có **vết lõm cung 1/4** khoét vào sườn, trên đó là một bầu cong.
  - Bên trong: lưỡi lửa giữa có **mép dưới lượn sóng** (chuỗi 2–3 chữ C nhỏ nối nhau); **lõi ở đáy là cụm 3 thùy tròn** như đám mây (vòm lớn giữa + 2 thùy nhỏ hai bên).
  - Mảnh tách rời: một mảnh **thon dài nhọn hai đầu** trên đỉnh, một **lưỡi nhỏ có vết lõm** ở trên-phải.
  - Tỉ lệ: cột cao ~1,5 lần rộng, rộng nhất ở 1/3 dưới.
- Trạng thái: lưỡi lửa đơn đã dựng lại khớp phác thảo; đang ghép thành ngọn lửa theo ảnh chuẩn để art lead duyệt; script chưa cập nhật.

## Kiểu 1 — phần tử lửa đơn cho particle (đang thử)

- Vòng 1 (6 ứng viên A–F, `mode1_fire/`): art lead nhận xét **A và B quá giống nhau** → các ứng viên/biến thể phải khác biệt rõ; **ngọn của E chưa thành đường cong** → ngọn luôn phải là một đường cong, mũi uốn sang một bên (móc câu), không được là mũi thẳng do hai mép gặp nhau.
- Vòng 2 (ngọn uốn cong, 6 dáng khác nhau, loại trùng >80%): art lead xác nhận **hình khối base đã ổn**. Yêu cầu tiếp: **thể hiện mờ và rõ ở các mép shape**. Đề xuất đang thử: ngọn + mép phía uốn ngọn sắc rõ; đáy + mép đối diện mờ dần; chuyển tiếp trơn dọc viền.
- Mép sắc/mờ (art lead sửa đề xuất ban đầu): **mép mờ nằm ở đỉnh các đường cong lõm vào trong** (điểm sâu nhất của vết lõm 1/4, của mép hơi lõm); **càng gần chỗ giao nhau giữa các đường cong (các mũi nhọn) càng sắc dần**. Đường cong lồi ra ngoài và các mũi nhọn giữ sắc.
- Art lead: **tăng độ mờ** và **mờ theo kiểu motion blur** (theo hướng chuyển động — phần tử lửa đi lên, nên kéo vệt dọc trục đứng) thay vì nhoè đều.
- Art lead: tăng thêm độ mờ (motion 0.16 → 0.26 cạnh ô).
- Art lead: đỉnh đường cong vẫn quá sắc → đỉnh mọi đường cong lõm mờ tối đa (tối thiểu 70%), thêm nhoè nhẹ để mép song song hướng chuyển động cũng mềm.
- Art lead tự làm mờ ứng viên F để làm mẫu (`art/fire_element_F_blur_ref.png`): **mờ cả khối** — lõi sáng ở giữa, sáng giảm dần ra mọi mép; đỉnh các đường cong lõm mềm nhất (vùng chuyển rất rộng); mũi nhọn vẫn giữ dáng nhọn nhưng tối dần về đầu mũi; có chút vệt kéo ở đầu mũi theo hướng chuyển động. Cách làm cục bộ từng đoạn mép trước đó "chưa ổn".
- Cách làm mờ mới (đang thử): giữ silhouette làm khung × dải sáng tối bên trong (lõi trắng, tối dần ở mép và mũi hẹp) × nhoè ra ngoài chỉ ở đỉnh cong lõm (motion blur dọc).
- Thông số art lead dùng để làm mờ mẫu F: **Photoshop Motion Blur, Angle 0°, Distance 33 px, áp lên toàn bộ shape** (`art/photoshop_motion_blur_settings.png`). Ảnh mẫu rộng ~287 px → distance ≈ 11,5% chiều rộng ảnh. PS motion blur đối xứng hai phía dọc theo góc. Không nhoè/levels thêm.
- Đã mô phỏng PS Motion Blur (đối xứng, distance 18% kích thước shape): góc 0° khớp gần như hoàn toàn mẫu F của art lead.
- **Quy tắc biên độ cong sửa lại:** vẫn random, nhưng mỗi đường cong là một cung tròn trong khoảng **từ 1/4 đến 1/2 hình tròn** (cung 90°–180°; tỉ lệ độ phồng/dây cung 0,21–0,5). Chiều cong vẫn có thể đảo; vết lõm luôn lõm.
- Art lead: C, D, E cùng cấu trúc nên nhìn giống nhau → đa dạng phải đến từ **cấu trúc khác nhau** (không chỉ biên độ). Đang thử 6 kiểu cấu trúc: cổ điển, giọt nước móc, lưỡi liềm, hai thùy, ba mũi, mép chữ S.
- **Làm rõ (art lead xác nhận):** "C, D, E giống nhau" là vì chúng **sai khung**: 2 đường cong lớn cùng phồng ra ngoài (dáng hạt đậu). Quy tắc: **khung chính của mọi phần tử lửa = 2 đường cong đối diện, một lồi một lõm** (dáng lưỡi liềm / móng vuốt). Đa dạng bằng biên độ, tỉ lệ, hướng quặp và chi tiết phụ (vết lõm 1/4, thùy nhỏ ở đáy, bớt một mũi) — không bằng cách đảo khung.
- **Sửa lại cách hiểu "đối diện" (art lead chọn kiểu 1 trong `mode1_fire/_curve_pairs.png`):** "đối diện" = **) ( lưng đối lưng** — hai đường cong **lõm vào** nằm ở hai phía đối diện của thân, cùng lõm về phía giữa (tạo eo thắt và mũi nhọn). Trong phác thảo: mép sau lõm ")" + vết lõm 1/4 bên hông "(". Hình chỉ có một đường lõm, hoặc hai mép cong cùng một phía như hai cung lồng nhau "((" (ví dụ `art/fire_feedback_not_opposing_*.png`), là **sai**. Mọi phần tử phải có cặp đường lõm lưng đối lưng; đa dạng bằng độ sâu từng đường lõm (1/4–1/2), tỉ lệ, độ cao ngọn, hướng quặp, chi tiết đáy.
- Art lead: đúng quy tắc ) ( nhưng **tổng thể quá mỏng, cần dày hơn** → thân bè hơn, mũi thấp hơn, hai đường lõm nông hơn trong khoảng 1/4–1/2; yêu cầu hình chiếm ≥ ~55% khung bao.
- Art lead: hình E (đáy 2 thùy, có thêm vết lõm thứ 3 ở đáy) **sai cấu trúc** → không thêm vết lõm nào ngoài cặp ) (; chi tiết đáy chỉ là đường cong lồi.

## ✅ Kiểu 1 ĐÃ CHỐT (2026-10-21) — đã tích hợp vào skill

- Preset `fire_element` trong `unity-vfx-maker/scripts/make_texture.py`; quy tắc ở `references/shape-language.md` mục "Lửa — kiểu 1"; ảnh tham chiếu copy sang `references/art/`.
- Phần kiểu 2 (texture sheet cả ngọn lửa theo line art) vẫn là nháp ở trên, chưa chốt.

## Kiểu 2 — texture sheet cả ngọn lửa (đang thử)

- Art lead chọn: **làm cả hai** — bản **cháy liên tục (loop)** trước, rồi bản **bùng lên rồi tan**; lưới **4×4 = 16 frame**; **nhiều tông** (viền tối, vùng giữa sáng hơn, lõi 3 thùy sáng nhất; grayscale → gradient map).
- Khung lấy từ line art `art/fire_lineart_v1.png`; các lưỡi lửa dùng quy tắc phần tử đã chốt (kiểu 1).
- **Nguyên tắc dựng kiểu 2 (art lead, 3 ảnh phác "vòng tròn → viền"):**
  1. Khung xương = **chuỗi 4 hình tròn** xếp từ dưới lên, **so le trái/phải**, nhỏ dần lên trên (1 to nhất ở đáy → 4 nhỏ nhất ở đỉnh). Mỗi hình tròn giữ phía của nó.
  2. **Viền lửa vẽ bao quanh các hình tròn**: mỗi hình tròn một thùy phình, nối bằng eo; ở eo có vết lõm + móc nhỏ (cặp lõm ) ( so le), đôi khi bong bóng phụ nhỏ.
  3. **Lửa bốc lên → các hình tròn trôi dần lên**, nhỏ dần; hình trên cùng ra khỏi đỉnh thì **quay về đáy làm hình to nhất**, thứ tự lặp lại → loop liền mạch.
- **Sửa (art lead):** ảnh phác 3 vẽ nhầm — khi lặp, **quả cầu 4 phải quay về đúng vị trí quả cầu 1**. Vị trí theo **ô** (độ cao) trên một đường zíc-zắc cố định, không theo từng quả cầu. Sheet 16 frame = các quả cầu dịch lên đúng 1 ô → frame 16 nối liền frame 1.
- **Chuyển động quả cầu (art lead mô phỏng, `art/fire_mode2_spine_motion.png`):** 4 quả cầu nằm dọc một **đường xương sống cong hình S**; đường S **tự uốn lượn khác nhau** theo thời gian (ngọn lửa đung đưa mượt, đều). **Toạ độ quả cầu tự do, kích thước random** (không nhất thiết to dưới nhỏ trên). Ràng buộc duy nhất: **frame đầu = frame cuối** để loop.
- **Quyết định (art lead, 2026-10-21):** tạm **bỏ lửa kiểu 2 bằng cách vẽ shape** (chất lượng shape quá thấp). Chuyển sang làm **bằng shader** (code HLSL, chạy Built-in + URP). Phần vẽ shape ở trên giữ làm tham khảo, không tiếp tục.

### Lửa kiểu 2 bằng shader — bản nháp 1 (2026-10-21)
- Shader `VFX/Fire Stylized` (`Assets/VFX/FireStylized/Shaders/SH_VFX_FireStylized.shader`), HLSL CGPROGRAM, Built-in + URP.
- Dáng ngọn lửa tính từ UV (đáy rộng bo tròn, thuôn lên đỉnh, lắc lư) + 2 lớp noise cuộn lên làm méo và ăn mòn -> tách lưỡi lửa, mẩu lửa bứt lên.
- 3 dải màu cel (ngoài / giữa / lõi), mép chống răng cưa.
- Loop liền mạch 2 s (SpeedA 0.5, SpeedB 1.0, SwaySpeed pi); build bake 16 frame 4x4 RGBA để dùng như flipbook.
- Build: menu `VFX/FireStylized/Build`. Sheet: `Docs/VFX/FireStylized/Loop_sheet.png`.
- Quy trình (art lead đề xuất, 2026-10-21): làm lửa bằng shader để có visual tốt nhất → bake texture sheet từ shader để dùng trong sản phẩm (nhẹ hơn); shader vẫn giữ để dùng cho trường hợp khác.
  Menu: `VFX/FireStylized/Build` (tạo prefab/material, bake) và `VFX/FireStylized/Bake Sheet From Material` (bake từ material đang chỉnh, không đổi material).
- Bản 2 (shader defaults): thân rộng 0.45, taper 1.3, erosion 1.15, noise A (2.0, 0.6), B (3.0, 1.2), distortion 0.3, bands 0.11/0.28/0.5, lề ô y 0.05–0.9. Mô phỏng nhanh: `scripts/fire_shader_sim.py` → `mode2_shader/v2/`.
- Sửa màu: project Linear → shader chuyển palette sRGB sang linear (GammaToLinearSpace). Bake chạy được cả trong Play mode (không đổi scene).
- Lưu ý: màu HDR (cường độ > 1) bị cắt về 1 khi bake ra PNG → cam HDR x4.6 thành vàng trong sheet.

### Lửa 3D bằng shader — bản nháp 1 (2026-10-21)
- Art lead: bản 2D quá flat; gắn lên sphere thì shader UV không bọc được khối → làm shader 3D riêng `VFX/Fire Stylized 3D` (`SH_VFX_FireStylized3D.shader`), giữ bản 2D.
- Vertex: kéo mesh lên + bóp đỉnh (giọt lửa), lắc, đẩy theo normal bằng noise cuộn lên. Fragment: "nhiệt" = facing (N·V) + đèn giả (một bên tối hơn) − noise ăn mòn (mạnh ở mép và đỉnh) → 3 dải cel.
- Noise import linear (sRGB off) vì project Linear. Prefab `VFX_FireStylized3D` (sphere). Bake sheet: `Docs/VFX/FireStylized/Loop3D_sheet.png`.
- Thông số hiện tại: Band 0.12/0.3/0.45, Shade 0.8, Pinch 0.7, Displace 0.25, Erosion 0.95, NoiseA (2.5,0.6), NoiseB (4,1.2), Fresnel 0.8.
- Bản 3D-2 (lưỡi lửa): đỉnh tách lưỡi bằng khe cắt quanh trục (5 thùy, độ với so le, hẹp dần thành đầu nhọn), bắt đầu từ h 0.5; mỗi lưỡi với tối thiểu 0.3. Đẩy đỉnh bằng vertex dễ dồn về cực sphere thành 1 gai → chỉ dùng nhẹ (TongueLength 0.15). Stretch 1.3, Pinch 0.45, TongueCut 0.9, TongueSharp 0.8.
- Art lead tự chỉnh material 3D (snapshot file lúc 15:29): Band 0.3/0.3/0.44, Displace 0, NoiseAmount 0.8, Pinch 0.5, Shade 1, Stretch 1.64, TongueCut 0, TongueLength 2, TongueSharp 0.2, HeightRange ±0.4, NoiseA (1,1), NoiseB (2,1), Mid HDR (1.74,0.78,0.14), Outer (1,0.02,0.1).

### Quy trình shader → bake sheet (đang thử trên nhiều loại effect, CHƯA đưa vào skill)
- Art lead (2026-10-21): bake loop 8 frame (4x2), không loop 16 frame (4x4). Thử trên nhiều dạng effect rồi mới chốt quy trình.
- Bộ bake dùng chung: `Assets/VFX/FireStylized/Editor/ShaderSheetBaker.cs` — 2 lượt (đo khung thật trên GPU rồi bake sát khung, lề 6%), trộn các mặt chồng nhau như trong game (shader cần `Blend [_SrcBlend] [_DstBlend], One OneMinusSrcAlpha`), xuất straight alpha.
- Màu: thuộc tính Color thường được Unity tự đổi sang linear → shader KHÔNG tự chuyển; màu [HDR] thì không được đổi (lửa giữ GammaToLinearSpace).
- Lửa 3D: bake lại 8 frame `T_FireStylized3D_Loop_4x2.png` từ material art lead chỉnh (sửa NaN ở cực sphere).
- Khói 3D (`Assets/VFX/SmokeStylized/`, shader `VFX/Smoke Stylized 3D`): sphere → cụm bông (7 thùy cố định + bump nhỏ), normal tính lại từ bề mặt đã biến dạng; 3 tông cel theo đèn giả; _Life 0..1: phồng (ease-out), bốc lên, xoay nhẹ, tan bằng noise lỗ lớn + nhỏ, mép tan mềm hơn theo hướng bay lên. Sheet `T_SmokeStylized3D_Puff_4x4.png`.
- Khói 3D bản 2 (góp ý art lead + ảnh ref cụm cầu tím): đổi sang MESH CỤM CẦU (`SM_SmokeStylized_Cluster`, 14 quả: 2 L / 5 M / 7 S, cùng cỡ không cạnh nhau, xếp dày và bất đối xứng trong mặt phẳng màn hình). Shader: từng quả nở lần lượt từ quả to ra ngoài, cả cụm tỏa rộng (spread 0.45→1.6) và bốc lên; sáng từ lõi cụm (mặt hướng vào tâm sáng, mặt ngoài tối) + key light; 4 tông cel; clip khi tan để không ghi depth.
- Lỗi đã gặp: CopySerialized vào mesh asset có sẵn không cập nhật GPU → xóa và tạo lại asset mỗi lần build.
- 3 noise dissolve (`scripts/dissolve_noises.py`, tileable, linear): Cells (Worley có trọng số L/M/S), Streaks (sợi dọc theo hướng bay lên), Chunks (vài mảng lớn). Menu `VFX/SmokeStylized/3D - Bake Dissolve Variants` → `Docs/VFX/SmokeStylized/Puff3D_dissolve{Cells,Streaks,Chunks}.png`.
- Art lead: 3 phương án dissolve theo noise (Cells/Streaks/Chunks) chưa ổn → cần nét dissolve STYLIZED. Shader: mép cắt sắc (chỉ fwidth), bỏ noise hạt vụn, m = lerp(noise, facing^p, _DissolveFacing) để tan theo hình khối từng quả; thêm viền màu chạy theo mép tan (_EdgeWidth, _EdgeColor). 3 look: RimBite (cắn từ mép, viền tối), HoleLine (lỗ tròn, viền sáng), Blobs (vỡ thành cục tròn, dải bóng trong). Sheet: `Docs/VFX/SmokeStylized/Puff3D_style*.png`.
- Art lead: tan "theo khối từ trong ra". Thử 1: đảo facing từng quả → quả bị khoét rỗng thành vòng tròn (vì mặt sau bị cull) → bỏ. Thử 2: theo cả cụm, lõi trước (CoreOutCells/CoreOutBlobs).
- Video ref của art lead (vụ nổ khói cel đỏ nâu): KHÔNG dùng noise — mỗi khối bị một hình tròn "tẩy" lớn ăn từ một phía → còn lại mảnh trăng lưỡi liềm đầu nhọn; quét theo hướng (dưới-trái → trên-phải), so le theo vị trí; mép trơn; tối dần khi tan. → shader thêm `_EraseMode` (Crescent): tâm tẩy = tâm quả (view space) lệch về phía nguồn quét × _EraseOffset, xoay ngẫu nhiên _EraseJitter, bán kính lớn dần; thời điểm theo vị trí dọc hướng quét (_SweepSpread). Sheet `Puff3D_styleCrescent.png`.
- Art lead chọn Crescent; yêu cầu xếp lại bố cục khối tròn. Bố cục mới (theo video): một khối gom tròn (elip 1.15 x 0.98), vòm về phía camera; 2 L ở giữa-trên, 5 M quanh, 7 S ở mép/đáy; lệch một bên. Crescent đặt mặc định trong Build (EdgeWidth 0.04, viền tối, DissolveStart 0.35, ToneNoise 0.12); tan kéo tới frame cuối (lp / (1.08 - t0)); bỏ vòng viền quanh lỗ tẩy mới mở. Sheet chính `T_SmokeStylized3D_Puff_4x4.png` đã bake lại.
- Art lead: bố cục "khối gom tròn" KHÔNG đúng ý → quay lại bố cục cụm bám nối bất đối xứng (bản đã duyệt cùng Crescent, seed 7). Giữ: Crescent mặc định, tan tới frame cuối, bỏ vòng viền lỗ mới, ToneNoise 0.12. Sheet chính đã bake lại.
- Art lead: quay về kiểu dissolve TRƯỚC khi tham khảo video → mặc định = CoreOut (Cells, DissolveFacing 0.6, RimPow 0.8, InsideOut 1, EdgeWidth 0.05 viền tối, DissolveStart 0.4, ToneNoise 0.35), bố cục cụm bất đối xứng. Crescent vẫn còn trong shader (_EraseMode) để dùng sau.
- Art lead xác nhận: CoreOut là dissolve mặc định cho khói (2026-10-21). Chưa đưa vào skill.
- Art lead: bố cục lớn trong / nhỏ ngoài, tan từ quả nhỏ trước; tỏa ra nhưng không để các quả cách xa (lộ khối, rời rạc). → đặt quả L trước rồi M, S bám ra ngoài (khoảng cách mong muốn tới tâm 0.22/0.68/1.05, chồng 0.55–0.68), SpreadEnd 1.3; thứ tự tan theo cỡ (_SizeStagger 0.4, nhịp tuyến tính, cut tới 0.8 ở frame cuối), EdgeWidth 0.03, DissolveStart 0.2.
- Art lead (2026-10-22): bố cục quá dài → cân bằng hướng đặt quả quanh tâm (ưu tiên phía còn thưa, hướng đều mọi phía) cho shape tròn hơn, vẫn bất đối xứng. Unity đóng → build bằng batchmode: -executeMethod VfxEffects.SmokeStylized3DBuild.BuildBatch.
- Art lead: khoảng cách các quả gần hơn → chồng 0.46–0.58, khoảng cách mong muốn 0.18/0.55/0.88, SpreadEnd 1.2; thêm ràng buộc rộng ≈ cao của cả cụm (tránh cụm dài).
- Art lead gửi phác shape khói (art/smoke_shape_sketch_v1.png): thân lớn + ~7 thùy tròn to quanh, khía lõm giữa thùy, tổng thể tròn. Build có UseSketchLayout = true: 8 hình tròn fit từ bản phác (pixel → unit, k = 1.1/340), jitter nhẹ. Random layout giữ làm phương án dự phòng.
- Art lead: tan dồn hết vào mấy frame cuối. Đo diện tích/frame (scratchpad coverage.py): trước 100%@f10 → 0%@f14. Sửa: nhịp inverse-smoothstep, _CutRange (0.38, 0.7) khớp dải mask của các thùy nhìn thấy (CoreOut: thùy ngoài ~0.4–0.65), cụm tỏa xong sớm (ease-out bậc 3, GrowLate 0.08), DissolveStart 0.3 → đỉnh f8 rồi giảm đều: 100/95/84/72/58/43/26/3%.
- Art lead (2026-10-23): khói bản hiện tại "tạm ổn" (shape theo bản phác + CoreOut + nhịp tan đều). Chưa chốt, chưa đưa vào skill.
