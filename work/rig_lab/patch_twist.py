# Một lần: thêm twist joint (số lượng theo đoạn tay/chân, dẫn động roll) vào template.html
p = "template.html"
s = open(p, encoding="utf8").read()


def rep(a, b):
    global s
    assert a in s, a[:60]
    s = s.replace(a, b, 1)


# trạng thái + định nghĩa đoạn
rep("const vis = {", '''// twist joint: số lượng theo đoạn (khớp đầu đoạn), áp cho cả R và L. Tên: <Khớp đầu>Twist<i>_<R|L>
const TW_SEG = { Shoulder: ["Elbow", "Cánh tay trên"], Elbow: ["Wrist", "Cẳng tay"], Hip: ["Knee", "Đùi"], Knee: ["Ankle", "Cẳng chân"] };
let TW = { Shoulder: 0, Elbow: 0, Hip: 0, Knee: 0 };
const vis = {''')
# bone generation
rep('  add("Weapon", "root", P("Weapon"));\n  return B;', '''  add("Weapon", "root", P("Weapon"));
  // twist: đoạn đầu (Shoulder/Hip) nhận roll NGƯỢC t lần roll của khớp đầu; đoạn cuối (Elbow/Knee) nhận roll +t lần roll của Wrist/Ankle
  const byName = {}; B.forEach(b => byName[b.name] = b);
  for (const s of ["R", "L"]) for (const st in TW_SEG) {
    const n = TW[st], a = byName[st + "_" + s], z = byName[TW_SEG[st][0] + "_" + s];
    for (let i = 1; i <= n; i++) {
      const t = i / (n + 1), proximal = st === "Shoulder" || st === "Hip";
      B.push({ name: st + "Twist" + i + "_" + s, parent: st + "_" + s, pos: a.pos.map((v, k) => v + (z.pos[k] - v) * t),
        twist: { source: proximal ? st + "_" + s : z.name, factor: +(proximal ? -t : t).toFixed(4), axis: "segment", segment: [st + "_" + s, z.name] } });
    }
  }
  return B;''')
# vẽ điểm twist
rep("const skelPts = new THREE.Points(", '''const twPts = new THREE.Points(new THREE.BufferGeometry(), new THREE.PointsMaterial({ size: 7, sizeAttenuation: false, depthTest: false, color: 0xffaa00 }));
twPts.renderOrder = 9; scene.add(twPts);
const skelPts = new THREE.Points(''')
rep('  B.forEach(b => { pts.push(...b.pos); if (b.parent && b.parent !== "root") seg.push(...idx[b.parent].pos, ...b.pos); });',
    '  const tpts = [];\n  B.forEach(b => { if (b.twist) { tpts.push(...b.pos); return; } pts.push(...b.pos); if (b.parent && b.parent !== "root") seg.push(...idx[b.parent].pos, ...b.pos); });\n  twPts.geometry.setAttribute("position", new THREE.Float32BufferAttribute(tpts, 3)); twPts.material.color.set(css("--warn"));')
rep("skelLines.visible = skelPts.visible = step >= 3 || (step === 2 && showSkel);",
    "skelLines.visible = skelPts.visible = step >= 3 || (step === 2 && showSkel); twPts.visible = step >= 3;")
# lưu/đọc
rep('if (a.exists && a.data().lm) LM = a.data().lm;', 'if (a.exists && a.data().lm) LM = a.data().lm; if (a.exists && a.data().tw) TW = Object.assign(TW, a.data().tw);')
rep('const a = localStorage.getItem("rig_lm"); if (a) LM = JSON.parse(a);', 'const a = localStorage.getItem("rig_lm"); if (a) LM = JSON.parse(a); const t = localStorage.getItem("rig_tw"); if (t) TW = Object.assign(TW, JSON.parse(t));')
rep('set({ lm: LM, at: Date.now() }); else localStorage.setItem("rig_lm", JSON.stringify(LM));',
    'set({ lm: LM, tw: TW, at: Date.now() }); else { localStorage.setItem("rig_lm", JSON.stringify(LM)); localStorage.setItem("rig_tw", JSON.stringify(TW)); }')
# xuất
rep("landmarks: LM, bones: B.map(b => ({ name: b.name, parent: b.parent, head: b.pos.map(v => +v.toFixed(3)) })) };",
    "landmarks: LM, twist_counts: TW, bones: B.map(b => Object.assign({ name: b.name, parent: b.parent, head: b.pos.map(v => +v.toFixed(3)) }, b.twist ? { twist: b.twist } : {})) };")
# QA: tên
rep("extra = [...mine].filter(n => !refNames.has(n));", "extra = [...mine].filter(n => !refNames.has(n) && !/Twist\\d/.test(n));")
# panel
rep('<span>Quy ước</span><span>tên rig khách, cm, +Y lên, +Z trước</span></div>', '''<span>Quy ước</span><span>tên rig khách, cm, +Y lên, +Z trước</span></div>
      <h2>Twist joint</h2>
      <div class="sub">Số xương twist trên mỗi đoạn, áp cho cả hai bên. Điểm màu cam trên viewport. Xương twist là con của khớp đầu đoạn; roll được dẫn động theo hệ số ghi trong rig.json.</div>
      <div class="kv" style="align-items:center">${Object.keys(TW_SEG).map(st => `<span><label for="tw_${st}">${TW_SEG[st][1]}</label></span><span><select id="tw_${st}">${[0, 1, 2, 3].map(n => `<option value="${n}" ${TW[st] === n ? "selected" : ""}>${n}</option>`).join("")}</select></span>`).join("")}</div>
      <div class="row"><button data-tw="0">Không twist</button><button data-tw="1">1 mỗi đoạn</button><button data-tw="2">2 mỗi đoạn</button></div>''')
rep('  const m = $("mir");', '''  Object.keys(TW_SEG).forEach(st => { const e = $("tw_" + st); if (e) e.addEventListener("change", () => { TW[st] = +e.value; syncScene(); dirty(); renderPanel(); }); });
  document.querySelectorAll("[data-tw]").forEach(b => b.addEventListener("click", () => { Object.keys(TW).forEach(st => TW[st] = +b.dataset.tw); syncScene(); dirty(); renderPanel(); }));
  const m = $("mir");''')
open(p, "w", encoding="utf8").write(s)
