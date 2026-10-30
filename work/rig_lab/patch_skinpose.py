# Một lần: bước 4 (Skin) cũng có pose thử (nút pose + thanh xoay) để tô phần bị khuất
p = "template.html"
s = open(p, encoding="utf8").read()


def rep(a, b, cnt=1):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b) if cnt == 0 else s.replace(a, b, cnt)


# raycast phải dùng bounding mới sau khi pose
rep("skinGeo.computeVertexNormals(); skinWire.geometry.dispose(); skinWire.geometry = new THREE.WireframeGeometry(skinGeo);\n  const sum",
    "skinGeo.computeVertexNormals(); skinGeo.computeBoundingSphere(); skinGeo.computeBoundingBox(); skinWire.geometry.dispose(); skinWire.geometry = new THREE.WireframeGeometry(skinGeo);\n  const sum")
# bước 4 hiển thị theo pose hiện tại
rep("  if (step === 4) { skinGeo.attributes.position.array.set(DATA.body.verts); skinGeo.attributes.position.needsUpdate = true; skinGeo.computeVertexNormals(); skinWire.geometry.dispose(); skinWire.geometry = new THREE.WireframeGeometry(skinGeo); strainOn = false; paintSkin(); }",
    "  if (step === 4) { strainOn = false; poseSkin(); paintSkin(); }")
# xương và chấm chọn theo pose ở bước 4 và 5
rep("PB = step === 5 && SK ? posedBones(B) : null", "PB = step >= 4 && SK ? posedBones(B) : null", 0)
rep("const pos = step === 5 && SK ? posedBones(B)[name] : b.pos;", "const pos = step >= 4 && SK ? posedBones(B)[name] : b.pos;")
# cọ dùng vị trí đã pose
rep("const d = Math.hypot(bodyV[i][0] - pt.x, bodyV[i][1] - pt.y, bodyV[i][2] - pt.z); if (d > brush.r) continue;",
    "const d = Math.hypot(PP[3 * i] - pt.x, PP[3 * i + 1] - pt.y, PP[3 * i + 2] - pt.z); if (d > brush.r) continue;")
rep("  const j = SK.idx[skinBone], jm = SK.idx[mirName(skinBone)],", "  const PP = skinGeo.attributes.position.array, j = SK.idx[skinBone], jm = SK.idx[mirName(skinBone)],")
# chọn joint đồng bộ xương xoay
rep("if (step === 4) { skinBone = name; if (skinView === \"dom\") skinView = \"one\"; paintSkin(); } else poseBone = name;",
    "if (step === 4) { skinBone = name; if (!/Twist/.test(name)) poseBone = name; if (skinView === \"dom\") skinView = \"one\"; paintSkin(); } else poseBone = name;")
# phần giao diện pose cho bước 4
rep("function setSkTool(t) {", r'''function poseSection() {
  const P = POSE[poseBone] || [0, 0, 0];
  const pres = ["Giơ tay lên", "Hạ tay", "Gập khuỷu", "Xoay cẳng tay", "Gập hông", "Ngồi xổm"].map(n => `<button data-spre="${n}">${n}</button>`).join("");
  return `<h2>Xoay thử để tô phần khuất</h2>
    <div class="sub">Xoay xương để lộ chỗ bị che rồi tô. Cọ, chọn joint và gán khối rời đều làm việc trên mesh đang pose. Click joint để chọn xương xoay.</div>
    <div class="row">${pres}<button id="spReset">Về pose gốc</button></div>
    <div class="row"><select id="spBone">${buildSkeleton(LM).filter(b => !b.twist && b.name !== "root").map(b => `<option ${b.name === poseBone ? "selected" : ""}>${b.name}</option>`).join("")}</select><button id="spClr">Về 0</button></div>
    ${[["Roll (dọc xương)", 0], ["Gập A", 1], ["Gập B", 2]].map(([t, i]) => `<div class="row" style="flex-wrap:nowrap"><label for="sp${i}" style="width:110px;font-size:12px">${t}</label><input id="sp${i}" type="range" min="-180" max="180" step="1" value="${P[i]}" style="flex:1"><span id="spv${i}" class="sub" style="width:36px;text-align:right">${P[i]}°</span></div>`).join("")}
    <div class="row"><label class="t"><input type="checkbox" id="spTw" ${poseOpt.twist ? "checked" : ""}> Dẫn động twist</label></div>`;
}
function wirePoseSection() {
  const on = (id, f) => { const e = $(id); if (e) e.addEventListener("click", f); };
  document.querySelectorAll("[data-spre]").forEach(b => b.addEventListener("click", () => { setPose(PRESETS[b.dataset.spre]); renderPanel(); }));
  on("spReset", () => { setPose({}); renderPanel(); });
  const bs = $("spBone"); if (!bs) return;
  bs.onchange = e => { poseBone = e.target.value; renderPanel(); };
  on("spClr", () => { delete POSE[poseBone]; applyPose(); renderPanel(); });
  [0, 1, 2].forEach(i => { const el = $("sp" + i); el.addEventListener("input", e => { const q = (POSE[poseBone] = POSE[poseBone] || [0, 0, 0]); q[i] = +e.target.value; $("spv" + i).textContent = q[i] + "°"; applyPose(); }); });
  $("spTw").onchange = e => { poseOpt.twist = e.target.checked; applyPose(); renderPanel(); };
}
function setSkTool(t) {''')
rep("      <h2>Lệch nhiều nhất (theo xương khách)</h2>", "      ${poseSection()}\n      <h2>Lệch nhiều nhất (theo xương khách)</h2>")
rep("  on(\"saveSkin\", saveSkin);", "  on(\"saveSkin\", saveSkin); wirePoseSection();")
open(p, "w", encoding="utf8").write(s)
