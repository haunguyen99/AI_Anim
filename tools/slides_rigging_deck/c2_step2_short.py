# ===== BƯỚC 2 (bản ngắn: gộp 6 trang đặt joint thành 2 trang)
std('Bước 2 · Đặt joint (1/2)','Joint đặt ở chỗ khớp thật sự gập',[
 blk('Quy tắc','Đặt <b>đúng chỗ cơ thể gập</b> (elbow, knee), không đặt giữa khối bắp tay hay đùi. Chỉ đặt bên phải và giữa, Frolvy tự lật sang trái.'),
 blk('Ninja: độ cao các joint (cm)','<b>Thân:</b> Root 71 · Spine 87 · Chest 102 · Neck 122 · Head 131 · Head End 185<br><b>Chân:</b> Hip 67 · Knee 39 · Ankle 12 (ngay trên heel)<br><b>Tay:</b> Scapula cách giữa 12 · Shoulder 26 · Elbow 43 · Wrist 64'),
 blk('Bạn xem','Bảo AI chụp <b>trước, bên, trên</b>. Hỏi: mỗi chấm có đúng chỗ khớp xoay không?')],
 [('img/ninja/n_joints_front.png','Nhìn trước (bên phải nhân vật ở bên trái ảnh).','wd'),('img/ninja/n_joints_side.png','Nhìn bên. Thanh ngang dài là cái khăn.','wd')],fw=1.5,mh=560,row=True)
std('Bước 2 · Đặt joint (2/2, review gate)','Đạt hay chưa đạt? Và lỗi AI hay mắc',[
 blk('Ninja: cần chỉnh','<b>Root, Hip, Knee</b> hạ 3 · <b>Neck, Head</b> hạ 7 · <b>Spine</b> hạ 5 · <b>Chest</b> hạ 8 · <b>Scapula</b> hạ 3 và ra 6 · <b>Shoulder</b> ra 6 (cm)'),
 err('Lỗi AI hay mắc','AI đặt joint ở chỗ "dễ thấy", không phải chỗ gập. Ví dụ: ankle cao 11,5 cm, đúng phải 6,5 cm (lệch 5 cm nên chân gập sai chỗ).')],
 [('img/ninja/n_beforeafter.png','Trái: chưa đạt (joint như trong file). Phải: đạt, joint đã hạ xuống đúng chỗ.','wd')],fw=1.7,mh=560)
