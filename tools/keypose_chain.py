"""Chuỗi ảnh key pose của một anim = một flipbook 2D (người dùng 2026-10-31). Dùng trong tools/keypose_gen.py và chạy riêng để kiểm.

- Key trước / key chủ: theo bảng pha keys/keypose.json "clips"[anim]["phases"] (xếp theo frame). Ảnh dùng của một key: ★ > ảnh mới nhất
  không bị ✕ (marks ở work/store/keypose/marks). Key chủ = key của pha đầu.
- Prompt key mới = prompt của ảnh key trước (bỏ phần sửa / ghi chú ref cũ, bỏ khối Pose:) + khối "NEXT KEY" chỉ ghi phần thay đổi.
- Đo ngay sau mỗi ảnh (vài ms): đường đất, chiều cao người, cột hông, 2 bàn chân ở đường đất, màu trung bình. Căn khung như ghim
  giấy 2D: đổi về khổ của key chủ, khớp đường đất, khớp bàn chân gần nhất với key trước. Ảnh gốc giữ ở keys/_raw/. Kết quả: keys/chain.json.

  .venv/Scripts/python.exe -I tools/keypose_chain.py check <job> <anim>      # đọc/đo cả chuỗi (không gọi Codex)
  .venv/Scripts/python.exe -I tools/keypose_chain.py measure ảnh.png ...
"""
import json, os, re, shutil, sys

import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "home"))
if "keypose" in sys.modules and not hasattr(sys.modules["keypose"], "job_dir"):   # tools/keypose/ (trang) trùng tên module
    del sys.modules["keypose"]
import keypose  # noqa: E402

MARKS = os.path.join(ROOT, "work", "store", "keypose", "marks")
# ngưỡng theo gdd_stage0.md mục "Đồng nhất chuỗi ảnh" (đơn vị: phần của chiều cao người key chủ)
TOL = {"ground": 0.01, "height": 0.03, "height_bad": 0.08, "foot": 0.01, "stance": 0.02, "stance_bad": 0.10, "color": 0.06}
STRIP = ["\n\nREVISION REQUEST", "\n\nVIEW CHANGE", "\n\n" + keypose.CONCEPT_TAG, "\n\nNEXT KEY", "\nOne attached image",
         "\nThe LAST attached", "\nThe VERY LAST", "\nAttached image "]


# ---------- chọn ảnh theo chuỗi
def marks(job):
    f = os.path.join(MARKS, job.replace("/", "__") + ".json")
    try:
        return json.load(open(f, encoding="utf8"))
    except (OSError, ValueError):
        return {}


def chosen(jd, job, key, view_stem_suffix=""):
    """ảnh dùng của key (ở một góc): ★ > mới nhất không ✕. Trả tên (không đuôi) hoặc None."""
    kd = os.path.join(jd, "keys")
    m = marks(job)
    stem = key + view_stem_suffix
    names = [os.path.splitext(f)[0] for f in os.listdir(kd) if f.lower().endswith(keypose.IMG)]
    names = [n for n in names if n == stem or re.fullmatch(re.escape(stem) + r"_(?:v|m|r)\d+", n)]
    if not names:
        return None
    star = [n for n in names if (m.get(n) or {}).get("mark") == "star"]
    ok = [n for n in names if (m.get(n) or {}).get("mark") != "reject"]
    pick = star or ok
    if not pick:
        return None
    return max(pick, key=lambda n: os.path.getmtime(img_path(jd, n)))


def img_path(jd, name):
    for ext in keypose.IMG:
        p = os.path.join(jd, "keys", name + ext)
        if os.path.isfile(p):
            return p
    return None


def phases(jd, clip):
    e = keypose._entry(keypose._cfg(jd), clip) if clip else None
    return sorted(((e or {}).get("phases") or []), key=lambda p: p.get("f") or 0)


def neighbours(jd, job, clip, key, suffix=""):
    """(pha của key, key chủ {key,name,phase}, key trước {key,name,phase}) theo bảng pha; key trước bỏ qua pha không có ảnh."""
    P = [p for p in phases(jd, clip) if p.get("key")]
    me = next((p for p in P if p["key"] == key), None)
    if not P or not me:
        return me, None, None
    m0 = P[0]
    master = {"key": m0["key"], "name": chosen(jd, job, m0["key"], suffix), "phase": m0}
    prev = None
    for p in reversed(P[:P.index(me)]):
        if p["key"] == key:
            continue
        n = chosen(jd, job, p["key"], suffix)
        if n:
            prev = {"key": p["key"], "name": n, "phase": p}
            break
    if master["key"] == key or not master["name"]:
        master = None
    return me, master, prev


# ---------- prompt
def base_prompt(jd, name):
    pf = os.path.join(jd, "keys", "prompts", name + ".txt")
    if not os.path.isfile(pf):
        return ""
    t = open(pf, encoding="utf8").read()
    cut = min([i for i in (t.find(s) for s in STRIP) if i >= 0] + [len(t)])
    t = t[:cut].rstrip()
    m = re.search(r"(?m)^Pose:", t)
    return t[:m.start()].rstrip() if m else t


def next_key_block(prev, me, change):
    pp = prev["phase"]
    return ("\n\nNEXT KEY OF THE SAME ANIMATION (like the next drawing of a 2D flipbook: played one after another they must form one smooth animation).\n"
            f"The LAST attached image is the previous key pose ({prev['name']}, frame F{pp.get('f')}, \"{pp.get('name')}\"). Copy it EXACTLY: the same "
            "character, same camera and angle, same canvas framing, same character size in the frame, same ground line height, same background and "
            "lighting; a foot that stays planted keeps exactly the same position on the ground. Do not redraw the costume, hair or prop differently.\n"
            f"Pose:\nThe ONLY changes for this key (frame F{me.get('f')}, \"{me.get('name')}\"): {change}\n"
            "Everything not listed above stays identical to the previous key. Apply each listed change at EXACTLY the amount written: not smaller "
            "and not larger (an 18 degree lean must clearly read as 18 degrees). Keep the same plain background colour as the previous key.")


# ---------- đo
def measure(path):
    a = np.asarray(Image.open(path).convert("RGB"), float)
    h, w = a.shape[:2]
    border = np.concatenate([a[:6].reshape(-1, 3), a[-6:].reshape(-1, 3), a[:, :6].reshape(-1, 3), a[:, -6:].reshape(-1, 3)])
    bg = np.median(border, axis=0)
    fg = np.abs(a - bg).sum(-1) > 40
    rows = np.where(fg.sum(1) > max(2, 0.003 * w))[0]
    if len(rows) < 10:
        return None
    top, ground = int(rows.min()), int(rows.max())
    H = ground - top
    ys, xs = np.nonzero(fg[top + int(0.45 * H): top + int(0.6 * H)])
    hipx = float(np.median(xs)) if len(xs) else w / 2
    band = fg[ground - max(3, int(0.03 * H)): ground + 1]
    cols = np.where(band.any(0))[0]
    feet, gap = [], max(4, int(0.015 * H))
    if len(cols):
        s = p = cols[0]
        for x in list(cols[1:]) + [10 ** 9]:
            if x - p > gap:
                if p - s > 0.01 * H:
                    feet.append([int(s), int(p)])
                s = x
            p = x
    rgb = a[fg].mean(0).tolist()
    return {"w": w, "h": h, "top": top, "ground": ground, "H": H, "hipx": hipx, "feet": feet, "rgb": rgb}


def _foot_c(f):
    return (f[0] + f[1]) / 2


def foot_shift(cur_feet, prev_feet, s=1.0):
    """dời ngang để ghim chân ảnh mới vào chân key trước. Ghép theo thứ tự trái→phải (góc side, chân sau / chân trước không đổi chỗ);
    số khối chân khác nhau (hai chân dính) thì dùng tâm cả vùng chân. Trả (dx, độ lệch từng cặp sau khi dời)."""
    if not cur_feet or not prev_feet:
        return None, []
    if len(cur_feet) == len(prev_feet):
        d = [_foot_c(g) - _foot_c(f) * s for f, g in zip(cur_feet, prev_feet)]
        dx = sum(d) / len(d)
        return dx, [abs(x - dx) for x in d]
    span = lambda F: (F[0][0] + F[-1][1]) / 2
    return span(prev_feet) - span(cur_feet) * s, []


def compare(cur, prev, master):
    """lệch của ảnh (đã căn) so với key trước và key chủ; trả (issues lỗi, warns chú ý, số đo)."""
    Hm = (master or prev)["H"]
    nums, bad, warn = {}, [], []
    nums["ground"] = abs(cur["ground"] - prev["ground"]) / Hm
    nums["height"] = abs(cur["H"] - (master or prev)["H"]) / Hm
    if prev["feet"] and cur["feet"]:
        if len(cur["feet"]) == len(prev["feet"]):   # chân trụ = chân dời ít nhất so với key trước (ghép theo thứ tự)
            nums["foot"] = min(abs(_foot_c(f) - _foot_c(g)) for f, g in zip(cur["feet"], prev["feet"])) / Hm
        else:
            nums["foot"] = abs(abs(foot_shift(cur["feet"], prev["feet"])[0])) / Hm
        st = lambda F: F[-1][1] - F[0][0]           # bề rộng cả vùng chân ở đường đất (hai chân dính thành một khối vẫn đo được)
        nums["stance"] = abs(st(cur["feet"]) - st(prev["feet"])) / Hm
    nums["color"] = float(np.abs(np.array(cur["rgb"]) - np.array((master or prev)["rgb"])).mean() / 255)
    if nums["ground"] > TOL["ground"]:
        bad.append(f"đường đất lệch {nums['ground']:.1%}")
    if nums["height"] > TOL["height_bad"]:
        bad.append(f"cỡ người lệch {nums['height']:.1%} so với key chủ")
    elif nums["height"] > TOL["height"]:
        warn.append(f"cỡ người lệch {nums['height']:.1%} (đúng nếu pha ngồi/ngả)")
    if nums.get("foot", 0) > TOL["foot"]:
        bad.append(f"chân trụ trượt {nums['foot']:.1%}")
    if nums.get("stance", 0) > TOL["stance_bad"]:
        bad.append(f"dáng chân đổi: bề rộng 2 chân lệch {nums['stance']:.1%} (pha có bước thì ghi rõ trong mô tả pha)")
    elif nums.get("stance", 0) > TOL["stance"]:
        warn.append(f"khoảng cách 2 chân đổi {nums['stance']:.1%} (đúng nếu pha có bước)")
    if nums["color"] > TOL["color"]:
        bad.append(f"màu lệch {nums['color']:.1%}")
    return bad, warn, {k: round(v, 4) for k, v in nums.items()}


def align(path, prev, master, raw_dir):
    """ghim ảnh vào khung chuỗi: khổ = khổ key chủ (hoặc key trước), cỡ người theo tỉ lệ khổ, khớp đường đất + chân gần nhất.
    Không phóng theo chiều cao người (pha ngả/ngồi đổi chiều cao thật). Ảnh gốc chép vào raw_dir. Trả (dx, dy, s) hoặc None."""
    ref = master or prev
    cur = measure(path)
    if not cur:
        return None
    im = Image.open(path).convert("RGB")
    s = ref["h"] / cur["h"]
    if abs(s - 1) > 1e-3:
        im = im.resize((round(cur["w"] * s), ref["h"]), Image.LANCZOS)
    sc = lambda v: v * s
    dy = prev["ground"] - sc(cur["ground"])
    dx = (ref["w"] - im.width) / 2
    fx = foot_shift(cur["feet"], prev["feet"], s)[0]
    if fx is not None:
        dx = fx
    dx, dy = int(round(dx)), int(round(dy))
    if abs(s - 1) < 1e-3 and dx == 0 and dy == 0 and im.width == ref["w"]:
        return (0, 0, 1.0)
    a = np.asarray(im)
    bg = np.median(np.concatenate([a[:6].reshape(-1, 3), a[:, :6].reshape(-1, 3)]), axis=0).astype(np.uint8)
    out = Image.new("RGB", (ref["w"], ref["h"]), tuple(int(c) for c in bg))
    out.paste(im, (dx, dy))
    os.makedirs(raw_dir, exist_ok=True)
    raw = os.path.join(raw_dir, os.path.basename(path))
    if not os.path.isfile(raw):
        shutil.copy2(path, raw)
    out.save(path)
    return (dx, dy, round(s, 4))


def _bg(a):
    return np.median(np.concatenate([a[:6].reshape(-1, 3), a[-6:].reshape(-1, 3), a[:, :6].reshape(-1, 3), a[:, -6:].reshape(-1, 3)]), axis=0)


def fix_bg(path, master_path, raw_dir):
    """nền trơn của ảnh về đúng màu nền key chủ (Codex chép ảnh trước làm nền trôi dần, SDR03 Hit 2026-10-31: xám → xanh qua 3 key).
    Điểm nền và viền chống răng cưa được dời theo cùng một độ lệch màu, nhân vật giữ nguyên. Trả độ lệch nền trước khi sửa (0..1)."""
    a = np.asarray(Image.open(path).convert("RGB"), float)
    want = _bg(np.asarray(Image.open(master_path).convert("RGB"), float))
    have = _bg(a)
    d = float(np.abs(want - have).mean() / 255)
    if d < 0.004:
        return d
    dist = np.abs(a - have).sum(-1)
    w = np.clip(1 - (dist - 12) / 40, 0, 1)[..., None]      # 1 = nền, 0 = nhân vật, giữa = viền
    out = np.clip(a + w * (want - have), 0, 255).astype(np.uint8)
    os.makedirs(raw_dir, exist_ok=True)
    raw = os.path.join(raw_dir, os.path.basename(path))
    if not os.path.isfile(raw):
        shutil.copy2(path, raw)
    Image.fromarray(out).save(path)
    return d


# ---------- sổ đo keys/chain.json
def book(jd):
    f = os.path.join(jd, "keys", "chain.json")
    try:
        return json.load(open(f, encoding="utf8"))
    except (OSError, ValueError):
        return {}


def book_set(jd, name, rec):
    d = book(jd)
    d[name] = rec
    f = os.path.join(jd, "keys", "chain.json")
    json.dump(d, open(f + ".tmp", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    os.replace(f + ".tmp", f)


def metrics(jd, name):
    """số đo của ảnh (sổ chain.json nếu ảnh chưa đổi, không thì đo lại)."""
    p = img_path(jd, name)
    rec = book(jd).get(name) or {}
    if rec.get("m") and rec.get("mtime") == round(os.path.getmtime(p), 2):
        return rec["m"]
    return measure(p)


def check_one(jd, name, prev_name, master_name, do_align=True):
    """đo + (căn) + so một ảnh vừa tạo. Ghi sổ. Trả rec {ok, bad, warn, nums, aligned}."""
    p = img_path(jd, name)
    prev = metrics(jd, prev_name) if prev_name else None
    master = metrics(jd, master_name) if master_name else None
    rec = {"prev": prev_name, "master": master_name, "aligned": None}
    if prev and do_align:
        rec["aligned"] = align(p, prev, master, os.path.join(jd, "keys", "_raw"))
        mp = img_path(jd, master_name or prev_name)
        rec["bg_fixed"] = round(fix_bg(p, mp, os.path.join(jd, "keys", "_raw")), 4)
    cur = measure(p)
    rec["m"] = cur
    rec["mtime"] = round(os.path.getmtime(p), 2)
    if prev and cur:
        rec["bad"], rec["warn"], rec["nums"] = compare(cur, prev, master)
    else:
        rec["bad"], rec["warn"], rec["nums"] = ([] if cur else ["không tách được nhân vật khỏi nền"]), [], {}
    rec["ok"] = not rec["bad"]
    book_set(jd, name, rec)
    return rec


def summary(rec):
    if not rec.get("nums"):
        return "key chủ / chưa có key trước để so" if rec.get("ok") else "; ".join(rec["bad"])
    n = rec["nums"]
    s = f"đất {n.get('ground', 0):.1%}, cỡ {n.get('height', 0):.1%}, chân trụ {n.get('foot', 0):.1%}"
    if rec.get("aligned") and rec["aligned"] != (0, 0, 1.0) and list(rec["aligned"]) != [0, 0, 1.0]:
        s += " (đã căn khung)"
    if rec["bad"]:
        s = "LỆCH: " + "; ".join(rec["bad"]) + " | " + s
    if rec["warn"]:
        s += " | chú ý: " + "; ".join(rec["warn"])
    return s


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) >= 3 and sys.argv[1] == "measure":
        for p in sys.argv[2:]:
            print(p, json.dumps(measure(p)))
        return
    if len(sys.argv) >= 4 and sys.argv[1] == "check":
        job, clip = sys.argv[2], sys.argv[3]
        jd = keypose.job_dir(job)
        P = [p for p in phases(jd, clip) if p.get("key")]
        prev = master = None
        seen = []
        for p in P:
            n = chosen(jd, job, p["key"])
            tag = f"F{p.get('f'):>3} {p['key']:<14}"
            if not n:
                print(tag, "— chưa có ảnh dùng được")
                continue
            if p["key"] in seen:
                print(tag, n, "(dùng lại ảnh, giống hệt)")
                continue
            seen.append(p["key"])
            m = metrics(jd, n)
            if master is None:
                master = (n, m)
                print(tag, n, f"key chủ {m['w']}x{m['h']} người cao {m['H']}px")
            else:
                bad, warn, nums = compare(m, prev[1], master[1])
                size = "" if (m["w"], m["h"]) == (master[1]["w"], master[1]["h"]) else f" KHỔ {m['w']}x{m['h']} ≠ key chủ"
                print(tag, n, ("LỆCH: " + "; ".join(bad) if bad else "đạt") + size, nums, ("chú ý: " + "; ".join(warn)) if warn else "")
            prev = (n, m)
        return
    print(__doc__)


if __name__ == "__main__":
    main()
