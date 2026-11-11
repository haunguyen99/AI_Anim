"""Video so sánh nhiều bản anim cùng khung xương Worker (Lumber), mỗi bản một cột, mỗi góc camera một hàng,
cùng tỉ lệ khung (không phóng riêng từng bản). Rìu AXE1 vẽ theo xương `accessory` (màu đỏ của render_pose).
    .venv/Scripts/python.exe -I tools/retarget/compare_video.py --out cmp.mp4 "Gốc Mixamo=a.fbx" "Style game=b.fbx"
        [--views game,front,side_r] [--size 300] [--fps 30] [--prop-follow Wrist_R]
--prop-follow: bản nào xương accessory không bám tay (bản retarget thẳng) thì gắn rìu vào xương này theo cách cầm của
bản đầu tiên có rìu bám tay (để so cùng một cách cầm)."""
import argparse, json, os, subprocess, sys, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, ".."))
from compare import track
import render_fbx_tex as RTX

DUMP = os.path.join(ROOT, "work", "g_lumbercity", "lumber_ropeway_crank", "review", "b50_v1.json")  # đỉnh + skin Worker
MODEL = r"E:\Horus\G-LumberCity\Assets\_Game\Animations\MC_Worker\MC_Worker.fbx"
TEX = r"E:\tvc_source\3D ANIM\G-LumberCity\T_color_palettes_3.tga"
BIND = os.path.join(ROOT, "work", "g_lumbercity", "base", "worker_bind_world.json")
RENDER = os.path.join(ROOT, "work", "g_lumbercity", "rig", "render_pose.py")
PY = os.path.join(ROOT, ".venv", "Scripts", "python.exe")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("clips", nargs="+"); ap.add_argument("--out", required=True)
    ap.add_argument("--views", default="game,front,side_r"); ap.add_argument("--size", type=int, default=300)
    ap.add_argument("--fps", type=int, default=30); ap.add_argument("--prop-follow", default="Wrist_R"); ap.add_argument("--no-prop", action="store_true", help="không vẽ rìu (vd Logger idle: game đeo rìu sau lưng)")
    a = ap.parse_args()
    clips = [c.split("=", 1) for c in a.clips]
    base = json.load(open(DUMP, encoding="utf-8"))
    joints = sorted({j for w in base["weights"] for j, _ in w})
    BW = {k: np.array(v) for k, v in json.load(open(BIND, encoding="utf-8")).items()}
    axe, _ = RTX.load(MODEL, TEX, only={"AXE1"})
    axe_v = axe.reshape(-1, 3); axe_t = np.arange(len(axe_v)).reshape(-1, 3).tolist()
    tracks = [track(p, a.fps) for _, p in clips]
    n = max(len(t) for t in tracks)
    # cách cầm chung: lấy từ bản đầu tiên có accessory bám cứng xương follow
    G = None
    for T in tracks:
        rel = [np.linalg.inv(W[a.prop_follow]) @ W["accessory"] for W in T]
        if np.ptp([r[:3, 3] for r in rel], axis=0).max() < 0.01:
            G = rel[0]; break
    frames, pos = {}, {}
    for ci, T in enumerate(tracks):
        rel = [np.linalg.inv(W[a.prop_follow]) @ W["accessory"] for W in T]
        follows = np.ptp([r[:3, 3] for r in rel], axis=0).max() < 0.01
        for f in range(n):
            W = T[min(f, len(T) - 1)]; key = "%d_%d" % (ci, f)
            frames[key] = {j: W[j].T.flatten().tolist() for j in joints}
            Wa = W["accessory"] if (follows or G is None) else W[a.prop_follow] @ G
            M = Wa @ np.linalg.inv(BW["accessory"])
            pos[key] = {"AXE1": ((np.c_[axe_v, np.ones(len(axe_v))] @ M.T)[:, :3]).tolist()}
    tmp = tempfile.mkdtemp(prefix="cmpvid_")
    dump = os.path.join(tmp, "dump.json")
    json.dump({"positions": base["positions"], "weights": base["weights"], "frames": frames,
               "prop_tris": {} if a.no_prop else {"AXE1": axe_t}, "prop_pos": pos}, open(dump, "w"))
    subprocess.run([PY, "-I", RENDER, dump, tmp, "--views", a.views, "--size", str(a.size), "--name", "sheet"], check=True)
    sheet = Image.open(os.path.join(tmp, "sheet.png"))
    S = a.size; vn = a.views.split(","); keys = list(frames)
    vname = {"game": "cam game", "front": "chính diện", "side_r": "bên phải", "top": "trên xuống", "game_front": "cam game trước"}
    head = 30
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 15)
    except OSError:
        font = None
    for f in range(n):
        img = Image.new("RGB", (S * len(clips), head + (S + 26) * len(vn)), (40, 42, 46)); dr = ImageDraw.Draw(img)
        for ci, (lab, _) in enumerate(clips):
            dr.text((ci * S + 8, 7), "%s   F%d" % (lab, f + 1), fill=(255, 220, 120), font=font)
            c = keys.index("%d_%d" % (ci, f))
            for r, v in enumerate(vn):
                cell = sheet.crop((c * S, r * (S + 26), (c + 1) * S, (r + 1) * (S + 26)))
                ImageDraw.Draw(cell).rectangle((0, 0, S, 25), fill=(40, 42, 46))
                ImageDraw.Draw(cell).text((6, 5), vname.get(v, v), fill=(220, 220, 220), font=font)
                img.paste(cell, (ci * S, head + r * (S + 26)))
        img.save(os.path.join(tmp, "f%04d.png" % f))
    w, h = img.size
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(a.fps), "-stream_loop", "2", "-i", os.path.join(tmp, "f%04d.png"),
                    "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", a.out], check=True)
    print("video: %s (%d frame × 3 vòng, %dx%d)" % (a.out, n, w, h))


if __name__ == "__main__":
    main()
