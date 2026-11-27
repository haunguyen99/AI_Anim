# Bản ngắn (user 2026-11-26): lược các trang 4, 8, 10, 12, 16, 18, 25, 26 (đánh số theo bản 31 trang), sửa trang 7, 21, 11 và checklist.
import re
def S_(i): return S[i-1]
# ---- trang 7 (từ điển): hàng Topology -> Bind skin
S[6]=re.sub(r'<tr class="(hl|)"><td><b>Topology</b></td><td>[^<]*</td></tr>',lambda m:f'<tr class="{m.group(1)}"><td><b>Bind skin</b></td><td>Lần đầu gắn skin vào joint, lúc nhân vật đứng ở bind pose</td></tr>',S[6])
assert 'Bind skin' in S[6]
# ---- trang 11: nhãn
S[10]=S[10].replace('Kiểm tra Mesh (2/3, review gate)','Kiểm tra Mesh (review gate)')
# ---- bản đồ bước (trang 9): bỏ Rig test, Export FBX thành bước 8
m9=S[8]
m9=re.sub(r'<div class="step gate"><span class="num">8·Gate</span><b>Rig test</b>.*?</div>','',m9,flags=re.S)
m9=m9.replace('<span class="num">9</span><b>Export FBX</b>','<span class="num">8</span><b>Export FBX</b>').replace('9 bước','8 bước')
S[8]=m9
# ---- trang 21: nội dung mới
n0=len(S)
CMDS['Phần ảnh hưởng đúng của Bind skin ở mỗi vùng']=('"Đưa mọi control về 0, rồi bind skin cho Ninja. Kunai bám 100% Weapon. Tối đa 4 joint mỗi điểm."','báo đã bind skin, chưa duyệt. Bước sau mới xem kết quả.')
std('Bước 6 · Bind skin (1/3)','Phần ảnh hưởng đúng của Bind skin ở mỗi vùng',[
 blk('Ý chính','Mỗi điểm trên skin bám theo <b>joint gần nó nhất</b>. Chỗ gần khớp thì chia cho cả hai joint, nên màu pha trộn.'),
 blk('Nhớ 3 điều',ul('Tối đa <b>4 joint</b> mỗi điểm, tổng luôn <b>100%</b>','Vùng nào bám joint của vùng đó, joint ở xa không kéo','Mảnh cứng (kunai) bám <b>100%</b> joint Weapon'))],
 [('img/ninja/n_skinmap.png','Ninja: màu cho biết mỗi điểm trên skin bám joint nào.','sch')],fw=1.2,mh=640)
newp=S.pop()
S[20]=newp
# ---- checklist (trang cuối) ngắn gọn
S[-1]=S[-1].replace('<h2>Checklist duyệt rig</h2>','<h2>Checklist duyệt rig: 6 ý chính</h2>')
i=S[-1].index('<div class="row bigl">'); j=S[-1].index('<p class="note">') if '<p class="note">' in S[-1] else None
new_list='''<div class="row bigl" style="flex-direction:column;gap:14px"><div class="card"><ul><li><b>Mesh:</b> topology đã kiểm, đủ vòng quad quanh khớp</li><li><b>Joint:</b> đúng chỗ khớp gập, đã xem 3 góc, Root ở hip</li><li><b>Control:</b> thấy rõ, không quá to, hai bên giống nhau</li><li><b>Skin:</b> tối đa 4 joint mỗi điểm, đã xoay các khớp và nhìn bằng mắt, không móp</li><li><b>AI báo rõ:</b> cái nào chưa kiểm</li><li><b>Xuất file:</b> chỉ khi bạn đã nói "chốt"</li></ul></div></div>'''
tail=S[-1][j:] if j else '</section>'
S[-1]=S[-1][:i]+new_list+tail


# ---- chỉnh theo yêu cầu (bản 23 trang: trang 9, 10, 11, 13, 14 = chỉ số 31-trang 13, 14, 15, 19, 20)
def _rm_blk(i,label):
    pat=r'<div class="blk"><div class="bl">'+re.escape(label)+r'</div><div class="bt">.*?</div></div>'
    new=re.sub(pat,'',S[i-1],count=1,flags=re.S); assert new!=S[i-1],label; S[i-1]=new
_rm_blk(13,'Ninja: độ cao các joint (cm)')
_rm_blk(14,'Ninja: cần chỉnh')
_rm_blk(15,'Ninja')
# trang 13 (Bước 5 Control): câu lệnh mẫu
_old=re.search(r'<div class="ct">"Vẽ control[^<]*"</div>',S[18]); assert _old
S[18]=S[18].replace(_old.group(0),'<div class="ct">"Tạo Control ôm sát mesh. Vũ khí gắn vào joint tay, joint Weapon dưới Wrist. Tạo hai bên đối xứng, so trái với phải."</div>')
S[18]=S[18].replace('bảng cỡ control hai bên và ảnh control quanh nhân vật.','control ôm sát mesh, vũ khí gắn Weapon, bảng cỡ hai bên trái và phải.')
# trang 14: ví dụ 2 từ biểu đồ -> ảnh minh hoạ
assert 'd_ctl_size.svg' in S[19]
S[19]=S[19].replace('img/rig/d_ctl_size.svg','img/ninja/n_ctl_bad.png').replace('Control hai bên chênh nhau. Xanh dương: phải. Tím: trái.','Ninja: control shoulder bên phải quá to, bên trái bé xíu. Xanh dương: phải. Tím: trái.').replace('Ví dụ 2 (xem biểu đồ)','Ví dụ 2 (xem hình)')

# ---- "Topology" -> "Lưới" (user 2026-11-26) + câu lệnh mẫu trang Kiểm tra Mesh
_cmd_old=re.search(r'"Kiểm topology Ninja:[^<]*"',S[10])
if _cmd_old: S[10]=S[10].replace(_cmd_old.group(0),'"Kiểm Lưới Ninja: xem số đường lưới ở các khớp có đủ không và kiểm tra xem đạt hay chưa."')
S[10]=S[10].replace('số tris, ảnh phóng to shoulder, và kết luận đạt / chưa đạt.','số đường lưới ở từng khớp, ảnh phóng to shoulder, và kết luận đạt hay chưa.')
S[10]=S[10].replace('max-height:330px','max-height:290px')
for _i in range(len(S)):
    S[_i]=S[_i].replace('Topology','Lưới').replace('topology','lưới')
# ---- xoá trang (theo số trang bản 31 trang)
for k in sorted([4,8,10,12,16,18,25,26],reverse=True): del S[k-1]
print('bản ngắn mới:',len(S),'trang')
