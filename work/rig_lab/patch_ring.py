# Một lần: con trỏ cọ là một đường tròn nằm trên bề mặt (thay cho quả cầu lưới)
p = "template.html"
s = open(p, encoding="utf8").read()


def rep(a, b):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b, 1)


rep('''const ring = new THREE.Mesh(new THREE.SphereGeometry(1, 20, 14), new THREE.MeshBasicMaterial({ color: 0xffffff, wireframe: true, transparent: true, opacity: .45, depthTest: false }));''',
    '''const ringPts = []; for (let k = 0; k < 64; k++) { const a = k / 64 * Math.PI * 2; ringPts.push(new THREE.Vector3(Math.cos(a), Math.sin(a), 0)); }
const ring = new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(ringPts), new THREE.LineBasicMaterial({ color: 0xffffff, depthTest: false }));''')
rep('''  const h = ray.intersectObject(skinMesh, false)[0]; return h ? h.point : null;
}''', '''  const h = ray.intersectObject(skinMesh, false)[0]; return h ? h.point : null;
}
function brushHitFull(e) {
  const r = cv.getBoundingClientRect();
  ray.setFromCamera({ x: ((e.clientX - r.left) / r.width) * 2 - 1, y: -((e.clientY - r.top) / r.height) * 2 + 1 }, cam);
  return ray.intersectObject(skinMesh, false)[0] || null;
}''')
rep('''{ const pt = brushHit(e); ring.visible = !!pt; if (pt) { ring.position.copy(pt); ring.scale.setScalar(brush.r); } } else ring.visible = false;''',
    '''{ const h = brushHitFull(e); ring.visible = !!h; if (h) { ring.position.copy(h.point).addScaledVector(h.face.normal, 0.3); ring.lookAt(h.point.clone().add(h.face.normal)); ring.scale.setScalar(brush.r); ring.material.color.set(brush.mode === "sub" ? css("--bad") : css("--fg")); } } else ring.visible = false;''')
open(p, "w", encoding="utf8").write(s)
