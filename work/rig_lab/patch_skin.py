# Một lần: ghép M2 (skin_part.js) vào template.html và thêm bước 4 Skin, bước 5 Thử khớp
p = "template.html"
s = open(p, encoding="utf8").read()


def rep(a, b):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b, 1)


js = open("skin_part.js", encoding="utf8").read()
rep('renderVbar(); resize(); setView("front")', js + '\nrenderVbar(); resize(); setView("front")')
rep("let gates = { 1: null, 2: null, 3: null };", "let gates = { 1: null, 2: null, 3: null, 4: null, 5: null };")
rep('const names = ["1 · Mesh", "2 · Khớp", "3 · Skeleton"];', 'const names = ["1 · Mesh", "2 · Khớp", "3 · Skeleton", "4 · Skin", "5 · Thử khớp"];')
rep("${gateHtml(3)}`;\n  }\n  wirePanel();", "${gateHtml(3)}`;\n  } else if (step === 4) { renderSkinPanel(p); } else { renderPosePanel(p); }\n  wirePanel();")
rep("  } else {\n    const checks = skelChecks()", "  } else if (step === 3) {\n    const checks = skelChecks()")
# vẽ xương theo pose ở bước 5
rep("  const seg = [], pts = [];\n  const tpts = [];\n  B.forEach(b => { if (b.twist) { tpts.push(...b.pos); return; } pts.push(...b.pos); if (b.parent && b.parent !== \"root\") seg.push(...idx[b.parent].pos, ...b.pos); });",
    "  const seg = [], pts = [], tpts = [], PB = step === 5 && SK ? posedBones(B) : null, ps = b => PB ? PB[b.name] : b.pos;\n  B.forEach(b => { if (b.twist) { tpts.push(...ps(b)); return; } pts.push(...ps(b)); if (b.parent && b.parent !== \"root\") seg.push(...ps(idx[b.parent]), ...ps(b)); });")
rep("  bodyMesh.visible = vis.body;", "  bodyMesh.visible = vis.body && step < 4; skinMesh.visible = vis.body && step >= 4 && !!SK; if (step < 4) skinWire.visible = false;\n  if (SK && step >= 4) skinMesh.material.opacity = 1;\n ")
# mở bước 4/5: đặt lại vị trí mesh skin
rep("function go(n) { step = n;", '''function showSkinFor() {
  if (!SK) return;
  if (step === 4) { skinGeo.attributes.position.array.set(DATA.body.verts); skinGeo.attributes.position.needsUpdate = true; skinGeo.computeVertexNormals(); skinWire.geometry.dispose(); skinWire.geometry = new THREE.WireframeGeometry(skinGeo); strainOn = false; paintSkin(); }
  if (step === 5) { poseSkin(); paintSkin(); }
}
function go(n) { step = n; showSkinFor();''')
open(p, "w", encoding="utf8").write(s)
