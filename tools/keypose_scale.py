"""Đo tỉ lệ dài vũ khí / chiều cao nhân vật trên ảnh key pose (Codex), để bắt ảnh vẽ vũ khí sai kích thước.
Ảnh nền trơn, nhìn ngang. Vũ khí = điểm ảnh màu gỗ nâu đỏ sẫm (G/R thấp) trên dải ngang có nhiều gỗ nhất; người = mọi điểm khác
nền. Lấy đoạn liền dài nhất (bỏ mũi tên/đạn bay tách rời; khe ≤ 8% chiều cao vẫn tính là liền vì đai sắt không phải màu gỗ).
Mốc chuẩn: đo chính script này trên ảnh render model thật CÙNG TỈ LỆ (tools/render_fbx_tex.py, vd sdr03/model_ref/scale_side.png).

    .venv/Scripts/python.exe -I tools/keypose_scale.py ảnh1.png ảnh2.png ... [--ref render_cùng_tỉ_lệ.png] [--target 0.47] [--tol 0.08]
Từ work/shoot_die_repeat/sdr03/keys/measure_scale.py (2026-10-28: Codex vẽ nỏ to ~1,5 lần, user "sai tỉ lệ giữ vũ khí và nhân vật")."""
import sys, argparse
import numpy as np
from PIL import Image
sys.stdout.reconfigure(encoding="utf-8")


def measure(p):
    a = np.asarray(Image.open(p).convert("RGB"), float)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    bg = np.median(a[:8].reshape(-1, 3), axis=0)
    fg = np.abs(a - bg).sum(-1) > 40
    wood = (r > 60) & (r < 190) & (g / np.maximum(r, 1) < 0.52) & (b / np.maximum(r, 1) < 0.45) & fg
    rows = np.where(fg.any(1))[0]
    H = rows.max() - rows.min()
    cnt = wood.sum(1); c = int(cnt.argmax()); band = slice(max(0, c - int(0.06 * H)), c + int(0.06 * H))
    cols = np.where(wood[band].any(0))[0]
    L = 0
    if len(cols):
        gap = max(8, int(0.08 * H)); s = cols[0]
        for x, y in zip(cols, np.r_[cols[1:], 10 ** 9]):
            if y - x > gap: L = max(L, x - s); s = y
    return H, L, L / H if H else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("images", nargs="+"); ap.add_argument("--ref")
    ap.add_argument("--target", type=float); ap.add_argument("--tol", type=float, default=0.08)   # ảnh đã duyệt 0,51–0,54 trên mốc 0,47; ảnh sai 0,68
    a = ap.parse_args()
    target = a.target
    if a.ref:
        _, _, target = measure(a.ref); print("mốc (render model): %.2f" % target)
    for p in a.images:
        H, L, k = measure(p)
        verdict = "" if target is None else ("đúng" if abs(k - target) < a.tol else "SAI " + ("to" if k > target else "nhỏ"))
        print("%-32s cao %4d px  vũ khí %4d px  tỉ lệ %.2f  %s" % (p.replace("\\", "/").split("/")[-1], H, L, k, verdict))
