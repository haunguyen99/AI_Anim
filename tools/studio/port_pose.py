"""Sinh tools/studio/modules/pose_engine.js + pose.css từ Pose Lab (work/pose_lab/index.html, bản gốc có mọi clip).

Giữ nguyên lõi Pose Lab (key, spline, IK / pole, foot lock, timing, copy / paste, Channel Box, vật lý, ragdoll, cân bằng,
khớp ref, chân chạm sàn, ghi chú vẽ, AI tự xem, FBX, playblast), chỉ thay chỗ chạm vào renderer / camera / canvas /
OrbitControls / TransformControls / vòng vẽ / kho lưu bằng của Studio (đối tượng `host`). Giao diện Pose Lab được dựng lại
từ HTML gốc (POSE_HTML) rồi modules/pose.js đặt từng khối vào vùng của Studio (shelf, dock, timeline, lớp phủ viewport).
Chạy lại khi Pose Lab đổi:  python tools/studio/port_pose.py   (mỗi phép thay có assert).
"""
import json, os, re

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SRC = os.path.join(ROOT, "work", "pose_lab", "index.html")
OUT_JS = os.path.join(ROOT, "tools", "studio", "modules", "pose_engine.js")
OUT_CSS = os.path.join(ROOT, "tools", "studio", "pose.css")
t = open(SRC, encoding="utf8").read().replace(chr(13) + chr(10), chr(10))


def between(s, a, b, start=0):
    i = s.index(a, start) + len(a)
    return s[i:s.index(b, i)], s.index(b, i)


def rep(s, old, new, n=1):
    c = s.count(old)
    assert c == n, "thấy %d lần (cần %d): %s" % (c, n, old[:90])
    return s.replace(old, new)


def cut(s, start, end, repl=""):
    i = s.index(start); i = s.rfind("\n", 0, i) + 1
    j = s.index(end, i) + len(end)
    if not end.endswith("\n"):
        j = s.index("\n", j) + 1
    return s[:i] + repl + s[j:]


# ------------------------------------------------------------------ id trùng với vỏ Studio
studio_ids = set(re.findall(r'id="([^"]+)"', open(os.path.join(ROOT, "tools", "studio", "index.html"), encoding="utf8").read()))
studio_ids |= {"panel", "jbox", "empty", "emptyList"}
body, _ = between(t, "</style>", "<script src=")
pose_ids = set(re.findall(r'id="([^"]+)"', body))
RENAME = {i: "p_" + i for i in pose_ids & studio_ids if i not in ("cv",)}


def ren_ids(s):
    for a, b in RENAME.items():
        s = s.replace('id="%s"' % a, 'id="%s"' % b).replace('$("%s")' % a, '$("%s")' % b).replace("#" + a + " ", "#" + b + " ").replace("#" + a + "{", "#" + b + "{")
        s = s.replace("getElementById(\"%s\")" % a, "getElementById(\"%s\")" % b)
    return s


# ------------------------------------------------------------------ CSS: khoanh vào .pz
css, _ = between(t, "<style>", "</style>")
css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
STUDIO_VARS = {"--bg", "--panel", "--raise", "--line", "--accent", "--accent-fg"}


def scope_sel(s):
    s = s.strip()
    if not s:
        return s
    if s.startswith(":root"):
        return ":root"
    m = re.match(r"^(html|body)((?:[.#:\[][^\s]*)?)(\s+.*)?$", s)
    if m:
        tag, cls, rest = m.group(1), m.group(2) or "", (m.group(3) or "").strip()
        if not rest:
            return (tag + cls) if cls else None          # body / html trơn: bỏ (vỏ Studio lo); body.km: giữ (biến CSS)
        return tag + cls + " .pz " + rest
    return ".pz " + s


def scope_block(text):
    out, i = [], 0
    while i < len(text):
        j = text.find("{", i)
        if j < 0:
            break
        head = text[i:j].strip()
        if head.startswith("@media") or head.startswith("@supports"):
            depth, k = 1, j + 1
            while depth:
                depth += {"{": 1, "}": -1}.get(text[k], 0); k += 1
            out.append(head + " {" + scope_block(text[j + 1:k - 1]) + "}\n"); i = k; continue
        k = text.index("}", j)
        bodyc = text[j + 1:k]
        if head.startswith("@"):
            out.append(head + " {" + bodyc + "}\n"); i = k + 1; continue
        sels = [scope_sel(x) for x in head.split(",")]
        if ":root" in sels:
            decls = [d for d in bodyc.split(";") if d.strip() and d.split(":")[0].strip() not in STUDIO_VARS and not d.strip().startswith("color-scheme")]
            decls = [d.replace("--ink:", "--ink-pz:").replace("--muted:", "--muted-pz:") for d in decls]
            out.append(":root {" + ";".join(decls) + "; --ink: var(--fg); --muted: var(--mute); }\n")
        else:
            sels = [x for x in sels if x]
            if sels:
                out.append(", ".join(sels) + " {" + bodyc + "}\n")
        i = k + 1
    return "".join(out)


pcss = scope_block(css)
pcss = ren_ids(pcss)
pcss += """
/* ---- đặt vào vỏ Studio (modules/pose.js) */
.pz { color: var(--ink); font-family: var(--sans); font-size: 13px; line-height: 1.45; }
.pz .timeline { position: static; z-index: auto; }
.pz.pzov { position: absolute; inset: 0; pointer-events: none; z-index: 3; }
.pz.pzov > .viewer { position: absolute; inset: 0; background: none; pointer-events: none; overflow: hidden; }
.pz.pzov > .viewer > * { pointer-events: auto; }
.pz.pzov > .viewer > #drawCv { pointer-events: none; }
.pz.pzov > .viewer.drawing > #drawCv { pointer-events: auto; }
.pz.pzshelf { display: flex; align-items: center; min-width: 0; overflow-x: auto; }
.pz.pzshelf .top { border: 0; padding: 0; flex-wrap: nowrap; }
.pz.pzdock { display: block; }
.pz.pzdock .side, .pz.pzdock .list { border: 0; display: block; overflow: visible; max-height: none; }
.pz.pzdock .side > div:first-child { max-height: none; overflow: visible; }
body.ws-pose #timeline { height: auto; display: block; padding: 0; }
body.ws-pose #shelf { height: auto; min-height: 38px; }
"""
open(OUT_CSS, "w", encoding="utf8", newline=chr(10)).write("/* SINH TỰ ĐỘNG bởi tools/studio/port_pose.py từ work/pose_lab/index.html — đừng sửa tay. */\n" + pcss)

# ------------------------------------------------------------------ HTML giao diện
html = body.strip()
html = rep(html, '<canvas id="cv"></canvas>', "")
html = ren_ids(html)

# ------------------------------------------------------------------ kho lưu: LOCALDB của Pose Lab, NS theo anim
ldb, _ = between(t, "/*LOCALDB*/", "</script>")
ldb = rep(ldb, '  const API = (window.LOCALDB_API || "http://127.0.0.1:8780") + "/api/store";', '  const API = location.origin + "/api/store";')
ldb = rep(ldb, '  const NS = (new URLSearchParams(location.search).get("ns")) || slug(document.title);', "")
ldb = rep(ldb, "(function () {", "ST.poseDB = function (NS) {")
ldb = ldb.rstrip()
assert ldb.endswith("})();"), ldb[-40:]
ldb = ldb[:-len("})();")] + "  return db;\n};\n"
ldb = ldb.replace("window.localDB = async function () {", "db.ping = async function () {")
ldb = re.sub(r"\n  // ---- nút Lưu trữ.*?\n  };\n(?=  return db;)", "\n", ldb, flags=re.S)

# ------------------------------------------------------------------ lõi
ms = t.index("<script>\n// ---------------------------------------------------------------- data") + len("<script>\n")
mend = t.index("</script>", ms)
main = t[ms:mend]
m = main
m = cut(m, "const POSES = [", "\n];\n", "const POSES = POSES_IN;\n")
m = cut(m, "const canvas = $(\"cv\"), viewer = $(\"viewer\");", 'viewer.addEventListener("contextmenu", e => e.preventDefault());',
        """const canvas = host.canvas, viewer = host.viewer, renderer = host.renderer, orbit = host.orbit, gizmo = host.gizmo;
const scene = new THREE.Scene(), overlay = new THREE.Scene(); host.scenes(scene, overlay);
scene.add(new THREE.HemisphereLight(0xffffff, 0x404650, 1.0));
const sun = new THREE.DirectionalLight(0xffffff, 0.9); sun.position.set(-3, 5, 4); scene.add(sun);
const grid = new THREE.GridHelper(4, 16, 0x4a515c, 0x30353d); scene.add(grid);
gizmo.setSize(0.85); gizmo.setSpace("local");
""")
m = rep(m, """function resize() {
  const r = viewer.getBoundingClientRect();
  renderer.setSize(r.width, r.height, false); camera.aspect = r.width / Math.max(1, r.height); camera.updateProjectionMatrix();
}
new ResizeObserver(resize).observe(viewer);""", "function resize() { host.resize(); }")
m = rep(m, "renderer.clear(); renderer.render(scene, camera); renderer.clearDepth(); renderer.render(overlay, camera);   // same tick: the GL canvas is still readable",
        "host.renderNow();   // same tick: the GL canvas is still readable")
m = cut(m, "function loop(now) {", 'setCam("right"); resize(); loop(); renderPoses(); openPose(POSES[0]);',
        """host.onFrame(now => { tickPlay(now || performance.now()); if (model) placeMarkers(); if (model && trailOn) trailUpdate(); });
setCam("right"); renderPoses(); openPose(POSES[0]);
""")
m = rep(m, '  if (!d) d = await window.localDB();   // không có db claude.ai: dùng kho trên máy (Home server)', "  d = host.db;")
m = rep(m, '  try { window.dbWidget({ db, cols: ["adjusts", "rounds", "keys", "anims"], host: ".tools" }); } catch (e) { console.error(e); }', "")
m = rep(m, 'document.addEventListener("keydown", e => {\n  if (e.target.matches("textarea, input")) return;',
        'document.addEventListener("keydown", e => {\n  if (!host.alive()) return;\n  if (e.target.matches("textarea, input")) return;')
m = re.sub(r"(?<![.\w$])camera\b(?!\s*:)", "CAM()", m)
m = rep(m, 'const dl = await claude.use("downloads").catch(() => null);', 'const dl = window.claude && claude.use ? await claude.use("downloads").catch(() => null) : host.downloads;   // Studio: tải thẳng về máy')
m = m.replace("drawImage(canvas,", "drawImage(renderer.domElement,")
m = re.sub(r"\bcanvas\.width\b", "renderer.domElement.width", m)
m = re.sub(r"\bcanvas\.height\b", "renderer.domElement.height", m)
m = ren_ids(m)
for bad in [r"requestAnimationFrame\(loop", r"new THREE\.WebGLRenderer", r"new THREE\.OrbitControls", r"new THREE\.TransformControls", r'\$\("cv"\)']:
    hit = re.search(bad, m)
    assert not hit, "còn sót: " + m[max(0, hit.start() - 80):hit.start() + 60]

# khối cuối: icon cho nút (IBTN) + playblast; TOUCH bỏ (Studio có chế độ cảm ứng riêng)
tail, _ = between(t, "</script>\n<script>", "</script>", mend)
tail = cut(tail, "/*TOUCH*/", "/*PLAYBLAST*/", "/*PLAYBLAST*/\n") if "/*TOUCH*/" in tail else tail
tail = ren_ids(tail)
tail = re.sub(r"(?<![.\w$])camera\b(?!\s*:)", "CAM()", tail)
tail = tail.replace("drawImage(renderer.domElement,", "drawImage(renderer.domElement,").replace("drawImage(canvas,", "drawImage(renderer.domElement,")

head = """// SINH TỰ ĐỘNG bởi tools/studio/port_pose.py từ work/pose_lab/index.html — đừng sửa tay, sửa port_pose.py rồi chạy lại.
ST.POSE_HTML = %s;
ST.POSE_RENAME = %s;
%s
ST.poseEngine = function (POSES_IN, host) {
const CAM = host.cam;
""" % (json.dumps(html, ensure_ascii=False), json.dumps(RENAME), ldb)
foot = """
return { get: () => ({ P, frame, sel, selSet, B, markers, model, playing, mode }), select: n => select(n), setSelection, setMode, goto, undo: () => $("undo").click(),
  canUndo: () => undoStack.length > 0, openPose, stopPlay, frameAll: typeof frameAll === "function" ? frameAll : null, setCam, NAMES, JOINTS: () => JOINTS };
};
"""
out = head + m + "\n" + tail + foot
open(OUT_JS, "w", encoding="utf8", newline=chr(10)).write(out)
print(len(out) // 1024, "KB ->", OUT_JS, "|", len(pcss) // 1024, "KB css | đổi id:", RENAME)
