"""Video anim Spine vẽ bằng runtime THẬT trên trang Spine Live (đủ IK, clipping, đổi ảnh slot, inherit), khung cố định.
2026-11-18 (demo mix idle + active Char4). Trang Spine Live phải đang mở (spine_live_cmd.py status).

  python -I tools/spine/live_video.py <json> --anim mix --frames 0-257,0-89 --out demo.mp4 [--cell 540x780] [--fps 30]
        [--bg 1c3a5c] [--no-burn] [--batch 24]

--frames: danh sách / khoảng frame theo thứ tự phát (vd "0-257,0-89" = mix rồi thêm một vòng idle đầu mix).
Bước: chụp thử mọi frame theo lô để lấy khung chung (hợp mọi lô) -> chụp lại từng lô với khung đó, không nhãn -> cắt ô ->
ffmpeg H.264 -> tools/frame_burn.py ghi số frame (đếm từ 1). In đường dẫn video.
"""
import base64, json, os, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import spine_live_cmd as C
from PIL import Image


def opt(a, name, d=None):
    if name in a:
        i = a.index(name); v = a[i + 1]; del a[i:i + 2]; return v
    return d


def frames_of(spec):
    out = []
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-"); out += list(range(int(a), int(b) + 1))
        elif part.strip():
            out.append(int(part))
    return out


def snap(js, anim, frames, cell, cols, box=None, bg=None):
    a = {"json": js, "anim": anim, "frames": frames, "cell": cell, "cols": cols, "nolabel": True}
    if box: a["box"] = box
    if bg: a["bg"] = "#" + bg
    r = C.bridge("snap", a)
    if not r.get("ok"):
        raise SystemExit("lỗi chụp: " + str(r.get("error")))
    return r["result"]


def main():
    a = sys.argv[1:]
    js = a.pop(0)
    anim = opt(a, "--anim", "idle"); out = opt(a, "--out", os.path.join(os.path.dirname(js), "preview", anim + ".mp4"))
    cw, ch = [int(x) for x in opt(a, "--cell", "540x780").split("x")]
    fps = int(opt(a, "--fps", "30")); batch = int(opt(a, "--batch", "24")); bg = opt(a, "--bg")
    burn = "--no-burn" not in a
    seq = frames_of(opt(a, "--frames", "0"))
    uniq = sorted(set(seq))
    cols = 6
    box = None
    for i in range(0, len(uniq), batch):          # khung chung: hợp khung mọi lô
        b = snap(js, anim, uniq[i:i + batch], [60, 90], cols)["box"]
        box = b if box is None else [min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3])]
    tmp = tempfile.mkdtemp(prefix="livevid_")
    img = {}
    for i in range(0, len(uniq), batch):
        fr = uniq[i:i + batch]
        r = snap(js, anim, fr, [cw, ch], cols, box, bg)
        sheet = Image.open(__import__("io").BytesIO(base64.b64decode(r["png"].split(",", 1)[1]))).convert("RGB")
        for k, f in enumerate(fr):
            x, y = (k % cols) * cw, (k // cols) * ch
            img[f] = sheet.crop((x, y, x + cw, y + ch))
        print(f"  chụp {i + len(fr)}/{len(uniq)} frame", flush=True)
    for n, f in enumerate(seq):
        img[f].save(os.path.join(tmp, f"f_{n + 1:05d}.png"))
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    raw = out if not burn else out[:-4] + "_raw.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", os.path.join(tmp, "f_%05d.png"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2", raw], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    if burn:
        subprocess.run([sys.executable, "-I", os.path.join(ROOT, "tools", "frame_burn.py"), raw, out, "--fps", str(fps)], check=True)
        os.remove(raw)
    print(json.dumps({"video": os.path.abspath(out), "frames": len(seq), "fps": fps, "box": box}, ensure_ascii=False))


if __name__ == "__main__":
    main()
