"""Phan loai texture VFX vao Assets/Library/<nhom>. Dry-run mac dinh; --apply de chep."""
import csv, hashlib, os, re, shutil, sys, uuid

RPG = r"D:/Projects/rpg-game/Assets"
PRJ = r"D:/Game_prj/VFX_LIb/Assets"
DST = PRJ + "/Library"
OUT = os.path.dirname(os.path.abspath(__file__))
EXT = {".png", ".tga", ".psd", ".jpg", ".jpeg", ".exr", ".tif", ".tiff"}

RPG_SRC = ["RPG_VFX", "2D_Art/Vfx", "EffectCore", "_Game/Resources_moved/Textures"]
PRJ_SKIP = ["Library", "Scenes", "_Game"]

# Goi y theo ten thu muc (uu tien cao nhat)
FOLDER = [
    (r"/decals?(/|$)", "decals"),
    (r"/scorch(/|$)", "decals"),
    (r"/(electric|lightning)s?(/|$)", "Lightnings_Electrics"),
    (r"/glow(/|$)", "glow"),
    (r"/sparks?(/|$)", "glow"),
    (r"/impact(/|$)", "impact"),
    (r"/noise(/|$)", "noise"),
    (r"/(slash|slashes)(/|$)", "Slash"),
    (r"/(smoke|dust)(/|$)", "smoke"),
    (r"/trails?(/|$)", "trail"),
    (r"/(shader_)?water(/|$)", "water"),
    (r"/(waves?|ring)(/|$)", "wave"),
]
# Lua: khong co thu muc rieng -> de chua xep (tru khi ten ro la nhom khac)
FIRE = r"fire|flame|magma|lava|torch"
FIRE_KEEP = r"slash|impact|explo|bomb|ring|noise|spark|ember"
# Goi y theo ten file (theo thu tu)
NAME = [
    (r"blood", "impact"),
    (r"lightning|electric|thunder|^ln$|(?<![a-z])arcs?(?![a-z])|bolt|zap|tesla", "Lightnings_Electrics"),
    (r"slash|sword|katana|melee|blade", "Slash"),
    (r"trail|beam|(?<![gt])ray|thrust|javelin|silk|chargepath|stretch|(?<!out)(?<!sp)line", "trail"),
    (r"decal|crack|break|ruin|symbol|magic_?circle|indicator|redzone|scorch", "decals"),
    (r"smoke|cloud|dust|fog|mist", "smoke"),
    (r"water|splash|liquid|bubble|caustic|droplet|(?<![a-z])rain(?!bow)|foam", "water"),
    (r"wave|ring|shock|ripple|vortex|wind", "wave"),
    (r"noise|perlin|dissolve|disolve|distort|voronoi|cellular", "noise"),
    (r"impact|(?<!w)hit|burst|explo|boom|bomb|punch|bite|radial|flash|muzzle", "impact"),
    (r"glow|flare|light|(?<![a-z])dot|point(?!er)|star|spark|ember|twinkle|halo|lens|blink|circle|ball", "glow"),
    (r"(?<!back)ground", "decals"),
]

def classify(rel):
    low = "/" + rel.replace("\\", "/").lower()
    folder = os.path.dirname(low)
    for pat, cat in FOLDER:
        if re.search(pat, folder):
            return cat, "thu muc"
    name = os.path.splitext(os.path.basename(low))[0]
    if re.search(FIRE, name) and not re.search(FIRE_KEEP, name):
        return "", ""
    for pat, cat in NAME:
        if re.search(pat, name):
            return cat, "ten file"
    return "", ""

def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

def walk(root, subs=None, skip=()):
    bases = [os.path.join(root, s) for s in subs] if subs else [root]
    for b in bases:
        for dp, dn, fn in os.walk(b):
            rel_dp = os.path.relpath(dp, root).replace("\\", "/")
            if rel_dp.split("/")[0] in skip:
                dn[:] = []
                continue
            for f in fn:
                if os.path.splitext(f)[1].lower() in EXT:
                    yield os.path.join(dp, f), os.path.relpath(os.path.join(dp, f), root)

def main(apply):
    rows, seen, used = [], {}, set()
    srcs = [("rpg", p, r) for p, r in walk(RPG, RPG_SRC)] + \
           [("prj", p, r) for p, r in walk(PRJ, skip=PRJ_SKIP)]
    for origin, path, rel in srcs:
        cat, why = classify(rel)
        h = md5(path)
        if h in seen:
            rows.append([origin, rel, cat, why, "trung", seen[h]]); continue
        if not cat:
            rows.append([origin, rel, "", "", "chua_xep", ""]); continue
        base, ext = os.path.splitext(os.path.basename(path))
        name, i = base + ext, 1
        while (cat, name.lower()) in used:
            i += 1; name = f"{base}_{i}{ext}"
        used.add((cat, name.lower()))
        dst = f"{DST}/{cat}/{name}"
        seen[h] = f"{cat}/{name}"
        rows.append([origin, rel, cat, why, "chep", f"{cat}/{name}"])
        if apply:
            shutil.copy2(path, dst)
            meta = path + ".meta"
            if os.path.exists(meta):
                txt = open(meta, encoding="utf-8", errors="replace").read()
                txt = re.sub(r"^guid: [0-9a-f]{32}", "guid: " + uuid.uuid4().hex, txt, count=1, flags=re.M)
                open(dst + ".meta", "w", encoding="utf-8", newline="\n").write(txt)
    with open(os.path.join(OUT, "classify.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(["nguon", "duong_dan", "nhom", "ly_do", "hanh_dong", "dich"]); w.writerows(rows)
    from collections import Counter
    print(Counter(r[4] for r in rows))
    print(Counter(r[2] for r in rows if r[4] == "chep"))

if __name__ == "__main__":
    main("--apply" in sys.argv)
