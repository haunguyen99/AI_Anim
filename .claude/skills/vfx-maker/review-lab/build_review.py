#!/usr/bin/env python3
"""VFX Review Lab builder.

Quét Docs/VFX/<Effect>/ (Plan.md, BuildReport.txt, Preview_sheet.png, ảnh/GIF) và
Assets/VFX/<Effect>/Textures (+ Prefabs) rồi gói thành MỘT file HTML tự chứa để review
mà không cần mở Unity.

  python -I build_review.py                       # tất cả effect, ghi Docs/VFX/_Review/index.html
  python -I build_review.py --effect Explosion    # chỉ vài effect (lặp lại --effect)
  python -I build_review.py --link                # không nhúng ảnh, chỉ trỏ đường dẫn tương đối (file nhỏ, cần giữ nguyên thư mục)
  python -I build_review.py --project D:/Game_prj/VFX_LIb --out some/dir/index.html
"""
import argparse, base64, json, mimetypes, os, re, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_EXT = {".png", ".gif", ".jpg", ".jpeg", ".webp"}
SKIP_DIRS = {"_archive", "_Review", "_ArtDirection"}


def rd(path):
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            return f.read()
    except OSError:
        return ""


def rel_url(path, out_dir):
    return os.path.relpath(path, out_dir).replace("\\", "/")


def src_of(path, out_dir, link, max_bytes):
    if link:
        return rel_url(path, out_dir)
    if os.path.getsize(path) > max_bytes:
        print(f"  ! bỏ qua (quá {max_bytes // 1048576}MB, dùng --max-mb hoặc --link): {path}")
        return None
    mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode("ascii")


def parse_report(text):
    times, layers = [], []
    for line in text.splitlines():
        m = re.match(r"\s*Preview times.*?:\s*(.+)", line)
        if m:
            times = [float(x) for x in re.findall(r"[\d.]+", m.group(1))]
        m = re.match(r"\s{2}(\S+)\s+max=(\d+)\s+life=([\d.]+)\s+mode=(\S+)\s+mat=(\S+)\s*(?:\((.*)\))?", line)
        if m:
            layers.append(dict(name=m.group(1).split("/")[-1], max=int(m.group(2)), life=float(m.group(3)),
                               mode=m.group(4), mat=m.group(5), shader=m.group(6) or ""))
    return times, layers


def built_at(report):
    m = re.search(r"^Built:\s*(.+)$", report or "", re.M)
    return m.group(1).strip() if m else ""


def grid_of(name):
    m = re.search(r"[_ ](\d+)x(\d+)(?=[_.\s]|$)", name)
    return (int(m.group(1)), int(m.group(2))) if m else None


def image_size(path):
    try:
        from PIL import Image
        with Image.open(path) as im:
            return im.size
    except Exception:
        return None


def build_effect(name, docs, assets, out_dir, link, max_bytes):
    print(f"- {name}")
    e = dict(name=name, plan=rd(os.path.join(docs, "Plan.md")), report=rd(os.path.join(docs, "BuildReport.txt")),
             timeline=None, times=[], layers=[], media=[], textures=[], prefabs=[], materials=0)
    e["times"], e["layers"] = parse_report(e["report"])

    seen = set()
    sheet = os.path.join(docs, "Preview_sheet.png")
    if os.path.isfile(sheet):
        s = src_of(sheet, out_dir, link, max_bytes)
        sz = image_size(sheet)
        n = len(e["times"]) or (round(sz[0] / sz[1]) if sz else 1)
        e["timeline"] = dict(src=s, frames=n)
        if not e["times"]:
            e["times"] = [round(i, 2) for i in range(n)]
        seen.add(os.path.abspath(sheet))

    for root, dirs, files in os.walk(docs):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in sorted(files):
            p = os.path.join(root, fn)
            ext = os.path.splitext(fn)[1].lower()
            if ext not in IMG_EXT or os.path.abspath(p) in seen:
                continue
            s = src_of(p, out_dir, link, max_bytes)
            if s:
                sub = os.path.relpath(root, docs).replace("\\", "/")
                e["media"].append(dict(name=fn if sub == "." else f"{sub}/{fn}", src=s, gif=ext == ".gif"))

    tex = os.path.join(assets, "Textures")
    if os.path.isdir(tex):
        for fn in sorted(os.listdir(tex)):
            if os.path.splitext(fn)[1].lower() not in IMG_EXT:
                continue
            p = os.path.join(tex, fn)
            s = src_of(p, out_dir, link, max_bytes)
            if not s:
                continue
            g = grid_of(fn)
            e["textures"].append(dict(name=fn, src=s, cols=g[0] if g else 1, rows=g[1] if g else 1, size=image_size(p)))
    # flipbook bake nằm trong Docs (ví dụ Puff3D_sheet.png) không có lưới trong tên → vẫn ở mục ảnh.

    pf = os.path.join(assets, "Prefabs")
    if os.path.isdir(pf):
        e["prefabs"] = [f for f in sorted(os.listdir(pf)) if f.endswith(".prefab")]
    mats = os.path.join(assets, "Materials")
    if os.path.isdir(mats):
        e["materials"] = len([f for f in os.listdir(mats) if f.endswith(".mat")])
    print(f"    timeline={'có' if e['timeline'] else 'không'} · ảnh/GIF={len(e['media'])} · texture={len(e['textures'])} · layer={len(e['layers'])}")
    return e


def main():
    for s in (sys.stdout, sys.stderr):
        try: s.reconfigure(encoding="utf-8", errors="replace")
        except Exception: pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=os.getcwd())
    ap.add_argument("--effect", action="append", help="tên effect (thư mục trong Docs/VFX); bỏ trống = tất cả")
    ap.add_argument("--out", help="mặc định <project>/Docs/VFX/_Review/index.html")
    ap.add_argument("--link", action="store_true", help="không nhúng ảnh, dùng đường dẫn tương đối")
    ap.add_argument("--max-mb", type=float, default=8.0)
    a = ap.parse_args()

    proj = os.path.abspath(a.project)
    docs_root = os.path.join(proj, "Docs", "VFX")
    if not os.path.isdir(docs_root):
        sys.exit(f"Không thấy {docs_root}")
    out = os.path.abspath(a.out or os.path.join(docs_root, "_Review", "index.html"))
    out_dir = os.path.dirname(out)
    os.makedirs(out_dir, exist_ok=True)

    names = a.effect or sorted(d for d in os.listdir(docs_root)
                               if os.path.isdir(os.path.join(docs_root, d)) and d not in SKIP_DIRS and not d.startswith("_"))
    effects = []
    # Thành phần chuẩn hoá: Docs/VFX/_Components/<Nhóm>/<ID>/ ↔ Assets/VFX/_Components/<Nhóm>/
    comp_root = os.path.join(docs_root, "_Components")
    if not a.effect and os.path.isdir(comp_root):
        groups = []
        for g in sorted(os.listdir(comp_root)):
            gd = os.path.join(comp_root, g)
            if not os.path.isdir(gd):
                continue
            items = []
            for cid in sorted(os.listdir(gd)):
                cd = os.path.join(gd, cid)
                if os.path.isdir(cd):
                    e = build_effect(cid, cd, os.path.join(proj, "Assets", "VFX", "_Components", g), out_dir, a.link, int(a.max_mb * 1048576))
                    e["group"] = "Thành phần · " + g
                    items.append(e)
            if items:
                groups.append((max(built_at(e["report"]) for e in items), items))
        # nhóm thành phần mới build nhất lên đầu → trang mở ra là thấy ngay
        for _, items in sorted(groups, key=lambda x: x[0], reverse=True):
            effects.extend(items)
    for n in names:
        d = os.path.join(docs_root, n)
        if not os.path.isdir(d):
            print(f"! không có Docs/VFX/{n}")
            continue
        e = build_effect(n, d, os.path.join(proj, "Assets", "VFX", n), out_dir, a.link, int(a.max_mb * 1048576))
        e["group"] = "Effect"
        effects.append(e)

    data = dict(project=os.path.basename(proj), generated=time.strftime("%Y-%m-%d %H:%M"), link=a.link, effects=effects)
    tpl = rd(os.path.join(HERE, "review_lab.html"))
    if "/*__DATA__*/" not in tpl:
        sys.exit("review_lab.html thiếu chỗ chèn dữ liệu")
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    with open(out, "w", encoding="utf-8") as f:
        f.write(tpl.replace("/*__DATA__*/null", blob))
    print(f"\nĐã ghi {out} ({os.path.getsize(out) / 1048576:.1f} MB, {len(effects)} effect)")


if __name__ == "__main__":
    main()
