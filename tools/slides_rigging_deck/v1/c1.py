# ===== PHẦN A
raw('<p class="kick">Art Animation · Rigging 3D</p><h1 style="margin-top:auto">Rigging 3D bằng AI<br>trong Frolvy</h1><p style="max-width:1400px;color:#c9d6ea;margin-bottom:auto">Hướng dẫn từng bước cho người chưa biết gì về 3D animation. Ví dụ xuyên suốt: nhân vật <b style="color:#F0B13B">Windy</b>, thầy phù thủy gió cầm gậy.</p>',dark=True)
S[-1]=S[-1].replace('<section class="dark"','<section class="dark on" style="justify-content:center;gap:40px"')
std('Phần A · Hiểu từ số 0','Rigging là gì? Lắp xương và dây vào con rối',[
 blk('Ví von con rối',ul('<b>Model</b> = vỏ con rối: chỉ là một cái vỏ cứng, chưa cử động được','<b>Joint</b> = khớp xương bên trong vỏ','<b>Skin</b> = lớp da ôm quanh xương, xương xoay thì da xoay theo','<b>Control</b> = sợi dây bạn giật để con rối cử động')),
 blk('Rigging là gì','Lắp xương, gắn da và nối dây vào model. Xong rig thì animator kéo dây (control) để nhân vật cử động.')],
 [('img/windy/w_mesh.png','<b>Windy chưa rig:</b> chỉ là vỏ (mesh). Cao 185 cm, cầm gậy.','wd'),('img/windy/w_joints_front.png','<b>Windy có joint:</b> các chấm vàng là khớp xương đặt bên trong vỏ.','wd')],fw=1.3,mh=560,row=True)
std('Phần A · Hiểu từ số 0','Rig nằm ở đâu trong quy trình làm game',[
 blk('Chuỗi việc',ul('Có <b>model</b> do artist tạo','<b>Rig</b>: lắp xương, da, dây điều khiển (việc của tài liệu này)','<b>Animator</b> kéo control để tạo chuyển động','Xuất file <b>FBX</b>, đưa vào Unity để game chạy')),
 blk('Vì sao quan trọng','Rig sai thì anim đẹp mấy cũng méo: tay móp, mặt dính vào cánh, chân trượt. Rig đúng thì animator làm nhanh và ít lỗi.')],
 [('img/rig/d_pipeline.svg','Rigging là bước nối giữa model và animation.','sch')],fw=1.5)
terms('Phần A · Từ cần biết (1/2)','Năm từ đầu tiên',[
 ('Joint','Khớp xương. Chấm vàng trong model, nơi một bộ phận xoay.','img/windy/w_joints_front.png','Windy: joint vai, khuỷu, gối…','object-position:50% 40%'),
 ('Control','Cái bạn kéo / xoay trong Frolvy. Nó điều khiển joint.','img/rig/mecha_ctl.jpg','Mecha Pup: các vòng màu quanh thân','object-position:50% 50%'),
 ('Skin / Weight','Cách "da" của model bám vào joint. Weight là mức bám (phần trăm).','img/rig/nb_skin_after.jpg','Night Bat: cùng một rig, 9 pose thử','object-position:50% 50%'),
 ('Bind','Dán da vào xương lần đầu, ở tư thế đứng yên (mọi control = 0).','img/rig/steam_weights.jpg','Steam Pug: màu = joint điều khiển','object-position:50% 50%'),
 ('IK / FK','FK: xoay từng khớp. IK: kéo bàn tay, cả tay gập theo.','img/rig/d_ikfk.svg','Hai cách điều khiển một cái tay','object-fit:contain;padding:6px')])
terms('Phần A · Từ cần biết (2/2)','Năm từ tiếp theo',[
 ('DEF','Joint dùng để skin (xương thật của game). Chỉ joint DEF được xuất ra.','img/rig/steam_joints.jpg','Steam Pug: các joint có tên','object-position:50% 50%'),
 ('Picker','Bảng nút bấm chọn control, đỡ phải bấm trên model.','img/rig/d_picker.svg','Bố cục picker đã duyệt','object-fit:contain;padding:6px'),
 ('Retopo','Dựng lại lưới (mạng ô) của model cho hợp để rig và uốn.','img/rig/mesh_nightbat.jpg','Night Bat: lưới quad + UV','object-position:50% 50%'),
 ('FBX','Loại file chứa xương, mesh, anim để đưa vào Unity.','img/rig/d_export.svg','Các bước xử lý FBX cho Unity','object-fit:contain;padding:6px'),
 ('Frolvy','Phần mềm rigging (như Maya). Nơi dựng rig; AI điều khiển qua cầu nối.','img/rig/nb_rig_show.jpg','Night Bat đang mở trong Frolvy','object-position:50% 50%')])
std('Phần A · Hiểu từ số 0','Ai làm gì: bạn, AI, Frolvy',[
 blk('Nguyên tắc','AI làm từng bước, <b>dừng ở các cổng duyệt</b> để bạn xem hình và số. Bạn ra lệnh tiếp mới đi tiếp.'),
 blk('Điều bạn luôn quyết','Joint đặt đúng chưa, skin đã mượt chưa, chốt xuất file. Bạn sửa tay trong Frolvy thì ý bạn thắng, AI không tự đổi lại.')],
 [('img/rig/d_roles.svg','Ba bên trong việc rig. Mũi tên là chiều việc đi.','sch')],fw=1.6)
# ===== BẢN ĐỒ
raw('''<p class="kick">Phần B · Từng bước làm</p><h2>Bản đồ 10 bước (ô vàng = cổng bạn duyệt)</h2>
<div class="flow" style="margin-top:14px">
<div class="step"><span class="num">0</span><b>Nhận việc</b><span>File, yêu cầu</span></div>
<div class="step"><span class="num">1</span><b>Đo model</b><span>Mảnh, cỡ, hướng</span></div>
<div class="step gate"><span class="num">1b·CỔNG</span><b>Kiểm lưới</b><span>Đạt hay retopo</span></div>
<div class="step gate"><span class="num">2·CỔNG</span><b>Đặt joint</b><span>Xương đúng chỗ</span></div>
<div class="step"><span class="num">3</span><b>Chuỗi joint</b><span>Đuôi, áo choàng</span></div>
<div class="step"><span class="num">4</span><b>Build Rig</b><span>Sinh control</span></div>
<div class="step"><span class="num">5</span><b>Control</b><span>Vừa tay bấm</span></div>
<div class="step gate"><span class="num">6·CỔNG</span><b>Skin</b><span>Da bám xương</span></div>
<div class="step"><span class="num">7</span><b>Picker</b><span>Bảng nút</span></div>
<div class="step gate"><span class="num">8·CỔNG</span><b>Kiểm rig</b><span>Thử mọi khớp</span></div>
<div class="step"><span class="num">9</span><b>Xuất FBX</b><span>Vào Unity</span></div></div>
<div class="row" style="margin-top:24px">
<div class="card"><h3>Mỗi bước có 2 trang</h3><p>Trang 1 (nền sáng): để làm gì, bạn chuẩn bị gì, AI làm gì, bạn xem gì để duyệt. Trang 2 (nền tối): lỗi AI hay mắc ở bước đó, có ví dụ thật.</p></div>
<div class="card"><h3>Ví dụ xuyên suốt: Windy</h3><p>Hình Windy là joint thật lấy từ file của dự án, vẽ lên mesh. Hình dán nhãn rõ là ảnh thật, sơ đồ hay hình vẽ từ file.</p></div></div>''')
# ===== BƯỚC 0
std('Bước 0 · Nhận việc','Biết mình có gì trong tay trước khi rig',[
 blk('Để làm gì','Không có đủ file hoặc không rõ yêu cầu thì rig xong cũng phải làm lại.'),
 blk('Bạn chuẩn bị',ul('File model (FBX), texture','Tài liệu thiết kế (cần anim gì, đạo cụ gì)','Nói rõ nhân vật dùng cho game nào')),
 blk('AI làm','Mở file, liệt kê có gì, <b>hỏi lại chỗ thiếu</b> (ví dụ: gậy có bay tự do không?).'),
 blk('Bạn xem gì để duyệt','Bảng bên phải đúng và đủ chưa.')],
 [],)
S.pop()
S.append('''<section><p class="kick">Bước 0 · Nhận việc</p><h2>Biết mình có gì trong tay trước khi rig</h2><div class="split"><div class="col">'''+
 blk('Để làm gì','Không đủ file hoặc không rõ yêu cầu thì rig xong cũng phải làm lại.')+
 blk('Bạn chuẩn bị',ul('File model (FBX) và texture','Tài liệu thiết kế: cần anim gì, đạo cụ gì','Nói rõ nhân vật dùng cho game nào'))+
 blk('AI làm','Mở file, liệt kê có gì, <b>hỏi lại chỗ thiếu</b> (ví dụ: gậy có bay tự do không).')+
 '''</div><div class="col" style="flex:1.35"><table style="font-size:24px"><tr><th style="width:36%">Windy: file trong tay</th><th>Dùng để làm gì</th></tr>
<tr class="hl"><td>Hero_Windy.fbx</td><td>Model: thân + gậy (2 mảnh)</td></tr>
<tr><td>T_Colorpalette.tga</td><td>Texture (bảng màu)</td></tr>
<tr class="hl"><td>Hero_Windy.fvfit</td><td>Vị trí joint đã đặt (36 joint)</td></tr>
<tr><td>Hero_Windy_rig.fv</td><td>Rig đã dựng trong Frolvy</td></tr>
<tr class="hl"><td>Tài liệu thiết kế</td><td>Cần Idle, Attack, Skill 1–3; ở Skill 3 gậy bay tự do trước mặt</td></tr></table>
<div class="blk"><div class="bl">Bạn xem gì để duyệt</div><div class="bt">Danh sách file đúng và đủ chưa; AI hiểu đúng yêu cầu (ví dụ gậy bay tự do) chưa.</div></div></div></div></section>''')
# ===== BƯỚC 1
std('Bước 1 · Đo model','Đo model bằng số: mảnh, cỡ, hướng mặt',[
 blk('Để làm gì','Trước khi đặt xương phải biết nhân vật to cỡ nào, có mấy mảnh rời, quay mặt hướng nào.'),
 blk('AI làm',ul('Liệt kê từng mảnh rời, đếm đỉnh','Đo chiều cao, sải tay, đơn vị','Báo hướng mặt, tay cầm gì')),
 blk('Bạn xem gì để duyệt','Windy: <b>2 mảnh</b> (thân + áo choàng + đầu là một mảnh, gậy riêng), cao <b>185 cm</b>, sải tay <b>175,6 cm</b>, đơn vị cm, mặt nhìn +Z, gậy ở tay phải (bên trái ảnh).')],
 [('img/windy/w_mesh.png','Windy: model chưa rig, kèm số đo. Gậy là mảnh riêng nên sau này gậy bay tự do được.','wd')],fw=1.1)
std('Bước 1 · Lỗi AI hay mắc','Đo sai thì joint đặt sai từ đầu',[
 err('Lỗi thật · Hero RPG2','Cắt cả model một lần: váy lẫn vào lát chân, giáp lẫn vào lát tay. Công cụ chỉ cắt mảnh lớn nhất nên lát chân và tay ra rỗng.'),
 err('Lỗi thật · Pet mesh v2','Mô tả mảnh theo đoán: gọi mảnh 80 đỉnh là "mắt", thực ra là cánh Night Bat. Hai file mesh mới còn quay ngược 180°.'),
 err('Lỗi thật · MeoTom','Mesh nằm lùi 3 cm so với bản cũ nên joint đặt theo số cũ lệch đều 2–3 cm.'),
 fix('Bạn làm gì','Yêu cầu AI <b>đo bằng số, gửi bảng</b> (số đỉnh, số mảnh, cỡ, hướng) trước khi đặt joint. Chỗ nào chỉ đoán thì bắt AI ghi rõ "chưa chắc".')],
 [('img/rig/mesh_turtle.jpg','Pebble Turtle: bản đo mesh (lưới 4 góc + UV) làm trước khi chuyển rig sang mesh mới.','real')],dark=True,fw=1.2)
# ===== BƯỚC 1b
std('Bước 1b · Kiểm lưới','Lưới (mạng ô vuông) tốt thì da mới uốn đẹp',[
 blk('Để làm gì','Lưới quyết định mesh gập có đẹp không. Lưới xấu thì skin kiểu gì cũng móp.'),
 blk('AI làm',ul('Đếm tam giác, xem toàn quad hay tam giác tự động','Xem có vòng lưới quanh vai, khuỷu, gối, cổ, mặt','Xem model đang ở tư thế T hay A')),
 blk('Bạn xem gì để duyệt','Windy: khoảng <b>2.950 tam giác</b>, hợp game mobile (1.500–15.000). Nhìn ảnh phóng to vai: quanh khớp có mấy vòng lưới? Ít vòng thì chỗ gập sẽ góc cạnh.')],
 [('img/windy/w_wire.png','Windy: toàn bộ lưới (thân + áo choàng).','wd'),('img/windy/w_wire_zoom.png','Phóng to vai và tay: số vòng lưới quanh khớp quyết định độ mượt khi gập.','wd')],fw=1.2,mh=330)
std('Bước 1b · Lỗi AI hay mắc','Chữa lưới sai cách',[
 err('Lỗi thật · MeoTom','Giảm mesh (decimate) <b>không phải</b> retopo: chỉ bớt tam giác, không sửa được hướng lưới. Quadriflow cho lưới đều nhưng không theo xương, không có vòng mắt, miệng ("cách đi lưới chưa đúng").'),
 err('Lỗi thật · MeoTom','Bake normal từ mesh Tripo mang theo lồi lõm, phải bỏ. Texture bake bị lật dọc khi vào Frolvy.'),
 fix('Bạn làm gì','Hỏi AI: lưới <b>đạt hay chưa đạt, chỗ nào</b>. Chưa đạt thì xin bản retopo của artist trước khi rig.')],
 [('img/rig/mesh_nightbat.jpg','Night Bat: lưới quad theo hình khối, UV không chồng. Đây là lưới đạt.','real'),('img/rig/d_uvflip.svg','Bẫy: Frolvy hiện texture lật dọc.','sch')],dark=True,fw=1.2,mh=290)
