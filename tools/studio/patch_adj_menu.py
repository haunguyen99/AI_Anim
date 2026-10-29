"""Vá lõi Pose: nút Sửa / Xoá của điều chỉnh key thu vào menu ⋯ ở góc phải dòng đầu (cạnh nhãn chờ AI).
User 2026-10-29: "Đổi các nút này thành icon 3 chấm ở góc này cho tiện".
Áp CÙNG bản vá vào work/pose_lab/index.html và tools/studio/modules/pose_engine.js (không chạy port_pose.py). Chạy lại an toàn."""
import os, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
FILES = [os.path.join(ROOT, "work", "pose_lab", "index.html"), os.path.join(ROOT, "tools", "studio", "modules", "pose_engine.js")]
OLD = '''    el.append(row); box.append(el);
  }
}'''
NEW = '''    if (row.children.length) {   // menu ⋯ ở góc dòng đầu thay hàng nút (user 2026-10-29)
      el.style.position = "relative";
      const kb = document.createElement("button"); kb.className = "btn akebab"; kb.textContent = "⋯"; kb.title = "Sửa / Xoá"; kb.setAttribute("aria-label", "Sửa hoặc xoá");
      kb.style.cssText = "padding:0 8px;min-height:0;height:22px;line-height:20px;font-size:16px;margin-left:6px;background:transparent;border:0;cursor:pointer;color:inherit";
      row.hidden = true; row.style.cssText = "position:fixed;z-index:50;min-width:90px;flex-direction:column;align-items:stretch;gap:4px;padding:6px;background:var(--panel,#1f2430);border:1px solid var(--line,#333);border-radius:8px;box-shadow:0 6px 18px rgba(0,0,0,.4)";
      // menu nổi (fixed) theo vị trí nút ⋯: khung cuộn của panel không cắt mất; bấm ra ngoài / cuộn thì đóng
      const close = () => { row.hidden = true; row.style.display = "none"; document.removeEventListener("pointerdown", outside, true); };
      const outside = e => { if (!row.contains(e.target) && e.target !== kb) close(); };
      kb.onclick = e => { e.stopPropagation(); if (!row.hidden) return close();
        const r = kb.getBoundingClientRect(); row.hidden = false; row.style.display = "flex";
        row.style.top = Math.min(r.bottom + 4, innerHeight - row.offsetHeight - 8) + "px"; row.style.left = Math.max(8, r.right - row.offsetWidth) + "px";
        document.addEventListener("pointerdown", outside, true); };
      row.style.display = "none";
      row.addEventListener("click", e => e.stopPropagation());
      for (const b of row.querySelectorAll("button")) { const f = b.onclick; if (b.textContent === "Sửa") b.onclick = ev => { row.style.cssText = ""; row.hidden = false; kb.remove(); f(ev); }; }
      const grp = document.createElement("span"); grp.style.cssText = "display:inline-flex;align-items:center;gap:2px"; pill.replaceWith(grp); grp.append(kb, pill);   // ⋯ ngay trước nhãn trạng thái
    }
    el.append(row); box.append(el);
  }
}'''
for p in FILES:
    raw = open(p, "rb").read().decode("utf8"); crlf = "\r\n" in raw; s = raw.replace("\r\n", "\n")
    if "akebab" in s: print("đã vá:", os.path.relpath(p, ROOT)); continue
    assert s.count(OLD) == 1, os.path.basename(p) + ": không thấy cuối renderAdjs"
    s = s.replace(OLD, NEW)
    if crlf: s = s.replace("\n", "\r\n")
    open(p, "wb").write(s.encode("utf8")); print("vá xong:", os.path.relpath(p, ROOT))
