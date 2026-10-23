# Một lần: cổng duyệt + ghi chú cố định ở cuối panel phải, phần còn lại cuộn
p = "template.html"
s = open(p, encoding="utf8").read()
def rep(a, b):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b, 1)
rep("aside{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:12px;min-width:0;max-height:78vh;overflow:auto}",
    "aside{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:0;min-width:0;height:min(78vh,720px);display:flex;flex-direction:column;overflow:hidden}\naside .pbody{flex:1;min-height:0;overflow:auto;padding:12px}\naside>.pbody:only-child{padding-bottom:12px}")
rep(".gate{margin-top:14px;padding-top:10px;border-top:1px solid var(--line)}",
    ".gate{flex:none;margin:0;padding:10px 12px 12px;border-top:1px solid var(--line);background:var(--panel)}\n.gate h2{margin:0 0 4px}")
rep("aside{max-height:none}", "aside{height:auto;overflow:visible} aside .pbody{overflow:visible}")
rep("  wirePanel(); renderJointBox();\n}", "  dockGate(p); wirePanel(); renderJointBox();\n}\nfunction dockGate(p) {   // cổng duyệt cố định ở đáy panel, phần còn lại cuộn\n  const g = p.querySelector(\".gate\"), body = document.createElement(\"div\"); body.className = \"pbody\";\n  while (p.firstChild && p.firstChild !== g) body.appendChild(p.firstChild);\n  p.insertBefore(body, g || null);\n}")
open(p, "w", encoding="utf8").write(s)
