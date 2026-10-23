p = "template.html"
s = open(p, encoding="utf8").read()
def rep(a, b):
    global s
    assert a in s, a[:60]
    s = s.replace(a, b, 1)
rep("let step = 1, sel = null,", "const vis = { body: true, props: DATA.props.map(() => true) };\nlet step = 1, sel = null,")
rep("  bodyMesh.userData.wire.visible = showWire;",
    "  bodyMesh.visible = vis.body; propMeshes.forEach((m, i) => m.visible = vis.props[i]);\n  bodyMesh.userData.wire.visible = showWire;")
rep('''$("vopts").innerHTML = `<label class="t"><input type="checkbox" id="owire" ${showWire ? "checked" : ""}> Lưới</label>` +''',
    '''$("vopts").innerHTML = `<label class="t"><input type="checkbox" id="ovb" ${vis.body ? "checked" : ""}> Thân</label>` +
    DATA.props.map((x, i) => `<label class="t"><input type="checkbox" class="ovp" data-i="${i}" ${vis.props[i] ? "checked" : ""}> ${x.name.replace("EN_M11_Boss_Gaygor_", "Prop ")}</label>`).join("") +
    `<label class="t"><input type="checkbox" id="owire" ${showWire ? "checked" : ""}> Lưới</label>` +''')
rep('const w = $("owire");', '$("ovb").onchange = e => { vis.body = e.target.checked; syncScene(); };\n  document.querySelectorAll(".ovp").forEach(c => c.onchange = () => { vis.props[+c.dataset.i] = c.checked; syncScene(); });\n  const w = $("owire");')
open(p, "w", encoding="utf8").write(s)
