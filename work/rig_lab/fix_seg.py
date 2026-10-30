for p in ["template.html", "skin_part.js"]:
    s = open(p, encoding="utf8").read()
    a = "const end = ks.length ? ks[0].pos : b.pos.map((v, i) => v + (v - byN[b.parent].pos[i]) * 0.5);"
    assert a in s, p
    s = s.replace(a, "const end = ks.length ? ks[0].pos : b.pos.slice();   // xương lá (Prop_M, váy): điểm seed, không kéo dài\n    const a0 = /^Hip_/.test(b.name) ? lerp(b.pos, end, 0.2) : b.pos;   // phần trên đùi thuộc vùng xương hông")
    s = s.replace("if (!n) { segs.push({ name: b.name, a: b.pos, b: end }); continue; }", "if (!n) { segs.push({ name: b.name, a: a0, b: end }); continue; }")
    s = s.replace("segs.push({ name: b.name, a: b.pos, b: lerp(b.pos, end, 1 / (n + 1)) });", "segs.push({ name: b.name, a: a0, b: lerp(a0, end, 1 / (n + 1)) });")
    s = s.replace("a: lerp(b.pos, end, i / (n + 1)), b: lerp(b.pos, end, (i + 1) / (n + 1))", "a: lerp(a0, end, i / (n + 1)), b: lerp(a0, end, (i + 1) / (n + 1))")
    open(p, "w", encoding="utf8").write(s)
