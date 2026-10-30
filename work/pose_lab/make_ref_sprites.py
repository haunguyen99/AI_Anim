"""Ref frames -> one JPEG sprite sheet per view for the Pose Lab ref panel.
.venv/Scripts/python.exe work/pose_lab/make_ref_sprites.py <frames_dir> <masks_dir> <out_dir> [height=360]
frames_dir/<view>/fNNN.png (any size), masks_dir/<view>_NNN.npy (bool silhouette, any size) -> out_dir/<view>.jpg +
out_dir/refs.json {views: {view: {file, cols, w, h, frames}}}. Crop = union of the silhouette over all frames + 10 %,
so the character stays the same size and place in every cell (feet line does not jump)."""
import sys, os, json, glob, cv2, numpy as np

fr_dir, mk_dir, out = sys.argv[1:4]
H = int(sys.argv[4]) if len(sys.argv) > 4 else 360
os.makedirs(out, exist_ok=True)
meta = {"views": {}}
for view in sorted(os.listdir(fr_dir)):
    files = sorted(glob.glob(os.path.join(fr_dir, view, "f*.png")))
    if not files: continue
    img0 = cv2.imread(files[0]); ih, iw = img0.shape[:2]
    box = None
    for m in sorted(glob.glob(os.path.join(mk_dir, f"{view}_*.npy"))):
        a = np.load(m); ys, xs = np.nonzero(a)
        if not len(xs): continue
        sx, sy = iw / a.shape[1], ih / a.shape[0]
        b = [xs.min() * sx, ys.min() * sy, (xs.max() + 1) * sx, (ys.max() + 1) * sy]
        box = b if box is None else [min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3])]
    if box is None: box = [0, 0, iw, ih]
    pw, ph = (box[2] - box[0]) * 0.1, (box[3] - box[1]) * 0.1
    x0, y0 = max(0, int(box[0] - pw)), max(0, int(box[1] - ph))
    x1, y1 = min(iw, int(box[2] + pw)), min(ih, int(box[3] + ph))
    W = max(2, round(H * (x1 - x0) / (y1 - y0)))
    cols = min(len(files), max(1, int(4096 // W)))
    rows = -(-len(files) // cols)
    sheet = np.zeros((rows * H, cols * W, 3), np.uint8)
    for i, f in enumerate(files):
        c = cv2.resize(cv2.imread(f)[y0:y1, x0:x1], (W, H), interpolation=cv2.INTER_AREA)
        r, k = divmod(i, cols); sheet[r * H:(r + 1) * H, k * W:(k + 1) * W] = c
    name = f"{view}.jpg"
    cv2.imwrite(os.path.join(out, name), sheet, [cv2.IMWRITE_JPEG_QUALITY, 82])
    meta["views"][view] = {"file": name, "cols": cols, "w": W, "h": H, "frames": len(files), "crop": [x0, y0, x1, y1]}
    print(view, f"crop {x0},{y0}-{x1},{y1} of {iw}x{ih}", f"cell {W}x{H}", f"grid {cols}x{rows}",
          f"{os.path.getsize(os.path.join(out, name)) // 1024} KB")
json.dump(meta, open(os.path.join(out, "refs.json"), "w"), indent=1)
