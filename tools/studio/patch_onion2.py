"""Bản vá 2 cho onion skin (sau patch_onion.py), user 2026-10-28: "Đổi thành nhập số key. và hiện ghost bằng pose đó".
Ô chọn chế độ → ô nhập frame ("1" hoặc "1, 7"): mỗi frame một bóng (trước frame đang xem = cam, sau = xanh, trùng = xám).
Ô trống = key ngay trước + ngay sau (mặc định cũ). Bỏ chế độ "Pose gốc".
Áp CÙNG bản vá vào work/pose_lab/index.html và tools/studio/modules/pose_engine.js (không chạy port_pose.py, xem patch_onion.py).
Chạy: python -I tools/studio/patch_onion2.py   (chạy lại an toàn)"""
import os, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
FILES = [os.path.join(ROOT, "work", "pose_lab", "index.html"), os.path.join(ROOT, "tools", "studio", "modules", "pose_engine.js")]

INPUT = r'''(function () {   // ô nhập frame cho bóng mờ cạnh nút (như Ghost Options → custom frames của Maya)
  const b = $("tGhost"); if (!b || $("tGhostF")) return;
  const s = document.createElement("input"); s.id = "tGhostF"; s.type = "text"; s.inputMode = "numeric"; s.className = "ghostf";
  s.style.cssText = "height:28px;width:72px;margin:0 4px 0 2px;font-size:12px;padding:0 6px";
  s.placeholder = "F: 1, 7"; s.value = ONION.frames;
  s.title = "Bóng mờ (như Ghost của Maya): gõ frame cần hiện pose, vd 1 hoặc 1, 7 rồi Enter. Trước frame đang xem = cam, sau = xanh. Để trống = key ngay trước + ngay sau";
  const apply = () => { ONION.frames = s.value.trim(); try { localStorage.setItem("pl:onionF", ONION.frames); } catch (e) {} if (!b.classList.contains("on")) b.click(); else goto(frame); };
  s.addEventListener("change", apply);
  s.addEventListener("keydown", e => { e.stopPropagation(); if (e.key === "Enter") { apply(); s.blur(); } });   // phím gõ không chạy phím tắt của Pose
  b.after(s);
})();'''

REPL = [
    ('const ONION = { mode: "k1", src: null, list: [], loading: null, off: 0 };\ntry { ONION.mode = localStorage.getItem("pl:onion") || "k1"; } catch (e) {}',
     'const ONION = { mode: "k1", frames: "", src: null, list: [], loading: null, off: 0 };\ntry { ONION.frames = localStorage.getItem("pl:onionF") || ""; } catch (e) {}'),
    ('const onionOn = () => $("tGhost") && $("tGhost").classList.contains("on") && ONION.mode !== "orig";',
     'const onionOn = () => $("tGhost") && $("tGhost").classList.contains("on");'),
    ('function onionFrames(f) {\n  const m = ONION.mode, n = NFR();',
     'function onionFrames(f) {\n  const n = NFR(), want = [...new Set(String(ONION.frames || "").split(/[^0-9]+/).filter(Boolean).map(Number).filter(x => x >= 1 && x <= n))].slice(0, 6);\n'
     '  if (want.length) return want.map(x => ({ f: x, side: x < f ? -1 : x > f ? 1 : 0, i: 0 }));   // frame người dùng nhập\n'
     '  const m = ONION.mode;'),
    ('const col = it.side < 0 ? 0xff8a3d : 0x3da5ff,', 'const col = it.side < 0 ? 0xff8a3d : it.side > 0 ? 0x3da5ff : 0xc3c9d4,'),
]


def swap_block(s):
    """Thay khối IIFE ô chọn chế độ (từ dòng chú thích tới '})();') bằng ô nhập."""
    a = s.find("(function () {   // ô chọn chế độ bóng mờ")
    if a < 0: return s, 0
    b = s.find("})();", a) + len("})();")
    return s[:a] + INPUT + s[b:], 1


for p in FILES:
    raw = open(p, "rb").read().decode("utf8"); crlf = "\r\n" in raw; s = raw.replace("\r\n", "\n")
    if "tGhostF" in s: print("đã vá:", os.path.relpath(p, ROOT)); continue
    for old, new in REPL:
        assert s.count(old) == 1, "%s: không thấy '%s…'" % (os.path.basename(p), old[:60])
        s = s.replace(old, new)
    s, n = swap_block(s); assert n == 1, "không thấy ô chọn chế độ"
    if crlf: s = s.replace("\n", "\r\n")
    open(p, "wb").write(s.encode("utf8")); print("vá xong:", os.path.relpath(p, ROOT))
