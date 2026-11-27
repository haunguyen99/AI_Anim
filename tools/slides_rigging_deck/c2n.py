# ===== BƯỚC 1 (gộp: nhận việc + đo + topology)
std('Bước 1 · Kiểm tra Mesh (1/3)','Biết có gì và nhân vật to cỡ nào',[
 blk('Để làm gì','Trước khi đặt joint phải biết đủ file chưa, nhân vật cao bao nhiêu, mấy mảnh mesh, quay mặt đâu.'),
 blk('Bạn chuẩn bị','File nhân vật (.fbx) và ảnh màu (texture).'),
 blk('Ninja','<b>Mesh body</b> (thân, đầu, khăn) và <b>kunai</b> là mảnh riêng. Cao 185 cm, sải tay 175,6 cm.'),
 blk('Bạn xem gì','Số mảnh, chiều cao, hướng mặt AI báo có khớp hình không.')],
 [('img/ninja/n_mesh.png','Ninja chưa rig, kèm số đo.','wd')],fw=1.05)
std('Bước 1 · Kiểm tra Mesh (2/3, review gate)','Topology tốt thì skin mới uốn đẹp',[
 blk('Để làm gì','Topology là mạng ô trên mesh. Ô đều, có vòng ô quanh khớp thì gập mượt. Ít ô hoặc lộn xộn thì chỗ gập bị góc cạnh.'),
 blk('Ninja','Khoảng <b>1.960 tris</b>, phần lớn ghép thành <b>quad</b> (ô 4 cạnh đều). Đây là ví dụ topology đạt.'),
 blk('Bạn xem gì','Nhìn ảnh phóng to shoulder: quanh khớp có mấy vòng quad? Càng đều càng tốt.')],
 [('img/ninja/n_wire.png','Ninja: toàn bộ topology (quad).','wd'),('img/ninja/n_wire_zoom.png','Phóng to shoulder: vòng quad quanh khớp.','wd')],fw=1.2,mh=330)
std('Bước 1 · Lỗi AI hay mắc (3/3)','Đo sai, hoặc chữa topology sai cách',[
 err('Ví dụ thật','AI đoán thay vì đo: cắt cả model một lần nên áo choàng lẫn vào chân. Hoặc gọi mảnh nhỏ là "mắt", thực ra là cánh.'),
 err('Ví dụ thật','AI chỉ giảm bớt tris rồi coi như dựng lại topology. Như vậy không sửa được hướng các ô.'),
 err('Ví dụ thật','Texture bị lật dọc khi vào Frolvy. Chỉ lật để xem, file cho game vẫn dùng ảnh gốc.'),
 fix('Bạn nói','<b>"Đo bằng số, gửi bảng: số mảnh, cỡ, hướng mặt."</b> Và: <b>"Topology đạt hay chưa? Chỗ nào chưa?"</b>')],
 [('img/rig/d_meshokbad.svg','Topology quanh một khớp: đạt (trái), chưa đạt (phải).','sch'),('img/rig/d_uvflip.svg','Bẫy texture bị lật.','sch')],dark=True,fw=1.2,mh=300)
# ===== BƯỚC 3
std('Bước 2 · Đặt joint (1/6)','Joint đặt ở chỗ khớp thật sự gập',[
 blk('Để làm gì','Joint là bộ khung. Đặt sai chỗ thì nhân vật gập sai chỗ.'),
 blk('Quy tắc','Đặt <b>đúng chỗ cơ thể gập</b> (elbow, knee), không đặt giữa khối bắp tay hay đùi.'),
 blk('Ninja','Gần 40 joint thân (ngón tay chỉ có middle finger và thumb), thêm chuỗi khăn mỗi bên.')],
 [('img/ninja/n_joints_front.png','Nhìn trước (bên phải nhân vật ở bên trái ảnh).','wd'),('img/ninja/n_joints_side.png','Nhìn bên. Thanh ngang dài là cái khăn.','wd'),('img/ninja/n_joints_top.png','Nhìn trên (mặt nhìn xuống dưới).','wd')],fw=2.0,mh=560,row=True)
std('Bước 2 · Đặt joint (2/6)','Chân: hip, knee, ankle',[
 blk('Hip · cao 67 cm','Chỗ đùi gắn vào hip.'),
 blk('Knee · cao 39 cm','Giữa đùi và cẳng chân.'),
 blk('Ankle · cao 12 cm','Chỗ cẳng chân gặp bàn chân, thấp, <b>ngay trên heel</b>.')],
 [('img/ninja/n_leg.png','Ninja, phóng to chân. Số là độ cao so với sàn.','wd')],fw=1.9,mh=640)
std('Bước 2 · Đặt joint (3/6)','Thân và đầu',[
 blk('Root · cao 71 cm','Root joint ở <b>giữa hai khớp hip</b>, ngang tầm hông.'),
 blk('Spine · 87 → Chest · 102 → Neck · 122','Ba điểm dọc giữa thân. Chest nằm ở giữa lồng ngực, thấp hơn shoulder.'),
 blk('Head · 131 · Head End · 185','Đầu xoay ở gáy. Điểm cuối nằm ở <b>đỉnh đầu</b>.')],
 [('img/ninja/n_spine.png','Ninja: thân và đầu, số là độ cao (cm).','wd')],fw=1.9,mh=640)
std('Bước 2 · Đặt joint (4/6)','Tay: scapula, shoulder, elbow, wrist',[
 blk('Scapula · cách giữa 12 cm, cao 119 cm','Gần spine (cột sống). Shoulder nhấc lên hạ xuống nhờ nó.'),
 blk('Shoulder · cách giữa 26 cm','<b>Nằm trong thân</b>, không ở rìa chỗ cánh tay mọc ra.'),
 blk('Elbow · 43 cm, Wrist · 64 cm','Elbow ở khoảng giữa shoulder và wrist.')],
 [('img/ninja/n_arm.png','Ninja: tay phải (bên trái ảnh). Scapula cách đường giữa 12 cm, shoulder 26 cm (14 cm giữa hai điểm).','wd')],fw=1.9,mh=520)
std('Bước 2 · Đặt joint (5/6, review gate)','Đạt hay chưa đạt? Nhìn 3 góc rồi sửa',[
 blk('Bạn xem','Bảo AI chụp <b>trước, bên, trên</b>. Hỏi: mỗi chấm có đúng chỗ khớp xoay không?'),
 blk('Ví dụ Ninja: cần chỉnh',ul('<b>Root, Hip, Knee</b> hạ 3 cm; <b>Neck, Head</b> hạ 7 cm; <b>Spine</b> hạ 5 cm; <b>Chest</b> hạ 8 cm','<b>Scapula</b> hạ 3 cm và ra ngoài 6 cm; <b>Shoulder</b> ra ngoài 6 cm','<b>Head End</b> đã đúng đỉnh đầu (giữ nguyên)')),
 blk('Sau khi bạn sửa','Nói: <b>"Giữ nguyên chỗ mình sửa."</b>')],
 [('img/ninja/n_beforeafter.png','Trái: chưa đạt (joint như trong file). Phải: đạt, joint đã hạ xuống đúng chỗ.','wd')],fw=1.8,mh=640)
std('Bước 2 · Lỗi AI hay mắc (6/6)','AI đặt joint ở chỗ "dễ thấy", không phải chỗ gập',[
 err('Ví dụ thật','Một nhân vật cao 1 m: AI đặt joint ankle cao 11,5 cm. Đúng phải là 6,5 cm (chỗ cẳng chân gặp bàn chân). Lệch 5 cm nên chân gập sai chỗ. Người duyệt phải sửa tay hơn nửa số joint.'),
 fix('Bạn nói','<b>"Chụp trước, bên, trên gửi mình trước khi build."</b> Nhìn bằng mắt rồi mới gật.')],
 [('img/rig/d_ankle.svg','Ankle đặt cao 11,5 cm thay vì 6,5 cm.','sch')],dark=True,fw=1.3)
# ===== BƯỚC 4
std('Bước 3 · Joint chain','Đuôi, khăn, áo choàng: mỗi thứ một joint chain',[
 blk('Để làm gì','Phần mềm như đuôi, áo choàng cần nhiều joint nối nhau để uốn lượn.'),
 blk('Quy tắc','Đầu chuỗi ở <b>chỗ gắn vào thân</b>. Chỗ cuộn gấp thì thêm joint.'),
 blk('Ninja','Khăn quàng đỏ dài bay phía sau: mỗi bên <b>5 joint</b> (Scarf 1 → 4 và Scarf End), nối từ Chest.')],
 [('img/ninja/n_chain.png','Ninja nhìn bên: joint chain Scarf 1 → Scarf End chạy dọc theo khăn.','wd'),('img/rig/wc_tail.jpg','Ví dụ khác: joint chain bám theo đuôi cuộn của một con vật.','real')],fw=1.2,mh=290)
std('Bước 3 · Lỗi AI hay mắc','Mất công bạn đã sửa',[
 err('Ví dụ thật','Bạn hạ vài joint, AI tự đổi cả chỗ bạn đã sửa. Công bạn mất.'),
 err('Ví dụ thật','Một lệnh Build nhầm đã <b>xoá hết control bên trái</b>. Không hoàn tác được.'),
 fix('Bạn nói','<b>"Giữ nguyên chỗ mình sửa."</b> Trước lệnh có nguy cơ xoá, nhắc AI lưu file.')],
 [],dark=True)
# ===== BƯỚC 5
std('Bước 4 · Build Rig','Bấm Build Rig: từ skeleton ra rig dùng được',[
 blk('Để làm gì','Frolvy tự sinh control từ skeleton bạn đã đặt.'),
 blk('Trước khi bấm',ul('Bỏ helper joint (joint thêm cho hiệu ứng, game điện thoại không dùng)','Root joint ở hip','Dựng lại lần hai: đưa mọi control về 0 trước')),
 blk('Bạn xem gì','Joint đúng chỗ, không có bản sao thừa, hai bên giống nhau.')],
 [('img/rig/d_build.svg','Build Rig sinh thêm gì.','sch')],fw=1.5)
std('Bước 4 · Lỗi AI hay mắc','Build để lại rác',[
 err('Ví dụ thật','AI tự bật thêm helper joint nên dư <b>126 joint</b>, thân bị kéo theo tay chân.'),
 err('Ví dụ thật','Dựng lại rig nhiều lần: joint cũ vẫn lọt vào file, thành "joint ma".'),
 fix('Bạn nói','<b>"Build một lần cho sạch."</b> Phải dựng lại thì đưa control về 0 trước.')],
 [],dark=True)
