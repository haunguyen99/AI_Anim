"""Đổi thuật ngữ tiếng Việt hoá sang thuật ngữ chuyên môn tiếng Anh (joint, control, skin, weight...) trong nguồn slide.
    python3 -I tools/slides_rigging_deck/to_english_terms.py   (chạy một lần; bản trước lưu ở v3/)"""
import re,sys
MAP=[
 ('dây điều khiển','control'),('dây đích','target control'),('mức bám','weight'),('dán da (bind)','bind skin (bind)'),('dán da','bind skin'),
 ('xương gốc','root joint'),('chuỗi xương','joint chain'),('bộ xương','skeleton'),('xương phụ','helper joint'),('xương','joint'),
 ('bả vai','scapula'),('cột sống','spine'),('cổ chân','ankle'),('cổ tay','wrist'),('ngón giữa','middle finger'),('ngón cái','thumb'),('ngón chân','toes'),
 ('tư thế gốc','bind pose'),('khung hình','frame'),('bảng nút','picker'),('công tắc IK/FK','IK/FK switch'),('cổng duyệt','review gate'),
 ('chiêu cuối','ultimate skill'),('tam giác','tris'),('kiểm lưới','kiểm topology'),('lưới','topology'),
 ('khuỷu','elbow'),('ngực','chest'),('hông','hip'),('gối','knee'),('gót','heel'),
]
WORD=[('vai','shoulder'),('cổ','neck'),('cổng','gate'),('vỏ','mesh'),('da','skin'),('dây','control')]
def cap(src,rep): return rep[0].upper()+rep[1:] if src[:1].isupper() else rep
def conv(text):
    for a,b in MAP: text=re.sub(r'(?<!\w)'+re.escape(a)+r'(?!\w)',lambda m:cap(m.group(0),b),text,flags=re.I)
    for a,b in WORD: text=re.sub(r'(?<!\w)'+a+r'(?!\w)',lambda m:cap(m.group(0),b),text,flags=re.I)
    return text
def conv_html(t):
    return re.sub(r'(<[^>]*>)|([^<]+)',lambda m: m.group(1) if m.group(1) else conv(m.group(2)),t)
def conv_file(path):
    s=open(path).read()
    # chỉ đổi trong chuỗi ' ' hoặc " " hoặc ''' ''' (không đụng tên file ảnh/lệnh)
    def strrep(m):
        t=m.group(0)
        if 'img/' in t or t.startswith("'<") and 'class=' in t and False: return t
        return conv(t)
    s=re.sub(r"'''.*?'''",lambda m: conv_html(m.group(0)),s,flags=re.S)
    def strrep2(m):
        t=m.group(0)
        if 'img/' in t: return t
        return conv_html(t) if '<' in t else conv(t)
    s=re.sub(r"'[^'\n]*'|\"[^\"\n]*\"",strrep2,s)
    s=s.replace("img/rig/d_ctl_size.svg","img/rig/d_ctl_size.svg")
    open(path,'w').write(s)
if __name__=='__main__':
    for f in sys.argv[1:]: conv_file(f)
