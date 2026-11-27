# ===== PHẦN A: đọc trước khi làm
raw('<p class="kick">Hướng dẫn cho người mới</p><h1 style="margin-top:auto">Nhờ AI làm rig<br>nhân vật 3D trong Frolvy</h1><p style="max-width:1400px;color:#c9d6ea;margin-bottom:auto">Bạn không cần biết gì về 3D. Tài liệu này chỉ bạn từng bước: AI làm gì, bạn xem gì, khi nào gật đầu, khi nào bảo AI làm lại. Ví dụ xuyên suốt là nhân vật <b style="color:#F0B13B">Windy</b>, thầy phù thủy gió cầm gậy.</p>',dark=True)
S[-1]=S[-1].replace('<section class="dark"','<section class="dark on" style="justify-content:center;gap:40px"')
std('Phần A · Đọc trước khi làm','Đọc xong, bạn sẽ làm được 3 việc',[
 blk('1. Giao việc cho AI','Biết bắt đầu từ đâu, cần chuẩn bị file gì, câu đầu tiên nói với AI là gì.'),
 blk('2. Duyệt từng bước','Biết ở mỗi "cổng" AI dừng lại, bạn cần nhìn vào đâu để biết là <b>đạt</b> hay <b>chưa đạt</b>.'),
 blk('3. Bắt AI sửa đúng chỗ','Biết các lỗi AI hay mắc và câu nói để AI làm lại, không phải tự học 3D.'),
 blk('Đọc mất bao lâu','Phần A đọc khoảng 10 phút. Phần B (10 bước) đọc từng bước khi cần. Phần C là bảng tra nhanh.')],
 [('img/windy/w_beforeafter.png','Ví dụ một lần duyệt: bên trái AI đặt xương chưa đúng, bên phải đã sửa. Bạn sẽ học cách nhìn ra điểm sai như vậy.','wd')],fw=1.5,mh=560)
std('Phần A · Đọc trước khi làm','Bắt đầu từ đâu? Làm 4 việc này',[
 blk('Bốn việc đầu tiên','Mở Frolvy, mở khung chat với AI, đưa file và nói yêu cầu, rồi xem hình AI gửi lại.'),
 blk('Bạn cần có sẵn',ul('File model nhân vật (đuôi .fbx) và file texture (ảnh màu)','Biết nhân vật dùng cho game nào, cần làm những chuyển động gì')),
 blk('Câu mẫu đầu tiên','"Rig nhân vật Windy trong Frolvy. Chỉ dùng xương cơ bản, gốc xương ở hông. Dừng ở bước đặt xương, chụp 3 góc gửi mình duyệt."'),
 blk('Chưa có ảnh màn hình thật','Hình bên phải là sơ đồ. Ảnh chụp cửa sổ Frolvy và khung chat sẽ thay vào sau.')],
 [('img/rig/d_start.svg','Bốn việc đầu tiên.','sch')],fw=1.5)
std('Phần A · Đọc trước khi làm','Rigging là gì? Lắp xương và dây vào con rối',[
 blk('Ví như con rối',ul('<b>Model</b> là cái vỏ con rối: một khối cứng, chưa cử động được','<b>Xương (joint)</b> là các khớp bên trong vỏ','<b>Da (skin)</b> là lớp ôm quanh xương: xương xoay thì da xoay theo','<b>Dây điều khiển (control)</b> là sợi dây bạn giật để con rối cử động')),
 blk('Rigging là gì','Là lắp xương, gắn da và nối dây vào model. Làm xong thì người làm hoạt hình chỉ cần kéo dây là nhân vật cử động.')],
 [('img/windy/w_mesh.png','Windy chưa rig: chỉ là cái vỏ (gọi là mesh). Cao 185 cm, cầm gậy.','wd'),('img/windy/w_joints_front.png','Windy đã có xương: mỗi chấm vàng là một khớp đặt bên trong vỏ.','wd')],fw=1.3,mh=560,row=True)
std('Phần A · Đọc trước khi làm','Rig nằm ở đâu khi làm game?',[
 blk('Chuỗi việc',ul('Artist tạo <b>model</b> (cái vỏ)','<b>Rig</b>: lắp xương, da, dây điều khiển. Đây là việc của tài liệu này','Người làm hoạt hình kéo dây để tạo chuyển động','Xuất file <b>FBX</b> (file đóng gói nhân vật), đưa vào <b>Unity</b> (phần mềm làm game) để game chạy')),
 blk('Vì sao rig quan trọng','Rig sai thì hoạt hình đẹp cỡ nào cũng méo: tay móp, mặt dính vào cánh, chân trượt. Rig đúng thì người làm hoạt hình làm nhanh và ít lỗi.')],
 [('img/rig/d_pipeline.svg','Rig là bước nối giữa cái vỏ và chuyển động.','sch')],fw=1.5)
std('Phần A · Đọc trước khi làm','Ai làm gì: bạn, AI và Frolvy',[
 blk('Quy tắc chính','AI làm từng bước và <b>dừng lại ở các cổng</b> để bạn xem hình và số. Bạn bảo đi tiếp thì AI mới đi tiếp.'),
 blk('Bạn luôn là người quyết','Xương đặt đúng chưa, da mượt chưa, khi nào xuất file. Bạn tự sửa trong Frolvy thì ý bạn thắng, AI không tự đổi lại.'),
 blk('Khi nào bảo AI dừng','Thấy AI làm sai hướng, hoặc làm tiếp mà bạn chưa duyệt: nói ngay <b>"Dừng lại. Quay về bước …"</b>. AI sẽ quay lại bước bạn chỉ.')],
 [('img/rig/d_roles.svg','Ba bên cùng làm việc. Mũi tên là chiều đi của việc.','sch')],fw=1.6)
quad('Phần A · Đọc trước khi làm','Bốn từ quan trọng nhất',[
 ('Xương (joint)','Khớp bên trong vỏ, hiện bằng chấm vàng. Nơi một bộ phận xoay, như khuỷu tay, đầu gối.','img/windy/w_joints_front.png'),
 ('Dây điều khiển (control)','Thứ bạn kéo hoặc xoay trong Frolvy. Kéo dây thì xương xoay theo.','img/rig/mecha_ctl.jpg'),
 ('Da và mức bám (skin, weight)','Da bám vào xương theo phần trăm. Một điểm bám 50% vai, 50% khuỷu thì gập theo cả hai.','img/rig/d_skinrule.svg'),
 ('Hai cách kéo tay (FK, IK)','FK: xoay từng khớp. IK: kéo bàn tay, cả tay tự gập theo.','img/rig/d_ikfk.svg')])
raw('''<p class="kick">Phần A · Đọc trước khi làm</p><h2>Từ điển một trang</h2>
<table style="font-size:21px"><tr><th style="width:15%">Từ</th><th style="width:35%">Nghĩa đời thường</th><th style="width:15%">Từ</th><th>Nghĩa đời thường</th></tr>
<tr class="hl"><td><b>Mesh</b></td><td>Cái vỏ của nhân vật, làm từ rất nhiều điểm và mặt nhỏ</td><td><b>Đỉnh</b></td><td>Một điểm trên vỏ. Mỗi đỉnh có "mức bám" vào xương</td></tr>
<tr><td><b>Lưới</b></td><td>Cách các điểm trên vỏ nối thành ô. Ô đều thì uốn đẹp</td><td><b>Retopo</b></td><td>Dựng lại lưới cho hợp, khi lưới gốc quá xấu để rig</td></tr>
<tr class="hl"><td><b>Texture, UV</b></td><td>Ảnh màu dán lên vỏ; UV là bản đồ cho biết dán chỗ nào</td><td><b>Bind</b></td><td>Lần đầu dán da vào xương, khi nhân vật đứng yên tư thế gốc</td></tr>
<tr><td><b>DEF</b></td><td>Các xương thật mà game dùng. Chỉ xương DEF mới được dán da</td><td><b>Root</b></td><td>Xương gốc đặt ở hông. Mọi xương khác nối từ đây</td></tr>
<tr class="hl"><td><b>Chuỗi xương</b></td><td>Nhiều xương nối nhau cho phần mềm: đuôi, áo choàng, khăn</td><td><b>Build Rig</b></td><td>Bấm một nút để Frolvy tự sinh dây điều khiển từ bộ xương</td></tr>
<tr><td><b>Ràng buộc (constraint)</b></td><td>Bắt vật này đi theo vật kia, ví dụ gậy đi theo bàn tay</td><td><b>Bake</b></td><td>"Chốt" chuyển động thành từng khung hình, để không phụ thuộc ràng buộc</td></tr>
<tr class="hl"><td><b>Pivot</b></td><td>Tâm xoay của một vật. Pivot sai thì xoay lệch</td><td><b>Picker</b></td><td>Bảng nút bấm để chọn dây điều khiển cho nhanh</td></tr>
<tr><td><b>Playblast</b></td><td>Video ngắn quay nhân vật cử động để xem lại</td><td><b>FBX</b></td><td>Loại file đóng gói xương, vỏ và chuyển động để đưa vào game</td></tr>
<tr class="hl"><td><b>Unity</b></td><td>Phần mềm làm game, nơi file FBX chạy thật</td><td><b>Frolvy</b></td><td>Phần mềm rig, giống Maya. AI điều khiển nó thay bạn</td></tr>
<tr><td><b>Cầu nối</b></td><td>Đường kết nối để AI ra lệnh cho Frolvy</td><td><b>Cổng duyệt</b></td><td>Chỗ AI dừng lại chờ bạn xem rồi mới đi tiếp</td></tr></table>''')
raw('''<p class="kick">Phần B · Từng bước làm</p><h2>Bản đồ 10 bước (ô vàng là cổng bạn duyệt)</h2>
<div class="flow" style="margin-top:14px">
<div class="step"><span class="num">1</span><b>Nhận việc, đo</b><span>File, cỡ, hướng</span></div>
<div class="step gate"><span class="num">2·CỔNG</span><b>Kiểm lưới</b><span>Đạt hay làm lại</span></div>
<div class="step gate"><span class="num">3·CỔNG</span><b>Đặt xương</b><span>Đúng chỗ khớp</span></div>
<div class="step"><span class="num">4</span><b>Chuỗi xương</b><span>Đuôi, áo choàng</span></div>
<div class="step"><span class="num">5</span><b>Build Rig</b><span>Sinh dây điều khiển</span></div>
<div class="step"><span class="num">6</span><b>Dây điều khiển</b><span>Vừa tay bấm</span></div>
<div class="step gate"><span class="num">7·CỔNG</span><b>Dán da</b><span>Da bám xương</span></div>
<div class="step"><span class="num">8</span><b>Bảng nút</b><span>Picker</span></div>
<div class="step gate"><span class="num">9·CỔNG</span><b>Thử rig</b><span>Thử mọi khớp</span></div>
<div class="step"><span class="num">10</span><b>Xuất file</b><span>Đưa vào game</span></div></div>
<div class="row" style="margin-top:24px">
<div class="card"><h3>Mỗi bước có 2 trang</h3><p>Trang nền sáng: làm gì, bạn xem gì. Trang nền tối: lỗi AI hay mắc ở bước đó. Các bước có cổng còn có thêm khung "đạt / chưa đạt".</p></div>
<div class="card"><h3>Windy làm ví dụ</h3><p>Hình Windy vẽ từ file xương thật của dự án. Hình có nhãn: <b>ảnh thật</b> (chụp từ Frolvy), <b>Windy</b> (vẽ từ file), <b>sơ đồ</b> (vẽ minh hoạ).</p></div></div>''')
