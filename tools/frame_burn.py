"""Ghi số frame lên video demo để người xem góp ý đúng frame ("frame 37 bị giật").

  python -I tools/frame_burn.py <video vào> <video ra> [--start 1] [--fps 30] [--pos tl|tr|bl|br] [--gif <file gif ra>]

- Số frame đếm từ --start (mặc định 1, như Maya / Spine hiển thị 1..N); chữ dạng "F 37 / 120" kèm giây, nền đen mờ, ở góc (mặc định trái trên).
- Không đổi kích thước, giữ fps của video vào (hoặc --fps nếu ép). Chiều rộng lẻ được cắt 1 px cho đúng yêu cầu của H.264.
- --gif: xuất thêm GIF có số frame (nặng hơn MP4, MP4 nên gửi trước).
- Cần ffmpeg trong PATH. In một dòng JSON: file ra, số frame, fps.
"""
import json, os, subprocess, sys

FONT = "C\\:/Windows/Fonts/consola.ttf"


def probe(path):
    p = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate,nb_frames",
                        "-of", "json", path], capture_output=True, text=True)
    s = (json.loads(p.stdout).get("streams") or [{}])[0]
    num, den = (s.get("r_frame_rate") or "30/1").split("/")
    fps = float(num) / float(den or 1)
    n = int(s["nb_frames"]) if s.get("nb_frames", "").isdigit() else None
    return int(s["width"]), int(s["height"]), fps, n


def opt(a, name, default=None):
    if name in a:
        i = a.index(name)
        v = a[i + 1] if i + 1 < len(a) else default
        del a[i:i + 2]
        return v
    return default


def main():
    a = sys.argv[1:]
    start = int(opt(a, "--start", 1))
    fps_force = opt(a, "--fps")
    pos = opt(a, "--pos", "tl")
    gif = opt(a, "--gif")
    if len(a) < 2 or not os.path.isfile(a[0]):
        sys.exit(__doc__)
    src, dst = a[0], a[1]
    w, h, fps, n = probe(src)
    if fps_force:
        fps = float(fps_force)
    if n is None:
        # đếm frame thật
        p = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries", "stream=nb_read_frames",
                            "-of", "default=nw=1:nk=1", src], capture_output=True, text=True)
        n = int(p.stdout.strip() or 0)
    size = max(14, round(h / 28))
    margin = max(6, round(h / 80))
    x = {"tl": f"{margin}", "bl": f"{margin}", "tr": f"w-tw-{margin}", "br": f"w-tw-{margin}"}[pos]
    y = {"tl": f"{margin}", "tr": f"{margin}", "bl": f"h-th-{margin}", "br": f"h-th-{margin}"}[pos]
    last = start + n - 1
    text = "F %{eif\\:n+" + str(start) + "\\:d} / " + str(last)
    draw = (f"drawtext=fontfile='{FONT}':text='{text}':fontsize={size}:fontcolor=white:box=1:boxcolor=black@0.55:boxborderw=6:x={x}:y={y}")
    vf = f"crop=floor(iw/2)*2:floor(ih/2)*2,{draw}"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", src]
    if fps_force:
        cmd += ["-r", str(fps)]
    cmd += ["-vf", vf, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17", "-an", dst]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        sys.exit("ffmpeg lỗi: " + p.stderr.strip()[:400])
    res = {"mp4": dst, "frames": n, "fps": fps, "so_frame": f"{start}..{last}"}
    if gif:
        g = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", dst, "-vf",
                            f"fps={min(fps, 30)},split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer:bayer_scale=3",
                            gif], capture_output=True, text=True)
        res["gif"] = gif if g.returncode == 0 else "lỗi: " + g.stderr.strip()[:200]
    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
