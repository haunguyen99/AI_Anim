"""Mesh Lab → Rig Lab: Rig Lab dùng bản mesh đã sửa trong Mesh Lab (kho cục bộ, ns *_mesh_lab, doc mesh/edit) thay cho mesh gốc.
- Chạy đồng bộ (XHR) trước script chính: thay body / clothes / props theo TÊN mesh, dịch gợi ý khớp và xương khách theo phép biến đổi
  (scale theo chiều cao + dịch) đo từ hộp bao thân gốc → thân sửa.
- Landmark đã lưu từ trước được dịch một lần khi bản sửa đổi (meshAt).
- Chip ở tiêu đề: "Mesh đã sửa" / "Mesh gốc" (bấm để đổi, nhớ theo trang).
Idempotent (/*MESHLINK*/). Chạy: python work/rig_lab/patch_meshlink.py"""
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "template.html")
s = open(P, encoding="utf8").read()
if "/*MESHLINK*/" in s:
    print("already patched"); raise SystemExit

PRE = r"""<script>
/*MESHLINK*/
(function () {
  window.__meshAt = null; window.__meshT = null; window.__meshInfo = { state: "none" };
  const slug = s => String(s || "page").toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, "").slice(0, 80) || "page";
  const ns = slug(document.title).replace(/rig_lab$/, "mesh_lab"), key = "rigmesh:" + ns;
  let pref = null; try { pref = localStorage.getItem(key); } catch (e) {}
  let ed = null;
  try {
    const x = new XMLHttpRequest(); x.open("GET", (window.LOCALDB_API || "http://127.0.0.1:8780") + "/api/store/" + encodeURIComponent(ns) + "/mesh/edit", false); x.send();
    if (x.status === 200) { const j = JSON.parse(x.responseText); if (j.exists && j.data && j.data.meshes && j.data.meshes.length) ed = j.data; }
  } catch (e) {}
  if (!ed) return;
  window.__meshInfo = { state: pref === "orig" ? "orig" : "edited", at: ed.at, ns, key };
  if (pref === "orig") return;
  const bbox = a => { const mn = [1e9, 1e9, 1e9], mx = [-1e9, -1e9, -1e9]; for (let i = 0; i < a.length; i += 3) for (let k = 0; k < 3; k++) { mn[k] = Math.min(mn[k], a[i + k]); mx[k] = Math.max(mx[k], a[i + k]); } return { mn, mx }; };
  window.__meshApply = function (D) {
    const by = {}; ed.meshes.forEach(m => { if (m.vis !== false) by[m.name] = m; });
    const take = (o, m) => { o.verts = m.verts; o.tris = m.tris; };
    const bn = D.body.name; let used = 0;
    if (!bn || !by[bn]) { window.__meshInfo = { state: "nobody", at: ed.at, ns, key, note: "Mesh Lab không có mesh thân '" + bn + "' (ẩn hoặc đổi tên): giữ mesh gốc." }; return D; }
    const o0 = bbox(D.body.verts), o1 = bbox(by[bn].verts), f = (o1.mx[1] - o1.mn[1]) / Math.max(1e-6, o0.mx[1] - o0.mn[1]);
    const c0 = [(o0.mn[0] + o0.mx[0]) / 2, o0.mn[1], (o0.mn[2] + o0.mx[2]) / 2], c1 = [(o1.mn[0] + o1.mx[0]) / 2, o1.mn[1], (o1.mn[2] + o1.mx[2]) / 2];
    const T = p => [c1[0] + (p[0] - c0[0]) * f, c1[1] + (p[1] - c0[1]) * f, c1[2] + (p[2] - c0[2]) * f];
    const same = D.body.verts.length === by[bn].verts.length;
    take(D.body, by[bn]); used++;
    (D.clothes || []).forEach(c => { if (by[c.name]) { take(c, by[c.name]); used++; } });
    (D.props || []).forEach(p => { if (by[p.name]) { take(p, by[p.name]); used++; } });
    if (Math.abs(f - 1) > 1e-4 || c0.some((v, i) => Math.abs(v - c1[i]) > 1e-3)) {
      for (const k in D.auto.landmarks) D.auto.landmarks[k] = T(D.auto.landmarks[k]).map(v => +v.toFixed(3));
      if (D.auto.H) D.auto.H = +(D.auto.H * f).toFixed(3);
      (D.ref || []).forEach(b => { if (b.pos) b.pos = T(b.pos); });
      window.__meshT = { f, c0, c1 };
    }
    if (!same) D.refW = {};   // skin khách theo số điểm cũ: không còn khớp
    const extra = ed.meshes.filter(m => m.vis !== false && !["body"].includes(m.name) && m.name !== bn && !(D.clothes || []).some(c => c.name === m.name) && !(D.props || []).some(p => p.name === m.name)).length;
    window.__meshAt = ed.at; window.__meshInfo = { state: "edited", at: ed.at, ns, key, used, extra, same, scale: +f.toFixed(4) };
    return D;
  };
  window.__meshLM = function (L) {   // landmark đã lưu theo mesh cũ → dịch theo phép biến đổi
    const T = window.__meshT; if (!T) return L; const o = {};
    for (const k in L) o[k] = Array.isArray(L[k]) && L[k].length === 3 ? [T.c1[0] + (L[k][0] - T.c0[0]) * T.f, T.c1[1] + (L[k][1] - T.c0[1]) * T.f, T.c1[2] + (L[k][2] - T.c0[2]) * T.f].map(v => +v.toFixed(3)) : L[k];
    return o;
  };
})();
</script>
"""

def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)

# 1) pre-script chạy sau shim LOCALDB, trước script chính
i = s.index("<script>\n", s.index("/*LOCALDB*/"))      # script ngay sau shim = script chính
i = s.rindex("<script>\n", 0, s.index("/*LOCALDB*/") + 1) if False else None
j = s.index("</script>\n", s.index("/*LOCALDB*/")) + len("</script>\n")
s = s[:j] + PRE + s[j:]
rep("const DATA = /*DATA*/null;", "const DATA = (window.__meshApply || (d => d))(/*DATA*/null);")
# 2) landmark đã lưu: dịch một lần khi bản sửa đổi
rep('''      const a = await db.doc("rig/landmarks").get(); if (a.exists && a.data().lm) LM = completeLM(a.data().lm);''',
    '''      const a = await db.doc("rig/landmarks").get(); if (a.exists && a.data().lm) { LM = completeLM(a.data().lm); if (window.__meshAt && a.data().meshAt !== window.__meshAt) { LM = completeLM(window.__meshLM(LM)); setTimeout(dirty, 800); } }''')
rep('''if (db) await db.doc("rig/landmarks").set({ lm: LM, tw: TW, at: Date.now() });''', '''if (db) await db.doc("rig/landmarks").set({ lm: LM, tw: TW, at: Date.now(), meshAt: window.__meshAt || null });''')
# 3) chip trong tiêu đề
rep('''  <div><h1>__NAME__ Rig Lab</h1></div>''', '''  <div><h1>__NAME__ Rig Lab</h1></div>
  <button id="meshChip" class="tool" hidden></button>''')
k = s.rfind("</script>")
JS = r"""
/*MESHLINK*/
(function () {
  const I = window.__meshInfo || { state: "none" }, b = document.getElementById("meshChip"); if (!b || I.state === "none") return;
  const when = I.at ? String(I.at).slice(0, 16).replace("T", " ") : "";
  b.hidden = false;
  if (I.state === "edited") { b.textContent = "Mesh đã sửa"; b.title = "Đang dùng mesh sửa trong Mesh Lab (" + when + ")" + (I.same ? "" : ", số điểm đã đổi nên skin cần tính lại") + (I.scale && Math.abs(I.scale - 1) > 1e-3 ? ", scale ×" + I.scale : "") + (I.extra ? ", " + I.extra + " mesh mới chưa dùng" : "") + ". Bấm để dùng mesh gốc."; }
  else if (I.state === "orig") { b.textContent = "Mesh gốc"; b.title = "Mesh Lab có bản đã sửa (" + when + "). Bấm để dùng bản đã sửa."; }
  else { b.textContent = "Mesh gốc"; b.title = I.note || ""; b.disabled = true; }
  b.style.cssText = "font-size:12px;padding:3px 8px;border-radius:6px;" + (I.state === "edited" ? "background:var(--accent);color:var(--accent-fg);border-color:var(--accent)" : "");
  b.onclick = () => { if (I.state === "nobody") return; try { localStorage.setItem(I.key, I.state === "edited" ? "orig" : "edited"); } catch (e) {} location.reload(); };
})();
"""
s = s[:k] + JS + s[k:]
open(P, "w", encoding="utf8", newline="").write(s)
print("ok")
