"""So pose Studio với một ô của bảng ref `keys/ref_sheet_v2.png`: chụp viewport ở đúng góc của ô rồi ghép cạnh nhau.

    .venv/Scripts/python.exe -I -X utf8 work/infinite_defense/ninja_idle/cmp_ref.py out.png front side 34 [--cid ID]
Ô: front | left | back | right | 34 | game. Góc camera Studio (az độ quanh trục đứng từ +Z sang +X = bên trái nhân vật, el độ ngẩng).
"""
import base64, io, os, sys, time
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import studio_cmd as SC

SHEET = os.path.join(ROOT, "work", "infinite_defense", "ninja_idle", "keys", "ref_sheet_v2.png")
BOX = {"front": (3, 3, 556, 420), "left": (559, 3, 1113, 420), "back": (1117, 3, 1669, 420),
       "right": (3, 466, 556, 880), "34": (559, 466, 1113, 880), "game": (1117, 466, 1669, 880)}
CAM = {"front": (0, 4), "left": (90, 4), "back": (180, 4), "right": (-90, 4), "34": (40, 14), "game": (-140, 40)}


def snap(az, el, d, size=800):
    SC.call("view", {"layout": "1", "cam": "persp", "frame": "all"})
    SC.call("view", {"az": az, "el": el, "d": d})
    time.sleep(0.8)   # đợi khung hình dùng góc camera mới (snap đầu có thể trễ một khung)
    SC.call("snap", {"w": size, "h": size}); time.sleep(0.2)
    r = SC.call("snap", {"w": size, "h": size})["result"]
    im = Image.open(io.BytesIO(base64.b64decode(r["png"]))).convert("RGB")
    return im


def main():
    a = sys.argv[1:]
    if "--cid" in a:
        i = a.index("--cid"); SC.CID = a[i + 1]; del a[i:i + 2]
    out, names = a[0], a[1:]
    sheet = Image.open(SHEET).convert("RGB")
    SC.call("anim", {"do": "select", "names": []})   # bỏ chọn khớp: không vẽ gizmo vào ảnh
    rows = []
    for n in names:
        ref = sheet.crop(BOX[n]); ref = ref.resize((round(ref.width * 600 / ref.height), 600), Image.LANCZOS)
        az, el = CAM[n]
        me = snap(az, el, 5.0).resize((600, 600), Image.LANCZOS)
        row = Image.new("RGB", (ref.width + 600, 600)); row.paste(ref, (0, 0)); row.paste(me, (ref.width, 0)); rows.append(row)
    W = max(r.width for r in rows); sheet_out = Image.new("RGB", (W, 600 * len(rows)))
    for i, r in enumerate(rows): sheet_out.paste(r, (0, 600 * i))
    sheet_out.save(out); print(out)


if __name__ == "__main__":
    main()
