# Rig Lab: mọi nút là icon (chữ thành tooltip), theo docs/ui_guidelines.md.
# Các nút được dựng lại bằng innerHTML nhiều lần, nên một script cuối trang gắn icon lại theo bộ chọn mỗi khi DOM đổi.
import os, urllib.parse, json
R = os.path.dirname(os.path.abspath(__file__)); p = f"{R}/template.html"; s = open(p, encoding="utf8").read()
assert "/*IBTN*/" not in s, "đã patch rồi"

I = {
 "help": '<circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 114 2c-1 .7-1.5 1.2-1.5 2.5M12 17h.01"/>',
 "mesh": '<path d="M12 3l8 4.5v9L12 21l-8-4.5v-9z"/><path d="M12 12l8-4.5M12 12v9M12 12L4 7.5"/>',
 "joints": '<circle cx="6" cy="6" r="2"/><circle cx="18" cy="12" r="2"/><circle cx="8" cy="19" r="2"/><path d="M7.6 7.4l8.8 3.6M16.4 13.4L9.6 17.6"/>',
 "bone": '<path d="M7 17a2.5 2.5 0 11-3.5-3.5L14 3a2.5 2.5 0 113.5 3.5 2.5 2.5 0 11-3.5 3.5L9.5 14.5A2.5 2.5 0 017 17z" transform="translate(1 2) scale(.9)"/>',
 "skin": '<path d="M12 3c4 5 6 8 6 11a6 6 0 01-12 0c0-3 2-6 6-11z"/>',
 "figure": '<circle cx="12" cy="5" r="2.3"/><path d="M12 8v7M6.5 10.5L12 8l5.5 2.5M9 21l3-6 3 6"/>',
 "vFront": '<rect x="5" y="5" width="14" height="14" rx="1"/>',
 "vSide": '<path d="M8 5l10 3v11l-10-3z"/>',
 "vTop": '<path d="M12 4l8 6-8 6-8-6z"/>',
 "vPersp": '<path d="M12 3l8 4.5v9L12 21l-8-4.5v-9z"/><path d="M12 12l8-4.5M12 12v9M12 12L4 7.5"/>',
 "undo": '<path d="M9 14L4 9l5-5"/><path d="M4 9h10a6 6 0 010 12h-3"/>',
 "redo": '<path d="M15 14l5-5-5-5"/><path d="M20 9H10a6 6 0 000 12h3"/>',
 "pointer": '<path d="M5 3l12 7-5.5 1.5L9 17z"/>',
 "move": '<path d="M12 3v18M3 12h18M12 3l-3 3M12 3l3 3M12 21l-3-3M12 21l3-3M3 12l3-3M3 12l3 3M21 12l-3-3M21 12l-3 3"/>',
 "rotate": '<path d="M20 12a8 8 0 11-2.6-5.9"/><path d="M20 4v5h-5"/>',
 "scale": '<path d="M14 4h6v6M10 20H4v-6M20 4l-7 7M4 20l7-7"/>',
 "check": '<path d="M5 12.5l4.5 4.5L19 7"/>',
 "edit": '<path d="M4 20l4-1 11-11-3-3L5 16z"/><path d="M14 6l3 3"/>',
 "done": '<circle cx="12" cy="12" r="9"/><path d="M8 12.5l3 3 5-6"/>',
 "waiting": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>',
 "arrowR": '<path d="M5 12h14M13 6l6 6-6 6"/>',
 "reset": '<path d="M4 12a8 8 0 108-8 8 8 0 00-5.7 2.4L4 9"/><path d="M4 4v5h5"/>',
 "close": '<path d="M6 6l12 12M18 6L6 18"/>',
 "download": '<path d="M12 4v11M7.5 10.5L12 15l4.5-4.5M5 20h14"/>',
 "bolt": '<path d="M13 3L5 14h6l-1 7 8-11h-6z"/>',
 "scan": '<path d="M4 8V5a1 1 0 011-1h3M16 4h3a1 1 0 011 1v3M20 16v3a1 1 0 01-1 1h-3M8 20H5a1 1 0 01-1-1v-3M4 12h16"/>',
 "play": '<path d="M8 5l11 7-11 7z"/>',
 "chevL": '<path d="M15 5l-7 7 7 7"/>',
 "chevR": '<path d="M9 5l7 7-7 7"/>',
 "tw0": '<circle cx="12" cy="12" r="8"/><path d="M6.3 6.3l11.4 11.4"/>',
 "tw1": '<path d="M5 12h14"/>',
 "tw2": '<path d="M5 9h14M5 15h14"/>',
 "brush": '<path d="M18 3l3 3-9 9-3-3z"/><path d="M9 12c-3 0-5 2-5 5 0 2-1 3-1 3s3 1 5 0c2-1 3-3 3-5"/>',
 "island": '<rect x="5" y="5" width="14" height="14" rx="1" stroke-dasharray="3 2.5"/>',
 "eye": '<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
}
def uri(n):
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="black" stroke-width="1.9" '
           'stroke-linecap="round" stroke-linejoin="round">%s</svg>' % I[n])
    return 'url("data:image/svg+xml,%s")' % urllib.parse.quote(svg, safe="/:='(),")

css = ["/*IBTN*/",
 ".ibtn{font-size:0!important;line-height:0;display:inline-flex;align-items:center;justify-content:center;gap:0;width:34px;height:32px;padding:0!important;flex:none}",
 ".ibtn::before{content:'';width:18px;height:18px;flex:none;background:currentColor;-webkit-mask:var(--ic) center/contain no-repeat;mask:var(--ic) center/contain no-repeat}",
 ".step.ibtn{width:auto;padding:0 14px!important;gap:8px;height:34px}.step.ibtn .dot{order:-1}.step.ibtn::before{width:20px;height:20px}",
 ".gate .chip.ibtn{width:22px;height:22px;border:0;background:none;padding:0!important}.chip.ibtn.ok{color:var(--ok)}.chip.ibtn.fix{color:var(--bad)}.chip.ibtn:not(.ok):not(.fix){color:var(--mute)}",
 "#vopts summary.ibtn{width:30px;height:28px}#vopts .dd>summary.ibtn::before{width:18px;height:18px}",
 "#helpBtn.ibtn{width:30px;height:30px;border-radius:50%}",
 "#vbar .ibtn,.row .ibtn{border-radius:6px}",
 ".ibtn.pri::before{background:currentColor}",
]
for ic in I:
    css.append('[data-ic="%s"]{--ic:%s}' % (ic, uri(ic)))
i = s.index("</style>")
s = s[:i] + "\n".join(css) + "\n" + s[i:]

# bộ chọn -> icon. "@step" lấy icon theo data-s.
js = r"""
<script>
/* Rig Lab: nút là icon, chữ thành tooltip (docs/ui_guidelines.md). Nút được dựng lại bằng innerHTML nhiều lần,
   nên gắn lại icon sau mỗi lần DOM đổi. */
(function () {
  const STEP = { 1: "mesh", 2: "joints", 3: "bone", 4: "skin", 5: "figure" };
  const R = [
    ["#helpBtn", "help"], [".step", "@step"],
    ["#vbar [data-v=front]", "vFront"], ["#vbar [data-v=side]", "vSide"], ["#vbar [data-v=top]", "vTop"], ["#vbar [data-v=persp]", "vPersp"],
    ["#bUndo", "undo"], ["#bRedo", "redo"],
    ["[data-mode=select]", "pointer"], ["[data-mode=translate]", "move"], ["[data-mode=rotate]", "rotate"], ["[data-mode=scale]", "scale"],
    ["#gOk", "check"], ["#gFix", "edit"], ["#toStep2", "arrowR"],
    ["#resetAuto", "reset"], ["#spReset", "reset"], ["#poseReset", "reset"], ["#jClr", "reset"], ["#clr", "close"], ["#jX", "close"],
    ["#exportRig", "download"], ["#expW", "download"],
    ["#doSkin", "bolt"], ["#doSkin2", "bolt"], ["#doSkin3", "bolt"], ["#doTest", "scan"], ["#pBat", "play"],
    ["#skPrev", "chevL"], ["#skNext", "chevR"],
    ["[data-tw='0']", "tw0"], ["[data-tw='1']", "tw1"], ["[data-tw='2']", "tw2"],
    ["[data-skt=pick]", "pointer"], ["[data-skt=brush]", "brush"], ["[data-skt=island]", "island"],
    ["#vopts summary", "eye"],
    [".gate .chip.ok", "done"], [".gate .chip.fix", "edit"], [".gate .chip:not(.ok):not(.fix)", "waiting"],
  ];
  function apply() {
    for (const [sel, ic] of R) document.querySelectorAll(sel).forEach(el => {
      if (el.dataset.ic) return;
      const label = el.textContent.replace(/\s+/g, " ").trim();
      el.dataset.ic = ic === "@step" ? (STEP[el.dataset.s] || "mesh") : ic;
      el.classList.add("ibtn");
      const t0 = el.getAttribute("title");
      el.title = label && t0 && t0 !== label ? label + " - " + t0 : (label || t0 || "");
      if (label) el.setAttribute("aria-label", label);
    });
  }
  let q = 0; const sched = () => { if (!q) q = setTimeout(() => { q = 0; apply(); }, 20); };
  new MutationObserver(sched).observe(document.body, { childList: true, subtree: true });
  apply();
})();
</script>
"""
s = s.rstrip() + "\n" + js.lstrip("\n")
open(p, "w", encoding="utf8", newline="").write(s)
print("ok", len(s))
