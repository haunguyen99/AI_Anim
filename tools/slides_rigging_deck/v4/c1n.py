# ===== PHẦN A
raw('<p class="kick">Hướng dẫn cho người mới</p><h1 style="margin-top:auto">Nhờ AI làm rig<br>nhân vật 3D</h1><p style="max-width:1300px;color:#c9d6ea;margin-bottom:auto">Bạn không cần biết 3D. Tài liệu này chỉ: AI làm gì, bạn xem gì, khi nào gật đầu, khi nào bảo làm lại. Ví dụ xuyên suốt: nhân vật <b style="color:#F0B13B">Windy</b>.</p>',dark=True)
S[-1]=S[-1].replace('<section class="dark"','<section class="dark on" style="justify-content:center;gap:40px"')
std('Phần A · Đọc trước','Đọc xong, bạn làm được 3 việc',[
 blk('1. Giao việc cho AI','Biết cần chuẩn bị gì và nói câu đầu tiên là gì.'),
 blk('2. Duyệt từng bước','Biết nhìn vào đâu để thấy <b>đạt</b> hay <b>chưa đạt</b>.'),
 blk('3. Bắt AI sửa đúng chỗ','Biết lỗi AI hay mắc và câu để AI làm lại.')],
 [('img/windy/w_beforeafter.png','Ví dụ một lần duyệt: trái chưa đạt, phải đã sửa.','wd')],fw=1.6,mh=520)
std('Phần A · Đọc trước','Bắt đầu từ đâu? 4 việc',[
 blk('Bạn cần có','File nhân vật (.fbx) và file ảnh màu (texture).'),
 blk('Câu đầu tiên','"Rig nhân vật Windy trong Frolvy. Dừng ở bước đặt joint, chụp 3 góc gửi mình duyệt."')],
 [('img/rig/d_start.svg','Bốn việc đầu tiên.','sch')],fw=1.7)
std('Phần A · Đọc trước','Rig là gì? Lắp joint và control vào con rối',[
 blk('Ví như con rối',ul('<b>Mesh</b>: cái vỏ cứng, chưa cử động','<b>Joint</b>: khớp bên trong mesh','<b>Skin</b>: lớp da ôm quanh joint, joint xoay thì skin xoay','<b>Control</b>: sợi dây bạn giật')),
 blk('Rig','Lắp joint, gắn skin, nối control. Xong thì chỉ cần kéo control là nhân vật cử động.')],
 [('img/windy/w_mesh.png','Windy chưa rig: chỉ là cái mesh.','wd'),('img/windy/w_joints_front.png','Windy có joint: mỗi chấm vàng là một khớp.','wd')],fw=1.3,mh=560,row=True)
std('Phần A · Đọc trước','Ai làm gì: bạn, AI và Frolvy',[
 blk('Quy tắc','AI làm từng bước và <b>dừng ở các gate</b>. Bạn xem rồi bảo đi tiếp.'),
 blk('Bạn là người quyết','Bạn tự sửa trong Frolvy thì ý bạn thắng. AI không tự đổi lại.'),
 blk('AI làm sai hướng','Nói ngay: <b>"Dừng lại. Quay về bước …"</b>')],
 [('img/rig/d_roles.svg','Ba bên cùng làm việc.','sch')],fw=1.6)
quad('Phần A · Đọc trước','Bốn từ quan trọng nhất',[
 ('Joint','Khớp bên trong mesh (chấm vàng). Nơi một bộ phận xoay.','img/windy/w_joints_front.png'),
 ('Control','Thứ bạn kéo. Các vòng màu quanh con vật là control. Kéo control thì joint xoay.','img/rig/mecha_ctl.jpg'),
 ('Skin và weight','Skin bám vào joint theo phần trăm. 50% shoulder + 50% elbow thì gập theo cả hai.','img/rig/d_skinrule.svg'),
 ('FK và IK','FK: xoay từng khớp. IK: kéo bàn tay, cả tay gập theo.','img/rig/d_ikfk.svg')])
raw('''<p class="kick">Phần A · Từ điển (1/2)</p><h2>Từ điển</h2>
<table style="font-size:23px"><tr><th style="width:21%">Từ</th><th>Nghĩa</th></tr><tr class="hl"><td><b>Mesh</b></td><td>Thân hình nhân vật, ghép từ rất nhiều mặt nhỏ</td></tr><tr class=""><td><b>Skin</b></td><td>Chính cái mesh đó, gọi là "skin" khi nói chuyện bám vào joint</td></tr><tr class="hl"><td><b>Topology</b></td><td>Cách các mặt nhỏ nối thành ô. Ô đều thì uốn đẹp</td></tr><tr class=""><td><b>Tris</b></td><td>Mặt nhỏ nhất của mesh. Ít quá thì thô, nhiều quá thì nặng game</td></tr><tr class="hl"><td><b>Texture</b></td><td>Ảnh màu dán lên mesh</td></tr><tr class=""><td><b>Root joint</b></td><td>Joint ở hip, mọi joint khác nối từ đây</td></tr><tr class="hl"><td><b>Joint chain</b></td><td>Nhiều joint nối nhau cho phần mềm: đuôi, áo choàng</td></tr><tr class=""><td><b>Build Rig</b></td><td>Bấm một nút, Frolvy tự sinh control từ skeleton</td></tr><tr class="hl"><td><b>Bind pose</b></td><td>Dáng đứng chuẩn lúc mới tạo, thường dang tay chữ T</td></tr><tr class=""><td><b>Frame</b></td><td>Một ảnh trong chuỗi chuyển động, như một trang flipbook</td></tr></table>''')
raw('''<p class="kick">Phần A · Từ điển (2/2)</p><h2>Từ điển</h2>
<table style="font-size:23px"><tr><th style="width:21%">Từ</th><th>Nghĩa</th></tr><tr class="hl"><td><b>Reset về 0</b></td><td>Đưa control về vị trí ban đầu, như nút reset (AI làm)</td></tr><tr class=""><td><b>Bind skin</b></td><td>Lần đầu gắn skin vào joint, lúc nhân vật đứng bind pose</td></tr><tr class="hl"><td><b>Picker</b></td><td>Bảng bấm để chọn control cho nhanh</td></tr><tr class=""><td><b>IK/FK switch</b></td><td>Nút đổi giữa hai cách kéo tay: kéo bàn tay hoặc xoay từng khớp</td></tr><tr class="hl"><td><b>Ultimate skill</b></td><td>Đòn mạnh nhất của nhân vật trong game</td></tr><tr class=""><td><b>Bridge (MCP)</b></td><td>Đường kết nối để AI ra lệnh cho Frolvy (nhóm kỹ thuật dựng sẵn)</td></tr><tr class="hl"><td><b>Frolvy</b></td><td>Phần mềm làm rig. AI điều khiển nó thay bạn</td></tr><tr class=""><td><b>FBX</b></td><td>File đóng gói nhân vật để đưa vào game</td></tr><tr class="hl"><td><b>Unity</b></td><td>Phần mềm làm game, nơi file FBX chạy thật</td></tr><tr class=""><td><b>Review gate</b></td><td>Chỗ AI dừng lại chờ bạn xem rồi mới đi tiếp</td></tr></table>''')
raw('''<p class="kick">Phần B · Từng bước</p><h2>10 bước (ô vàng là gate bạn duyệt)</h2>
<div class="flow" style="margin-top:14px">
<div class="step"><span class="num">1</span><b>Nhận việc, đo</b><span>File, cỡ</span></div>
<div class="step gate"><span class="num">2·Gate</span><b>Kiểm topology</b><span>Đạt hay làm lại</span></div>
<div class="step gate"><span class="num">3·Gate</span><b>Đặt joint</b><span>Đúng chỗ khớp</span></div>
<div class="step"><span class="num">4</span><b>Joint chain</b><span>Đuôi, áo choàng</span></div>
<div class="step"><span class="num">5</span><b>Build Rig</b><span>Sinh control</span></div>
<div class="step"><span class="num">6</span><b>Control</b><span>Vừa tay bấm</span></div>
<div class="step gate"><span class="num">7·Gate</span><b>Bind skin</b><span>Skin bám joint</span></div>
<div class="step"><span class="num">8</span><b>Picker</b><span>Chọn control nhanh</span></div>
<div class="step gate"><span class="num">9·Gate</span><b>Rig test</b><span>Thử mọi khớp</span></div>
<div class="step"><span class="num">10</span><b>Export FBX</b><span>Vào game</span></div></div>
<div class="row" style="margin-top:24px"><div class="card"><h3>Mỗi bước</h3><p>Trang sáng: làm gì, xem gì. Trang tối: lỗi AI hay mắc.</p></div>
<div class="card"><h3>Nhãn trên hình</h3><p><b>ẢNH THẬT</b> chụp từ Frolvy · <b>WINDY</b> vẽ từ file joint thật · <b>SƠ ĐỒ</b> vẽ minh hoạ.</p></div></div>''')
