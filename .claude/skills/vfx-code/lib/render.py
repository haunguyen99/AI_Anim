"""Render một effect vfx-code ra flipbook Unity + preview + kiểm tra.

  python -I render.py <effect.py> --out <dir> [--frames 16] [--cols 4] [--res 2] [--opts '{"seed":3}'] [--gif] [--check]
  python -I render.py <effect.py> --project <unity_project> --effect <Tên> [--gif] [--check] [--review]

Chế độ --effect (xuất đúng chỗ Review Lab đọc):
  Assets/VFX/<Tên>/Textures/   T_<name>_<grid>.png (+ _Body_/_Light_) + <name>.json   → trình phát flipbook
  Docs/VFX/<Tên>/              Preview_sheet.png (1 hàng, mỗi frame một ô) + BuildReport.txt   → timeline
                               <name>_preview.png, <name>.gif                                 → ảnh / GIF
  --review  dựng lại Review Lab (build_review.py, cả trang) sau khi render.

Xuất:
  blend "add":   T_<name>_<grid>.png                      một sheet Additive
  blend "alpha": T_<name>_Body_<grid>.png + T_<name>_Light_<grid>.png  (Alpha Blended + Additive)
  <name>.json    duration, loop, fps, thời điểm frame, pivot, space → builder Unity (assets/VfxCodeBuild.cs)
Frame chia đều theo duration → Unity: Frame over Time 0 → 1 TUYẾN TÍNH, Start Lifetime = duration.
"""
import argparse
import importlib.util
import json
import math
import os
import subprocess
import sys
import time

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import core as cf  # noqa: E402

REVIEW_LAB = os.path.join(os.path.dirname(os.path.dirname(HERE)), "vfx-maker", "review-lab", "build_review.py")


def load(path):
    spec = importlib.util.spec_from_file_location("fx_" + os.path.splitext(os.path.basename(path))[0], path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def png(arr, path):
    a = (np.clip(arr, 0, 1) * 255 + 0.5).astype(np.uint8)
    Image.fromarray(a, "RGBA" if a.shape[2] == 4 else "RGB").save(path, optimize=True)


def main():
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("effect")
    ap.add_argument("--out", help="thư mục xuất (chế độ thường)")
    ap.add_argument("--project", help="project Unity (chế độ --effect)")
    ap.add_argument("--effect", dest="effect_name", help="tên effect: xuất vào Assets/VFX/<Tên>/Textures + Docs/VFX/<Tên>/")
    ap.add_argument("--review", action="store_true", help="dựng Review Lab cho effect sau khi render (cần --effect)")
    ap.add_argument("--frames", type=int, default=16)
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--res", type=float, default=2.0)
    ap.add_argument("--opts", default="{}")
    ap.add_argument("--opts-file", help="file JSON chứa options (tránh lỗi trích dẫn shell)")
    ap.add_argument("--gif", action="store_true")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if not a.out and not a.effect_name:
        ap.error("cần --out <dir> hoặc --effect <Tên> (kèm --project)")

    mod = load(a.effect)
    M = mod.META
    sp_issues = cf.check_space(M)
    if sp_issues:
        print("CHƯA ĐỦ THÔNG TIN KHÔNG GIAN — hỏi người dùng trước khi làm tiếp:\n  - " + "\n  - ".join(sp_issues))
        sys.exit(2)
    opts = json.loads(open(a.opts_file, encoding="utf-8").read()) if a.opts_file else json.loads(a.opts)

    if a.effect_name:
        proj = os.path.abspath(a.project or os.getcwd())
        tex_dir = os.path.join(proj, "Assets", "VFX", a.effect_name, "Textures")
        doc_dir = os.path.join(proj, "Docs", "VFX", a.effect_name)
    else:
        tex_dir = doc_dir = a.out
    os.makedirs(tex_dir, exist_ok=True)
    os.makedirs(doc_dir, exist_ok=True)

    name = M["name"]
    rows = int(math.ceil(a.frames / a.cols))
    grid = f"{a.cols}x{rows}"
    times = cf.sample_times(M, a.frames)
    frames = cf.render(mod, opts, times, a.res)

    sheets = []
    if M["blend"] == "add":
        sheets.append(f"T_{name}_{grid}.png")
        png(cf.sheet([cf.to_add_rgba(f) for f in frames], a.cols), os.path.join(tex_dir, sheets[-1]))
    else:
        sheets.append(f"T_{name}_Body_{grid}.png")
        png(cf.sheet([cf.to_alpha_rgba(f) for f in frames], a.cols), os.path.join(tex_dir, sheets[-1]))
        if any(f.light.max() > 0.01 for f in frames):
            sheets.append(f"T_{name}_Light_{grid}.png")
            png(cf.sheet([cf.to_light_rgba(f) for f in frames], a.cols), os.path.join(tex_dir, sheets[-1]))

    comp = [cf.composite(f) for f in frames]
    prev = cf.sheet(comp, a.cols)
    im = Image.fromarray((prev * 255).astype(np.uint8), "RGB")
    dr = ImageDraw.Draw(im)
    W, H = frames[0].W, frames[0].H
    for i, t in enumerate(times):
        r, c = divmod(i, a.cols)
        dr.text((c * W + 4, r * H + 3), f"{i} · {t:.3f}s", fill=(150, 150, 160))
        ox, oy = M["origin"]
        px, py = c * W + ox * a.res, r * H + oy * a.res
        dr.line([(px - 3, py), (px + 3, py)], fill=(200, 40, 40))
        dr.line([(px, py - 3), (px, py + 3)], fill=(200, 40, 40))
    im.save(os.path.join(doc_dir, f"{name}_preview.png"))

    if a.effect_name:   # timeline của Review Lab: 1 hàng, số frame = rộng / cao, thời điểm đọc từ BuildReport
        png(np.hstack(comp), os.path.join(doc_dir, "Preview_sheet.png"))

    if a.gif:
        fps = M.get("fps", 30)
        n = int(round(M["duration"] * fps)) + (0 if M.get("loop") else 6)
        ts = [i / fps for i in range(n)]
        fr = cf.render(mod, opts, ts, a.res)
        ims = [Image.fromarray((cf.composite(f) * 255).astype(np.uint8), "RGB") for f in fr]
        ims = ims * (2 if M.get("loop") else 1)
        ims[0].save(os.path.join(doc_dir, f"{name}.gif"), save_all=True, append_images=ims[1:], duration=int(1000 / fps), loop=0)

    info = dict(source=os.path.abspath(a.effect).replace("\\", "/"), name=name, blend=M["blend"], duration=M["duration"],
                loop=M.get("loop", False), fps=M.get("fps", 30), frames=a.frames, cols=a.cols, rows=rows,
                times=[round(t, 4) for t in times], size=M["size"], res=a.res, space=M["space"],
                pivot=[M["origin"][0] / M["size"][0], M["origin"][1] / M["size"][1]], sheets=sheets,
                options={**M.get("options", {}), **opts})
    with open(os.path.join(tex_dir, f"{name}.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=1, default=str)
    print(f"{name}: {a.frames} frame {grid}, {W}x{H}/ô, blend {M['blend']} -> {tex_dir}")

    issues = cf.check(mod, opts) if a.check else None
    if a.check:
        print("check: sạch" if not issues else "check:\n  - " + "\n  - ".join(issues))

    if a.effect_name:
        sp = M["space"]
        rep = [f"Built: {time.strftime('%Y-%m-%d %H:%M')} (vfx-code, code render — chưa dựng trong Unity)",
               f"Source: {info['source']}",
               f"Preview times (s): {', '.join(f'{t:.3f}' for t in times)}",
               f"Blend: {M['blend']} · duration {M['duration']:.3f}s · loop {M.get('loop', False)} · {a.frames} frame {grid} · {W}x{H}/ô",
               f"Space: {sp.get('context')} · {sp.get('plane')} · camera {sp.get('camera')} · {sp.get('width_m')} m · neo {sp.get('anchor')} · nền {sp.get('background')}",
               f"Sheets: {', '.join(sheets)}",
               "Check: " + ("chưa chạy" if issues is None else "sạch" if not issues else "; ".join(issues))]
        with open(os.path.join(doc_dir, "BuildReport.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(rep) + "\n")

    if a.review:
        if not a.effect_name:
            print("--review cần --effect")
        elif not os.path.isfile(REVIEW_LAB):
            print(f"Không thấy Review Lab ở {REVIEW_LAB}")
        else:
            sys.stdout.flush()
            # dựng lại CẢ trang: build_review --effect sẽ ghi đè index.html chỉ còn 1 effect
            subprocess.run([sys.executable, "-I", REVIEW_LAB, "--project", proj], check=False)

    if issues:
        sys.exit(1)


if __name__ == "__main__":
    main()
