"""Playblast cho Spine Live (2026-11-27, người dùng: "tạo công cụ có thể playblast ở spinelive").

Trang (tools/spine_live/playblast.js) vẽ từng frame bằng runtime Spine THẬT (cầu nối `snap`, đủ IK / mesh / clipping / đổi ảnh slot),
gửi các tấm contact sheet lên đây; server cắt từng ô, đánh số frame, ghép mp4 H.264 bằng ffmpeg vào `<thư mục skeleton>/preview/`.

  POST /api/spine/playblast {op: "start",  json, anim}                          -> {id}
  POST /api/spine/playblast {op: "frames", id, png (dataURL), cols, cw, ch, frames: [số frame từng ô]}  -> {n}
  POST /api/spine/playblast {op: "finish", id, seq: [frame theo thứ tự phát], fps, burn, name?}        -> {video, url, frames, size}
  POST /api/spine/playblast {op: "cancel", id}
Video lấy qua GET /spine-live/f/<rel> (có Range để tua).
"""
import base64, io, os, re, shutil, subprocess, tempfile, time, uuid

JOBS = {}          # id -> {tmp, json, anim, t}
TTL = 3600


def _gc():
    now = time.time()
    for k in [k for k, j in JOBS.items() if now - j["t"] > TTL]:
        shutil.rmtree(JOBS.pop(k)["tmp"], ignore_errors=True)


def _font(size):
    from PIL import ImageFont
    for kw in ({"size": size},):
        try:
            return ImageFont.load_default(**kw)        # Pillow >= 10.1: font vector cỡ tuỳ ý
        except TypeError:
            pass
    return ImageFont.load_default()


def _job(b):
    j = JOBS.get(b.get("id"))
    if not j:
        raise ValueError("phiên quay không còn (hết hạn hoặc server khởi động lại): quay lại từ đầu")
    j["t"] = time.time()
    return j


def handle(b, safe, rel):
    from PIL import Image, ImageDraw
    op = b.get("op")
    _gc()
    if op == "start":
        js = safe(b.get("json", ""))
        if not js or not os.path.isfile(js):
            raise ValueError("không thấy file skeleton")
        anim = re.sub(r"[^\w\-]", "_", str(b.get("anim") or "setup"))[:60]
        jid = uuid.uuid4().hex[:12]
        JOBS[jid] = {"tmp": tempfile.mkdtemp(prefix="playblast_"), "json": js, "anim": anim, "t": time.time()}
        return {"id": jid}
    if op == "cancel":
        j = JOBS.pop(b.get("id"), None)
        if j:
            shutil.rmtree(j["tmp"], ignore_errors=True)
        return {}
    j = _job(b)
    if op == "frames":
        png = b.get("png", "")
        if "," not in png:
            raise ValueError("thiếu ảnh")
        sheet = Image.open(io.BytesIO(base64.b64decode(png.split(",", 1)[1]))).convert("RGB")
        cols, cw, ch, frames = int(b["cols"]), int(b["cw"]), int(b["ch"]), b["frames"]
        for k, f in enumerate(frames):
            x, y = (k % cols) * cw, (k // cols) * ch
            sheet.crop((x, y, x + cw, y + ch)).save(os.path.join(j["tmp"], "src_%d.png" % int(f)))
        return {"n": len(frames)}
    if op == "finish":
        seq = [int(f) for f in b.get("seq") or []]
        if not seq:
            raise ValueError("không có frame")
        fps = max(1, min(120, int(b.get("fps") or 30)))
        burn = bool(b.get("burn", True))
        tmp = j["tmp"]
        size = None
        cache = {}
        for n, f in enumerate(seq):
            src = os.path.join(tmp, "src_%d.png" % f)
            if not os.path.isfile(src):
                raise ValueError("thiếu frame %d (chưa gửi)" % f)
            im = cache.get(f) or Image.open(src).convert("RGB")
            size = im.size
            if burn:
                im = im.copy(); d = ImageDraw.Draw(im); fnt = _font(max(12, im.size[0] // 22)); txt = "F%d" % f
                for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                    d.text((8 + dx, 6 + dy), txt, font=fnt, fill=(0, 0, 0))
                d.text((8, 6), txt, font=fnt, fill=(255, 255, 255))
            im.save(os.path.join(tmp, "f_%05d.png" % (n + 1)))
        d_out = os.path.join(os.path.dirname(j["json"]), "preview")
        os.makedirs(d_out, exist_ok=True)
        name = re.sub(r"[^\w\-]", "_", str(b.get("name") or (j["anim"] + "_playblast")))[:80]
        out = os.path.join(d_out, name + ".mp4")
        r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", os.path.join(tmp, "f_%05d.png"),
                            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-movflags", "+faststart",
                            "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2", out], capture_output=True, text=True, timeout=300)
        if r.returncode:
            raise ValueError("ffmpeg lỗi: " + (r.stderr or "")[-300:])
        shutil.rmtree(JOBS.pop(b["id"])["tmp"], ignore_errors=True)
        rp = rel(out)
        return {"video": rp, "url": "/spine-live/f/" + rp, "frames": len(seq), "fps": fps, "size": list(size or (0, 0)),
                "bytes": os.path.getsize(out)}
    raise ValueError("op không hợp lệ: %s" % op)
