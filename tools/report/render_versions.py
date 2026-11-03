"""Dựng video tiến độ cho /skillreport từ các phiên bản Spine Live đã lưu (runtime Spine thật, qua cầu nối snap).

  python tools/report/render_versions.py <spec.json> [--only 03_idle_v13,07_active_v23] [--compare]

Cần: Home đang chạy và một trang Spine Live đang mở (lệnh snap đi qua trang đó). Kiểm: tools/spine_live_cmd.py status.

spec.json (ghi trong thư mục báo cáo, vd work/test/spine/X/_review/spec.json):
{
  "json": "work/test/spine/X/x.json",          # file skeleton làm việc (khoá sổ phiên bản)
  "out": "work/test/spine/X/_review",          # thư mục báo cáo: vNN.json, images/, frames/, v/*.mp4 + *.jpg
  "idle_anim": "idle",                          # anim nền khi phát active (idle cuối → active → idle đầu)
  "cell": [360, 420], "fps": 30,
  "items": [                                    # mỗi mốc thay đổi lớn = 1 video
    {"name": "01_rig", "v": 5, "kind": "rig", "anim": "rig_test", "title": "Rig: PSD mới"},
    {"name": "02_idle_v07", "v": 7, "kind": "idle", "title": "Idle lượt 1", "loops": 3},
    {"name": "07_active_v23", "v": 23, "kind": "active", "title": "Active v1"},
    {"name": "11_mix", "v": 81, "kind": "play", "anim": "mix", "title": "Mix"}
  ],
  "compare": [{"name": "compare_idle", "items": ["02_idle_v07", "06_idle_v20"], "cols": 5}]
}
kind: rig / play = phát anim 2 vòng; idle = phát `loops` vòng (mặc định 3); active = 30F cuối idle → active → 60F đầu idle.
Số frame tự đọc từ độ dài anim trong file phiên bản (ghi "frames" để ép).
Ra: <out>/v/<name>.mp4 (H.264, faststart) + <out>/v/<name>.jpg (poster ở giữa video) — dùng thẳng cho trang báo cáo và slide.
"""
import argparse, glob, json, math, os, shutil, subprocess, sys

from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
PY = sys.executable


def ffmpeg():
    p = shutil.which("ffmpeg")
    if p:
        return p
    g = glob.glob(os.path.expandvars(r"%LOCALAPPDATA%/Microsoft/WinGet/Packages/Gyan.FFmpeg*/*/bin/ffmpeg.exe"))
    if g:
        return g[0]
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        sys.exit("không thấy ffmpeg (winget install Gyan.FFmpeg)")


def anim_frames(js, anim, fps):
    a = json.load(open(js, encoding="utf-8"))["animations"].get(anim)
    if a is None:
        sys.exit(f"{js}: không có anim {anim}")
    tmax = 0.0

    def walk(x):
        nonlocal tmax
        if isinstance(x, dict):
            if isinstance(x.get("time"), (int, float)):
                tmax = max(tmax, x["time"])
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(a)
    return max(1, int(round(tmax * fps)))


class R:
    def __init__(s, spec):
        s.sp = spec
        s.out = os.path.join(ROOT, spec["out"])
        s.cw, s.ch = spec.get("cell", [360, 420])
        s.fps = spec.get("fps", 30)
        s.ff = ffmpeg()
        s.font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 18)
        os.makedirs(os.path.join(s.out, "v"), exist_ok=True)
        os.makedirs(os.path.join(s.out, "frames"), exist_ok=True)
        js = spec["json"].replace("\\", "/")
        s.store = os.path.join(ROOT, "work", "store", "_sys", "spine_live", "versions", js.replace("/", "__"))
        img = os.path.join(ROOT, os.path.dirname(js), "images")
        if os.path.isdir(img) and not os.path.isdir(os.path.join(s.out, "images")):
            shutil.copytree(img, os.path.join(s.out, "images"))   # snap tìm ảnh ở <thư mục json>/images

    def version(s, v):
        dst = os.path.join(s.out, f"v{v:02d}.json")
        if not os.path.isfile(dst):
            src = os.path.join(s.store, f"v{v:04d}.json")
            if not os.path.isfile(src):
                sys.exit(f"không có phiên bản #{v}: {src}")
            shutil.copy(src, dst)
        return dst

    def render(s, v, anim, title, n=None):
        js = s.version(v)
        n = n or anim_frames(js, anim, s.fps)
        fd = os.path.join(s.out, "frames", f"v{v:02d}_{anim}")
        if os.path.isdir(fd) and len(os.listdir(fd)) == n + 1:
            return fd, n
        cols = 13
        sheet = fd + "_sheet.png"
        rel = os.path.relpath(js, ROOT).replace("\\", "/")
        r = subprocess.run([PY, "-I", os.path.join(ROOT, "tools", "spine_live_cmd.py"), "snap", rel, "--anim", anim,
                            "--frames", ",".join(map(str, range(n + 1))), "--cell", f"{s.cw}x{s.ch}", "--cols", str(cols),
                            "--out", sheet], capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
        if r.returncode or not os.path.isfile(sheet):
            sys.exit(f"snap lỗi ({rel} {anim}): {r.stdout} {r.stderr}\nKiểm Home + trang Spine Live: tools/spine_live_cmd.py status")
        im = Image.open(sheet).convert("RGB")
        shutil.rmtree(fd, ignore_errors=True); os.makedirs(fd)
        for i in range(n + 1):
            x, y = (i % cols) * s.cw, (i // cols) * s.ch
            out = Image.new("RGB", (s.cw, s.ch + 30), (12, 20, 34))
            out.paste(im.crop((x, y, x + s.cw, y + s.ch)), (0, 30))
            ImageDraw.Draw(out).text((8, 6), f"{title} · F{i}", fill=(255, 220, 90), font=s.font)
            out.save(os.path.join(fd, f"{i:03d}.png"))
        return fd, n

    def encode(s, seq, name):
        lst = os.path.join(s.out, "frames", "_seq")
        shutil.rmtree(lst, ignore_errors=True); os.makedirs(lst)
        k = 0
        for fd, rng in seq:
            for i in rng:
                shutil.copy(os.path.join(fd, f"{i:03d}.png"), os.path.join(lst, f"{k:04d}.png")); k += 1
        mp4 = os.path.join(s.out, "v", name + ".mp4")
        subprocess.run([s.ff, "-y", "-loglevel", "error", "-framerate", str(s.fps), "-i", os.path.join(lst, "%04d.png"),
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "21", "-movflags", "+faststart", mp4], check=True)
        shutil.copy(os.path.join(lst, f"{k // 2:04d}.png"), os.path.join(s.out, "frames", "_poster.png"))
        Image.open(os.path.join(s.out, "frames", "_poster.png")).convert("RGB").save(
            os.path.join(s.out, "v", name + ".jpg"), quality=88)
        print(f"{mp4}  {os.path.getsize(mp4) // 1024} KB  {k} frame")

    def item(s, it):
        kind, t = it["kind"], it["title"]
        if kind == "active":
            ia = s.sp.get("idle_anim", "idle")
            fi, ni = s.render(it["v"], ia, t + " · idle")
            fa, na = s.render(it["v"], it.get("anim", "active"), t, it.get("frames"))
            tail = min(30, ni)
            s.encode([(fi, range(ni - tail, ni)), (fa, range(na)), (fi, range(0, min(60, ni)))], it["name"])
        else:
            anim = it.get("anim") or ("idle" if kind == "idle" else "rig_test")
            fd, n = s.render(it["v"], anim, t, it.get("frames"))
            loops = it.get("loops", 3 if kind == "idle" else 2)
            s.encode([(fd, range(n))] * loops, it["name"])

    def compare(s, c):
        vids = [os.path.join(s.out, "v", n + ".mp4") for n in c["items"]]
        cols = c.get("cols", len(vids))
        rows = math.ceil(len(vids) / cols)
        args, filt, row_labels = [], "", []
        for v in vids:
            args += ["-i", v]
        for r in range(rows):
            ids = list(range(r * cols, min(len(vids), (r + 1) * cols)))
            while len(ids) < cols:   # hàng cuối thiếu: lặp video cuối cho đủ cột
                ids.append(ids[-1])
            filt += "".join(f"[{i}:v]" for i in ids) + f"hstack=inputs={cols}[r{r}];"
            row_labels.append(f"[r{r}]")
        filt += ("".join(row_labels) + f"vstack=inputs={rows}[o]") if rows > 1 else ""
        out = os.path.join(s.out, "v", c["name"] + ".mp4")
        m = ["-map", "[o]"] if rows > 1 else ["-map", "[r0]"]
        subprocess.run([s.ff, "-y", "-loglevel", "error", *args, "-filter_complex", filt.rstrip(";"), *m, "-shortest",
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "22", "-movflags", "+faststart", out], check=True)
        print(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec"); ap.add_argument("--only"); ap.add_argument("--compare", action="store_true")
    a = ap.parse_args()
    spec = json.load(open(a.spec, encoding="utf-8"))
    r = R(spec)
    only = set(a.only.split(",")) if a.only else None
    for it in spec["items"]:
        if not only or it["name"] in only:
            r.item(it)
    if a.compare or not only:
        for c in spec.get("compare", []):
            r.compare(c)


if __name__ == "__main__":
    main()
