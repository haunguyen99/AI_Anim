# Ngôn ngữ hình khối VFX (nghiên cứu web + board Pinterest của người dùng)

Tổng hợp ngày 2026-10-21. Nguồn: blog Flash FX (họa sĩ FX 2D), VFX Apprentice (tóm tắt style guide của Riot, khóa Elemental Foundations), các thread phê bình trên RealTimeVFX, phân tích phong cách Kanada (fullfrontal.moe, animetudes), Clip Studio Tips, MediBang, 80.lv, animeoutline.com, cùng board Pinterest "VFX" của người dùng (https://pin.it/6aCxO2A0G). Các con số đánh dấu *(suy ra)* là ước lượng để tham số hóa, không phải số liệu được công bố. Ghi chú: *Elemental Magic* là sách của Joseph Gilland, không phải Jason Keyser.

## Nguyên tắc chung

- **Một khối chính mang thông tin, các khối phụ tối hơn và nhạt hơn.** Khối chính có độ tương phản cao nhất. Không phải thứ gì cũng quan trọng. (Riot qua VFX Apprentice)
- **Ít khối, khối to, nét đậm; có dày có mỏng.** Tránh chi tiết li ti và nhiễu tần số cao, tránh xếp chồng quá nhiều lớp làm hình bị đục. (VFX Apprentice style guides; RealTimeVFX hit spark critique)
- **Nhịp lớn / vừa / nhỏ cho cả khối đặc và khoảng âm (lỗ, khe).** Tránh đối xứng, hình tròn đều. Tỉ lệ khối chính : phụ : chi tiết ≈ 1 : 0,5 : 0,2; để ~30–50% texture là khoảng âm *(suy ra)*. (VFX Apprentice Elemental Foundations)
- **Trộn mép cứng và mép mềm.**
- **Góc càng nhọn càng nguy hiểm/mạnh; tròn là an toàn** (hồi máu không được trông như đòn đánh).
- **Giá trị sáng tránh 0 và 100 tuyệt đối** cho khối phụ; dải sáng tối rộng nhất dành cho khối chính. Vẽ grayscale rồi tô màu bằng gradient map. (Riot; Overwatch Pharah study)
- **Càng về cuối càng ít chi tiết.** Hình đang vỡ chuyển từ khối lớn sang khoảng âm; thiết kế phải chắc ở mọi frame. (RealTimeVFX explosion critique; Chris Graf / Toon Boom)
- **Sinh ra rõ, chết rõ, không kéo dài.** "Effect cảm thấy dài là quá dài." Phong cách anime giữ frame (24–30 fps, trộn 1s và 2s).

## Yêu cầu của art lead (ưu tiên cao nhất)

Do người dùng (art lead) đưa ra cho từng loại effect. Khi mâu thuẫn với phần nghiên cứu bên dưới hoặc số đo thư viện, **làm theo mục này**.

### Hai kiểu làm effect (art lead, 2026-10-21) — áp dụng cho mọi loại

1. **Một ảnh cho particle random:** texture là **một phần tử đơn** (vd một lưỡi lửa). Particle System random xoay, kích thước, màu, vị trí để ghép thành effect. Phần tử phải đọc được ở mọi góc xoay và không rối khi chồng nhiều lần.
2. **Texture sheet chạy frame by frame:** mỗi frame là **cả effect đã ghép sẵn** (vd cả ngọn lửa theo line art), biến đổi qua các frame.

Làm lần lượt từng kiểu, theo thứ tự art lead chọn.

Quy trình: yêu cầu hình khối đang thử nghiệm được ghi nháp ở `D:\Game_prj\VFX_LIb\Docs\VFX\_ArtDirection\` (vd `fire_WIP.md`); chỉ đưa vào file này và vào `make_texture.py` **sau khi art lead chốt**.

### Lửa — kiểu 1: phần tử đơn cho particle (ĐÃ CHỐT 2026-10-21)

Preset: `make_texture.py fire_element` (mặc định đã có mờ; `--sharp` cho bản cứng; `--look` chọn 1 trong 6 dáng: balanced, deep_bite, deep_back, waisted, even_pair, low_wide). Không làm flipbook cho phần tử này.

- **Gốc từ phác thảo của art lead** ([art/fire_tongue_sketch_v1.png](art/fire_tongue_sketch_v1.png)): một lưỡi lửa có 4 mũi, nối bằng 4 đường cong.
- **Khung bắt buộc: 2 đường lõm "lưng đối lưng" `) (`** ([art/curve_pairs_back_to_back.png](art/curve_pairs_back_to_back.png), kiểu 1): mép sau lõm vào và một vết lõm bên hông lõm vào từ phía đối diện, cùng lõm về phía giữa thân. Mép trước lồi, đáy lồi.
  - Sai: chỉ có một đường lõm; hai mép lớn cùng cong một phía như hai cung lồng nhau `( (` (dáng lưỡi liềm mảnh); hai mép cùng phồng ra (dáng hạt đậu); thêm vết lõm thứ ba (ví dụ đáy chia 2 thùy).
- **Biên độ cong:** mỗi cạnh là một cung tròn từ **1/4 đến 1/2 hình tròn** (90°–180°), random trong khoảng đó; không cạnh nào thẳng hay cuộn quá nửa vòng.
- **Ngọn:** mũi nhọn, **uốn cong sang một bên** (móc câu), không phải mũi thẳng do hai mép gặp nhau.
- **Độ dày:** thân đầy đặn, không mảnh (hình chiếm ≥ ~64% khung bao của nó).
- **Đa dạng:** khác nhau ở độ sâu từng đường lõm, tỉ lệ thân, độ cao ngọn, hướng quặp. Các biến thể phải khác dáng rõ ràng; không tạo đa dạng bằng cách phá khung.
- **Mờ:** **Photoshop Motion Blur áp lên toàn bộ shape**, đối xứng; art lead dùng Angle 0°, Distance 33 px trên shape dài ~180 px → distance ≈ **18% kích thước shape** ([art/photoshop_motion_blur_settings.png](art/photoshop_motion_blur_settings.png), mẫu: [art/fire_element_F_blur_ref.png](art/fire_element_F_blur_ref.png)). Không dùng nhoè đều (Gaussian) hay làm mờ cục bộ từng đoạn mép.
- Hình nằm giữa ô, phủ ~88% ô, nền đen, trắng 1 tông (màu do particle tint).

## Lửa (nghiên cứu web)

- Silhouette **rộng ở đáy, hẹp ở ngọn**, tách thành vài mũi nhọn; các lưỡi kề nhau nghiêng khác hướng. (animeoutline)
- Hình đổi theo chu kỳ **S → C → S**; mũi lửa đổi hướng so với frame trước. (Flash FX #12)
- Có **khối lõi tròn gần như đứng yên** (lửa ổn định: ~80% thể tích ở lõi). Lửa phun ra: phồng như bong bóng, tuôn ra, tan, rồi đáy phồng lại.
- **Mảng tách rời**: tách ở ~60–80% chiều cao, co lại và biến mất trong 3–5 frame *(suy ra)*, trong khi thân vẫn bốc lên đều.
- **Ít lưỡi lửa nhưng to**, silhouette dạng tam giác bất quy tắc; nhiều lưỡi nhỏ đều nhau, hình vuông vức là lỗi phổ biến. (RealTimeVFX campfire critique)
- Tông: khối vàng nằm trong khối cam; Kanada dùng vàng, cam, đen cùng một chớp trắng, khối lửa góc cạnh di chuyển như sóng. Trong texture vẫn giữ 1 tông trắng, màu do layer tint.

## Khói

- **Các khối cuộn chồng lên nhau**, không phải một đường viền phình to; bóng nằm ở chỗ khối đè khối và phía khuất sáng. (Flash FX; Elemental Foundations)
- Hai họ: **sợi khói** (hành xử như lửa) và **khói cuộn** (như mây).
- Dựng một silhouette tổng đơn giản trước, rồi chia đường cong lớn thành múi nhỏ; múi to nhỏ ngẫu nhiên; vệt khói thì đáy rộng, ngọn hẹp, múi nhỏ dần về ngọn. **Tránh puff tròn đều.**
- **Lớn nhanh rồi chậm**: 3 hình đầu chiếm gần hết độ lớn (ease-out mạnh).
- **Tan**: mở một lỗ chính trước (nhanh rồi chậm), lỗ phụ nhập vào, khe lan ra mép; giữ vài cụm sống thêm vài frame; mảnh nhỏ dần, thưa dần rồi co về không. Nhiều puff chồng nhau thì lệch thời điểm 4–5 frame.
- Khói sống lâu hơn lửa, nuốt lửa và tối dần.

## Điện

- Dựng từ **các đoạn thẳng góc ngẫu nhiên** quanh một đường dẫn; phân cấp thân → nhánh → nhánh con; nhánh ngắn hơn, mảnh hơn, thon dần tới hết. **Quá nhiều nhánh trông rối chứ không mạnh.** (Clip Studio 7688; HitFilm)
- Thân 5–9 đoạn, góc rẽ 20–60° và thỉnh thoảng gãy gắt 90–150°; độ dài đoạn 0,5–1,5× trung bình; **tránh zíc-zắc đều** *(suy ra)*. 1–3 nhánh, tách 20–45°, dài 20–50% thân *(suy ra)*.
- Nét dày ở gốc, **thắt mảnh ngay sau mỗi góc gãy**, vót về 0 ở đầu. Chỉ thân chính có viền tối; nét mảnh không viền. Glow là bản blur cộng thêm. (MediBang)
- Board của người dùng: nhiều **nét móc cong ngắn hình chữ C/hook**, hai đầu vót như nét cọ; vệt ngang có nhánh li ti.
- Qua các frame: mỗi frame một hình mới, hoặc với tia cố định thì chỉ đổi hình 1–2 lần đầu; thêm một **frame trống** cho mạnh; **nhánh nhỏ tắt trước, thân chính sống lâu hơn** (nhánh con → nhánh → thân đứt khúc → lõi mảnh dần).

## Impact / hit spark

- Vụ nổ **gai nhọn, sáng**; các mảnh bắn thẳng ra nhiều hướng; trắng → đen → tắt dần, không tắt đột ngột. (RealTimeVFX 11286)
- 4–8 gai chính, khoảng cách và góc **cố ý không đều**; độ dài theo nhịp lớn/vừa/nhỏ: 1–2 gai ≈1,0, vài gai 0,5–0,7, gai nhỏ 0,2–0,35; chân gai ≈15–25% chiều dài; lõi tròn nhỏ bên dưới *(suy ra)*.
- Board của người dùng: burst gai tam giác dài ngắn không đều, có **mảnh vụn tam giác văng ra**, viền màu.
- Sóng xung kích phụ không được sáng/dày/lâu hơn sự kiện chính.

## Slash

- Sáng nhất sát lưỡi kiếm, có highlight; trail một màu trông yếu; trail lơ lửng một chút trong lúc bị ăn mòn.
- Lưỡi liềm dày nhất ở ~30–40% dọc cung (gần đầu dẫn); đuôi vót dài, đầu vót ngắn; **mép ngoài cứng sáng, mép trong mềm và rách**; ăn mòn từ đuôi về đầu *(suy ra)*.
- Board của người dùng: mép rách gồ ghề, sọc bên trong, mảnh vụn nhỏ tách ra dọc mép.

## Shockwave

- Mép trong và mép ngoài biến thiên (khoảng cách, đoạn cong/thẳng, góc gãy), hoặc gradient tròn cắt bằng noise.
- Lớn nhanh rồi chững lại, không tuyến tính; tắt nhanh hơn sự kiện chính. Mép ngoài sắc sáng, mép trong mờ vào; bề rộng vành 5–15% bán kính, mỏng và đứt dần khi lan.

## Glow / sparkle

- Glow là lớp cộng riêng, quầng mềm lớn. Sparkle 12 frame: độ mờ 0 → 100% ở giữa → 0, scale đỉnh ở giữa, xoay 90° trong đời sống.
- Sao 4 cánh **hai trục không bằng nhau** (vd 1,0 và 0,6) *(suy ra)*; board của người dùng thêm một vệt flare ngang dài mảnh.

## Những lỗi cần tránh

- Nhiều lưỡi/múi nhỏ đều nhau; hình vuông vức; hình tròn hoặc đối xứng.
- Nhiễu dày đến tận cuối; dải sáng tối đầy đủ trên khối phụ.
- Quá nhiều nhánh/lớp; effect kéo dài.
