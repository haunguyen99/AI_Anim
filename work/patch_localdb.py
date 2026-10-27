"""Nhúng kho dữ liệu trên máy (tools/home/localdb.js) vào ba Lab master và nối vào chỗ lấy db của mỗi Lab.
Idempotent (dấu /*LOCALDB*/). Chạy lại sau khi sửa localdb.js: python work/patch_localdb.py --refresh"""
import os, re, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SHIM = open(os.path.join(ROOT, "tools", "home", "localdb.js"), encoding="utf8").read().strip()
BLOCK = "<script>\n" + SHIM + "\n</script>\n"
refresh = "--refresh" in sys.argv


def edit(path, pairs):
    s = open(path, encoding="utf8").read()
    if "/*LOCALDB*/" in s:
        if not refresh:
            print("already patched:", os.path.basename(path)); return
        s = re.sub(r"<script>\n/\*LOCALDB\*/.*?</script>\n", lambda m: BLOCK, s, count=1, flags=re.S)
    else:
        for a, b in pairs:
            assert s.count(a) == 1, (path, a[:70], s.count(a))
            s = s.replace(a, b)
        i = s.index("<script>\n")          # script chính đầu tiên (không src): shim phải có trước nó
        s = s[:i] + BLOCK + s[i:]
    open(path, "w", encoding="utf8", newline="").write(s)
    print("ok:", os.path.basename(path))


W = os.path.join(ROOT, "work")

edit(os.path.join(W, "pose_lab", "index.html"), [(
'''  if (!window.claude || !window.claude.use) { $("status").textContent = "Đây là bản chạy thử trên máy: nút Lưu sẽ tải file .json. Mở trang trên claude.ai để lưu thẳng cho AI."; return; }
  const [d, u, cm] = await Promise.all([claude.use("db"), claude.use("user"), claude.use("comments")]);
  db = d; user = u; comments = cm;
  if (!db) { $("status").textContent = "Đăng nhập claude.ai để lưu điều chỉnh. Bạn vẫn chỉnh thử được trên model."; refresh(); return; }''',
'''  const hasClaude = !!(window.claude && window.claude.use);
  let d = null, u = null, cm = null;
  if (hasClaude) [d, u, cm] = await Promise.all([claude.use("db"), claude.use("user"), claude.use("comments")]);
  if (!d) d = await window.localDB();   // không có db claude.ai: dùng kho trên máy (Home server)
  db = d; user = u; comments = cm;
  try { window.dbWidget({ db, cols: ["adjusts", "rounds", "keys", "anims"], host: ".tools" }); } catch (e) { console.error(e); }
  if (!db) {
    if (!hasClaude) { $("status").textContent = "Đây là bản chạy thử trên máy: nút Lưu sẽ tải file .json. Mở Home (tools/home) để lưu vào dự án, hoặc mở trang trên claude.ai."; return; }
    $("status").textContent = "Đăng nhập claude.ai để lưu điều chỉnh. Bạn vẫn chỉnh thử được trên model."; refresh(); return;
  }''')])

edit(os.path.join(W, "review_page", "index.html"), [(
'''  if (!window.claude || !window.claude.use) { renderNotes(); return; }
  const [d, u, cm] = await Promise.all([claude.use("db"), claude.use("user"), claude.use("comments")]);
  db = d; user = u; comments = cm;''',
'''  const hasClaude = !!(window.claude && window.claude.use);
  let d = null, u = null, cm = null;
  if (hasClaude) [d, u, cm] = await Promise.all([claude.use("db"), claude.use("user"), claude.use("comments")]);
  if (!d) d = await window.localDB();   // không có db claude.ai: dùng kho trên máy (Home server)
  db = d; user = u; comments = cm;
  try { window.dbWidget({ db, cols: ["notes", "rounds"], host: ".top" }); } catch (e) { console.error(e); }
  if (!hasClaude && !db) { renderNotes(); return; }''')])

edit(os.path.join(W, "rig_lab", "template.html"), [(
'''  if (!db) saveMsg = saveMsg || "Chưa nối được db: chỉ lưu trong trình duyệt này, AI không đọc được.";''',
'''  if (!db) { try { db = await window.localDB(); } catch (e) { db = null; } }   // không có db claude.ai: kho trên máy (Home server)
  try { window.dbWidget({ db, cols: ["rig"], host: "header" }); } catch (e) { console.error(e); }
  if (!db) saveMsg = saveMsg || "Chưa nối được db: chỉ lưu trong trình duyệt này, AI không đọc được.";'''),
('''      saveMsg = "Đã nối db: lưu cho AI đọc được.";''',
 '''      saveMsg = db.isLocal ? "Đã lưu vào dự án trên máy (work/store)." : "Đã nối db: lưu cho AI đọc được.";''')])

edit(os.path.join(W, "mesh_lab", "template.html"), [])   # Mesh Lab tự gọi window.localDB / dbWidget khi khởi động
