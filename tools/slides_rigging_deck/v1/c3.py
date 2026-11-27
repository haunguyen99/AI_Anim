# ===== BƯỚC 6 Skin
std('Bước 6 · Skin (1/5)','Skin: da của nhân vật bám vào xương bao nhiêu phần',[
 blk('Để làm gì','Mỗi đỉnh của mesh phải "nghe lời" một hoặc vài joint. Đó là skin. Mức nghe lời là <b>weight</b>, tổng luôn 100%.'),
 blk('Luật gốc',ul('Chỉ bám joint DEF, tối đa 4 joint mỗi đỉnh','Mảnh cứng (giáp, mắt, gậy): 100% một joint','Joint xa không được kéo: tay chân không kéo thân')),
 blk('Windy','Thân + đầu + áo choàng skin vào các joint của team. <b>Gậy skin 100% vào một joint riêng</b> (joint112) nên gậy bay tự do được.')],
 [('img/rig/d_skinrule.svg','Weight là gì, và Windy áp dụng ra sao.','sch'),('img/rig/steam_weights.jpg','Steam Pug: bản đồ weight, mỗi chấm một đỉnh, màu là joint điều khiển nhiều nhất.','real')],fw=1.2,mh=300)
std('Bước 6 · Skin (2/5)','Cổng duyệt: thử xoay từng khớp ở góc thật',[
 blk('Bạn xem gì','AI xoay từng khớp (vai, khuỷu, hông, gối, cổ, thân) ở góc animator hay dùng, <b>nhìn bằng mắt</b> bằng camera cận.'),
 blk('Dấu hiệu skin ổn','Da gập tự nhiên, không phình, không thót hình nêm, không dính vào bộ phận khác.'),
 blk('Số đo','Độ co giãn cạnh lưới chỉ để tham khảo. Số đẹp vẫn có thể che lỗi mắt thấy.')],
 [('img/rig/nb_skin_before.jpg','Night Bat, bản thử đầu (12/11 10:36): cánh phình, tai kéo méo, màng cánh dính vào mặt.','real'),('img/rig/nb_skin_after.jpg','Cùng 9 pose, bản thử thứ 13 (14:17): cánh gọn, tai và đầu tách nhau.','real')],fw=1.5,mh=560,row=True)
std('Bước 6 · Lỗi AI hay mắc (3/5)','Vai, ống tay, khuỷu',[
 err('Lỗi thật · Nova','Xoay vai thì ống tay thót hình nêm vì mép dưới ống tay còn bám thân. Sửa: vertex tay chỉ bám Shoulder (và Elbow gần khuỷu).'),
 err('Lỗi thật · Hero RPG2','Khuỷu hở 4,1 cm khi gập 57°. Lần 1 AI kéo cả bắp tay theo khuỷu thì tay móp (71 cạnh xấu). Sửa đúng: chỉ phần nằm trong ống giáp = 100% joint của ống.'),
 err('Lỗi thật · Hero RPG2','Bả vai không theo Scapula (20 / 79 đỉnh, trung bình 4%). Sửa lên 53 / 79 đỉnh, 21%.'),
 fix('Bạn làm gì','Nói rõ <b>góc xem</b> và <b>khớp nào móp</b>. AI đo trên phần nhìn thấy, đừng đo cả phần nằm trong ống.')],
 [('img/rig/d_elbow.svg','Khuỷu hở khi gập: đầu bắp tay trượt khỏi ống giáp.','sch'),('img/rig/d_scapula.svg','Scapula bám bả vai trước và sau khi sửa.','sch')],dark=True,fw=1.3,mh=300)
std('Bước 6 · Lỗi AI hay mắc (4/5)','Chân móp, và sửa quá tay cũng móp',[
 err('Lỗi thật · Hero RPG2','"Tay không móp mà chân móp": 74 / 545 đỉnh chân ăn sai joint. Chân dùng dải chiều cao tự đặt thay vì bám vị trí khớp như tay.'),
 err('Lỗi thật · Hero RPG2','Làm mịn weight quá tay: sau gối co từ ×0,45 xuống ×0,29. Hạ 2 lượt và bỏ qua vùng sau gối, đáy quần.'),
 blk('Giới hạn thật','Lưới thưa thì không thể hết hẳn móp. Gập đùi trên 60° hay cúi thân 40° bằng một khớp: animator nên chia góc cho nhiều joint.')],
 [('img/rig/d_stretch.svg','Độ co giãn trước và sau khi sửa. Dòng 3 là lỗi ngược do làm mịn quá.','sch'),('img/rig/steam_leg.jpg','Steam Pug: thử gập chân 6 góc, nhìn cận đùi và gối.','real')],dark=True,fw=1.3,mh=300)
std('Bước 6 · Lỗi AI hay mắc (5/5)','Lỗi ngầm: nhìn pose gốc thì ổn, chạy anim mới vỡ',[
 err('Lỗi thật · Night Bat','Người dùng báo "cánh dính vào mặt, tai" <b>4 lần</b>. Gốc không phải weight: skin được bind lúc một control đang lệch. Tai nối cánh bằng mặt dài nên skin không tách nổi, phải tách tai thành mesh riêng.'),
 err('Lỗi thật · London','Joint <b>root</b> có skin: 277 / 1199 đỉnh. Root dời thì thân méo.'),
 fix('Bạn làm gì','Bảo AI: "<b>mọi control về 0 trước khi bind</b>", và kiểm root không có skin trước khi xuất.')],
 [('img/rig/nb_skin_side.jpg','Night Bat nhìn bên: cánh và tai chồng vào khối đầu ở nhiều pose.','real'),('img/rig/d_root.svg','Joint root có skin ở các file đã quét.','sch')],dark=True,fw=1.3,mh=235)
# ===== BƯỚC 7 Picker
std('Bước 7 · Picker','Picker: bảng nút để chọn control cho nhanh',[
 blk('Để làm gì','Animator bấm nút trên bảng thay vì mò control trên model.'),
 blk('Bạn xem gì để duyệt',ul('Bấm từng nút = đúng control','Không nút nào đè nhau','Nút All chứa mọi control')),
 err('Lỗi thật · Hero RPG2','Đổi cỡ control 3D mà không đổi nút picker: "kích cỡ control thân ở picker vẫn chưa thay đổi". Hai vòng sửa vì không đồng bộ.')],
 [('img/rig/d_picker.svg','Bố cục picker đã duyệt (Hero, 57 nút): đỏ = phải, xanh dương = trái, vàng = thân.','sch')],fw=1.5)
# ===== BƯỚC 8 Kiểm rig
std('Bước 8 · Kiểm rig','Thử rig như animator sẽ dùng, không chỉ đọc số',[
 blk('Để làm gì','Phát hiện lỗi trước khi animator mất công làm anim trên rig hỏng.'),
 blk('Bạn xem gì để duyệt',ul('Thử đủ <b>4 tay chân</b>, IK và FK','Đổi frame rồi pose gốc phải đứng yên','Texture đúng trên viewport','Windy: xoay tay xem gậy có theo, xem áo choàng')),
 blk('AI phải báo','Cái nào <b>chưa kiểm</b> (chưa vào Unity, chưa playblast, chưa kiểm xuyên mesh).')],
 [('img/rig/d_check.svg','Kiểm đủ 4 chi × IK / FK. Kiểm cũ chỉ thử tay trái nên sót.','sch')],fw=1.3)
std('Bước 8 · Lỗi AI hay mắc','AI báo "xong" khi chưa thử hết',[
 err('Lỗi thật · rig 2026-11-02','Group rìu constrain vào cổ tay DEF làm cổ tay thôi chạy. Kiểm rig báo sạch vì mặc định chỉ thử tay <b>trái</b>.'),
 err('Lỗi thật · Hero RPG2','Hàm thử đưa control về 0 nên <b>xoá mất pose bạn đang thử</b> (2 lần), và trả công tắc sai thứ tự làm tay IK trái về 0.'),
 err('Lỗi thật · Pet mesh v2','Rig không về dáng gốc: bind lệch gối 2,1 cm, kênh control "chết" giữ giá trị lệch. Phiên con không tự thấy, người phải bắt.'),
 err('Lỗi thật · MeoTom','Hậu: "rig chưa ổn", "mọi joint sai". AI báo xong khi chưa soi control và joint từng cái bằng số.')],
 [('img/rig/d_autosnap.svg','Thứ tự trả công tắc sau khi thử, để không mất pose của bạn.','sch')],dark=True,fw=1.1)
# ===== BƯỚC 9 Xuất FBX
std('Bước 9 · Xuất FBX','Xuất file cho Unity: Base và file anim khác nhau',[
 blk('Hai loại file',ul('<b>Base</b> = xương + mesh','<b>File anim</b> = chỉ xương + clip, không mesh')),
 blk('Quy tắc','Chỉ xuất khi bạn nói <b>"chốt"</b>. Vòng sửa và góp ý không xuất file.'),
 blk('Windy','Dùng kiểu Generic: giữ tên và cây xương của team, chỉ xuất xương và anim. Đã xuất thử khớp 0 cm với FBX của team.')],
 [('img/rig/d_export.svg','Các bước xử lý FBX trước khi vào Unity.','sch')],fw=1.5)
std('Bước 9 · Lỗi AI hay mắc','FBX từ Frolvy vào Unity bị vỡ',[
 err('Lỗi thật · Pebble Turtle','Base vỡ skin: đầu và chân bay khỏi thân (Unity lấy bind pose từ cluster, Frolvy không ghi BindPose). Sửa: thêm BindPose, bỏ clip tĩnh khỏi Base.'),
 err('Lỗi thật · Pebble Turtle','File anim lỗi "Cannot find root motion transform": file chỉ có một nút gốc. Sửa: thêm Null "Dummy" cùng cấp, chỉ ở file anim.'),
 err('Lỗi thật · Night Bat','Joint ma, node thừa trong FBX vì Frolvy luôn ghi cả scene. Sửa: lọc sau khi xuất, giữ cây root + mesh.'),
 fix('Bạn làm gì','Bảo AI <b>chạy kiểm bằng Unity chạy nền</b> và đọc log import. Có lỗi mới thì đọc log, không đoán.')],
 [('img/rig/d_bindpose.svg','Hai lỗi vào Unity: thiếu BindPose và thiếu nút Dummy.','sch')],dark=True,fw=1.0)
# ===== PHẦN C
raw('''<p class="kick">Phần C · Dùng ngay</p><h2>Thấy gì thì nghi lỗi nào</h2>
<table style="font-size:24px"><tr><th style="width:30%">Bạn thấy</th><th style="width:30%">Thường là do</th><th>Làm gì</th></tr>
<tr class="hl"><td>Mesh móp khi xoay một khớp</td><td>Weight sai vùng, vertex bám joint xa</td><td>Nói rõ khớp và góc; AI thử lại bằng mắt, camera cận</td></tr>
<tr><td>Mặt, tai dính vào cánh, mảnh khác</td><td>Bind lúc control đang lệch, hoặc mesh hàn liền</td><td>Control về 0, bind lại; hoặc tách mảnh</td></tr>
<tr class="hl"><td>Rig nghiêng dù control = 0</td><td>Rebuild khi đang lệch pose</td><td>Control về 0 rồi Rebuild; kiểm pivot</td></tr>
<tr><td>Control ẩn, to quá, lệch hai bên</td><td>Vẽ control không theo mesh</td><td>Liệt kê cỡ, so trái phải</td></tr>
<tr class="hl"><td>Joint nằm sai chỗ khớp</td><td>AI đặt theo tâm hình khối</td><td>Xem 3 góc, tự dời tay rồi nói AI giữ nguyên</td></tr>
<tr><td>Vào Unity: mesh vỡ hoặc lỗi gốc</td><td>Thiếu BindPose, thiếu nút Dummy</td><td>Chạy bước xử lý FBX, kiểm Unity</td></tr>
<tr class="hl"><td>AI báo xong mà bạn vẫn thấy sai</td><td>Chưa kiểm hết (4 chi, đổi frame)</td><td>Bắt AI liệt kê cái chưa kiểm</td></tr></table>''')
std('Phần C · Dùng ngay','Cách nói với AI để nó làm đúng',[
 '<div class="say"><b>Giao việc:</b> "Rig nhân vật Windy trong Frolvy. Chỉ joint base, Root ở hông. Dừng ở bước đặt joint, chụp 3 góc gửi mình duyệt."</div>',
 '<div class="say"><b>Góp ý:</b> "Điểm Chest hạ xuống 4 cm, HeadEnd về đỉnh đầu. Giữ nguyên chỗ mình đã sửa, chỉ đặt lại các joint con."</div>',
 '<div class="say"><b>Bắt kiểm:</b> "Thử đủ 4 tay chân, IK và FK, đổi frame xem pose gốc có đứng yên. Báo cái nào chưa kiểm."</div>',
 '<div class="say"><b>Chốt:</b> "Chốt rig. Xuất Base và file anim, kiểm trong Unity."</div>'],
 [('img/windy/w_beforeafter.png','Ví dụ góp ý chính xác: nêu <b>điểm nào</b>, <b>sửa bao nhiêu</b>, <b>hướng nào</b>.','wd')],fw=1.2,mh=460)
raw('''<p class="kick">Phần C · Dùng ngay</p><h2>Checklist duyệt rig (12 mục)</h2>
<div class="row"><div class="card"><ul><li>Lưới đã kiểm, retopo xong nếu cần</li><li>Joint đặt ở điểm xoay, đã xem 3 góc</li><li>Root ở hông, không helper, twist</li><li>Chuỗi vải, đuôi, tai theo đúng hình</li><li>Control ôm mesh, không ẩn, không quá to</li><li>Hai bên trái phải đối xứng</li></ul></div>
<div class="card"><ul><li>Skin chỉ DEF, tối đa 4 joint, không lẫn bên</li><li>Root không có skin</li><li>Đã xoay vai, khuỷu, hông, gối, cổ, thân bằng mắt</li><li>Pose gốc đứng yên khi đổi frame</li><li>Picker khớp control, không nút đè nhau</li><li>AI ghi rõ cái chưa kiểm</li></ul></div></div>
<p class="note">Gửi checklist này kèm mỗi bản rig để người duyệt biết đã kiểm tới đâu.</p>''',dark=True)
raw('''<p class="kick">Phần C · Dùng ngay</p><h2>Bẫy của Frolvy: lỗi của công cụ, không phải của AI</h2>
<div class="row"><div class="card err"><span class="lab">Xoá nhầm mesh</span><p>Xoá khi đang ở chế độ đỉnh / mặt thì xoá nhầm mesh khác, Ctrl+Z không lấy lại (Hero 2026-10-31). Luôn về chế độ object trước khi xoá.</p></div>
<div class="card err"><span class="lab">Undo lẫn việc bạn làm</span><p>Hoàn tác nhiều bước có thể lùi quá việc bạn đã làm. Sửa tiến, kiểm lại sau undo.</p></div>
<div class="card err"><span class="lab">Cổng nhầm cửa sổ</span><p>Cổng chết thì lệnh tự nhảy sang cửa sổ Frolvy khác, không báo. Kiểm scene sau mỗi lần Frolvy khởi động lại.</p></div></div>
<div class="row"><div class="card err"><span class="lab">Lưu, mở file</span><p>Lưu đè file đã có thì báo False; mở file khi scene đang sửa thì báo False và lệnh nhập sau đó chồng vào scene rig.</p></div>
<div class="card err"><span class="lab">Xoá joint</span><p>Giữ vị trí cục bộ của con (cả cây nhảy lên), xoá nhãn cha. Skin vẫn trỏ joint đã xoá sau Rebuild: lưu weight trước.</p></div>
<div class="card"><h3>Gặp lỗi của Frolvy</h3><p>Ghi một dòng: Lỗi / Cách thấy / Mong muốn. Hỏi bạn rồi mới gửi cho đội phát triển.</p></div></div>''')
