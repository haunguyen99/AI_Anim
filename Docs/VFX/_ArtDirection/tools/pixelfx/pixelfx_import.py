"""Import pixelfx (https://github.com/patch-gg/pixelfx, MIT) sprite sheets into the Shape Lab library, group "pixelfx".

  python -I pixelfx_import.py <pixelfx_repo>/sheets [--dry-run]

For each effect sheet (<category>/<name>.png + .json from `node tools/sheets.mjs <categories>`):
  1. sample at most 16 frames evenly (loops: evenly over the loop; one-shots: first..last frame)
  2. write a 4xN colour sheet + small JSON (fps, loop, pivot, picked frames) to tools/pixelfx/sheets/<category>/
  3. add it to the Shape Lab library (element "pixelfx", name "<Category> · <Name>") as a tone mask flipbook
Then: python -I ../shape_library/shape_library.py build
Full-frame originals are not kept in the project (156 MB); re-run sheets.mjs to get them.
"""
import argparse
import json
import math
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "shape_library"))
import shape_library as sl  # noqa: E402

MAX_FRAMES = 16
COLS = 4
CAT_NAMES = {"scifi": "Sci-fi", "spawn": "Spawn & death"}


def pick(n, loop):
    if n <= MAX_FRAMES:
        return list(range(n))
    if loop:
        return [round(i * n / MAX_FRAMES) % n for i in range(MAX_FRAMES)]
    return [round(i * (n - 1) / (MAX_FRAMES - 1)) for i in range(MAX_FRAMES)]


def main():
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("sheets")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    meta = sl.load_meta()
    if not any(e["id"] == "pixelfx" for e in meta["elements"]):
        meta["elements"].append({"id": "pixelfx", "name": "PixelFX", "palette": "Impact"})
    known = {s.get("source") for s in meta["shapes"] if s["element"] == "pixelfx"}
    out_root = HERE / "sheets"
    index = []
    for j in sorted(Path(a.sheets).glob("*/*.json")):
        if j.name == "index.json":
            continue
        d = json.loads(j.read_text(encoding="utf-8"))
        px = d["meta"]["pixelfx"]
        frames = d["frames"]
        idx = pick(len(frames), px.get("loop", False))
        fw, fh = px["frameSize"]
        rows = math.ceil(len(idx) / COLS)
        src = Image.open(j.with_suffix(".png")).convert("RGBA")
        sheet = Image.new("RGBA", (fw * COLS, fh * rows), (0, 0, 0, 0))
        for k, f in enumerate(idx):
            r = frames[f]["frame"]
            sheet.paste(src.crop((r["x"], r["y"], r["x"] + r["w"], r["y"] + r["h"])), ((k % COLS) * fw, (k // COLS) * fh))
        cat, name = j.parent.name, j.stem
        fname = f"{cat}-{name}_{COLS}x{rows}.png"
        nice = f"{CAT_NAMES.get(cat, cat.capitalize())} · {px['name']}"
        index.append({"id": px["id"], "name": px["name"], "category": cat, "file": f"sheets/{cat}/{fname}",
                      "fps": px["fps"], "loop": px.get("loop", False), "framesOriginal": len(frames),
                      "picked": idx, "frameSize": [fw, fh], "pivot": px.get("pivot")})
        if a.dry_run:
            print(f"  {nice:40s} {len(frames):3d} -> {len(idx)} frame, {fw}x{fh}")
            continue
        (out_root / cat).mkdir(parents=True, exist_ok=True)
        p = out_root / cat / fname
        sheet.save(p, optimize=True)
        if fname in known:
            print(f"  = đã có: {fname}")
            continue
        sl.make_entry(p, "pixelfx", nice, meta, grid=(COLS, rows))
    if not a.dry_run:
        (HERE / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
        sl.save_meta(meta)
        print(f"{len(index)} effect -> tools/pixelfx/sheets + library group 'pixelfx'")


if __name__ == "__main__":
    main()
