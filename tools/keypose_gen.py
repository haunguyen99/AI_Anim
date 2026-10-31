"""Tạo ảnh cho một yêu cầu ở trang Key Pose (/keypose): đọc work/store/keypose/requests/<id>.json,
ghép prompt = prompt của ảnh gốc + phần sửa, gọi tools/codex_img.py lần lượt n ảnh, ghi trạng thái để trang hiện tiến độ.

  .venv/Scripts/python.exe -I tools/keypose_gen.py <id>                     # dùng chữ người yêu cầu làm phần sửa
  .venv/Scripts/python.exe -I tools/keypose_gen.py <id> --extra "English"   # Claude viết lại phần sửa cho rõ (nên dùng)
  .venv/Scripts/python.exe -I tools/keypose_gen.py <id> --prompt file.txt   # thay cả prompt (key mới không có ảnh gốc)
  .venv/Scripts/python.exe -I tools/keypose_gen.py <id> --extra "..." --markup note.jpg   # góp ý vẽ ở workspace Image Key: ảnh có nét khoanh làm ref cuối

Ảnh ra: keys/<key>_r<N>.png, góc khác góc chính: keys/<key>__<góc>_r<N>.png (+ prompts/…txt). Yêu cầu có "view" (right / left / front /
back / top / q34): ảnh gốc ở góc khác thì dựng lại đúng pose đó ở góc mới (VIEW CHANGE), kèm ảnh render model thật ở góc đó nếu có. Ref: keys/keypose.json {"refs": [...]} hoặc model_ref/ (xem tools/home/keypose.py).
Mỗi ảnh khoảng 1,5 phút, không chạy song song (codex_img tự xếp hàng).
"""
import argparse, json, os, re, subprocess, sys, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "home"))
import keypose  # noqa: E402

REQ = os.path.join(ROOT, "work", "store", "keypose", "requests")
PY = sys.executable


def patch(path, **kw):
    d = json.load(open(path, encoding="utf8"))
    d.update(kw)
    tmp = path + ".tmp"
    json.dump(d, open(tmp, "w", encoding="utf8"), ensure_ascii=False)
    os.replace(tmp, path)
    return d


def next_r(kd, key):
    nums = [int(m.group(1)) for f in os.listdir(kd) for m in [re.match(re.escape(key) + r"_r(\d+)\.", f)] if m]
    return max(nums, default=0) + 1


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("id")
    ap.add_argument("--extra", help="phần sửa (tiếng Anh) thay cho chữ người yêu cầu")
    ap.add_argument("--prompt", help="file prompt thay cả prompt")
    ap.add_argument("--reply", help="lời nhắn hiện trên trang khi xong")
    ap.add_argument("--markup", help="ảnh góp ý có nét khoanh (Studio Image Key: studio_cmd.py notes --out), gửi kèm làm ref cuối")
    a = ap.parse_args()
    rp = os.path.join(REQ, a.id + ".json")
    r = json.load(open(rp, encoding="utf8"))
    jd = keypose.job_dir(r["job"])
    kd = os.path.join(jd, "keys")
    key = re.sub(r"[^A-Za-z0-9_]+", "_", r["key"])
    # góc nhìn (Image Key nhiều góc, 2026-10-30): view của yêu cầu; góc chính của nhân vật = ảnh không hậu tố
    main_v = keypose.views_cfg(jd)["main"]
    view = r.get("view") or main_v
    stem = key if view == main_v else key + "__" + view
    base = r.get("base") or ""
    base_view = keypose.parse(base)[1] or main_v if base else view
    new_view = view != base_view   # dựng góc mới từ ảnh của góc khác (thường là góc chính đã ★)
    if a.prompt:
        prompt = open(a.prompt, encoding="utf8").read()
    else:
        bp = os.path.join(kd, "prompts", base + ".txt")
        if not os.path.isfile(bp):   # ảnh gốc không có prompt: lấy prompt mới nhất cùng key (ưu tiên cùng góc)
            pd = os.path.join(kd, "prompts")
            cands = [f for f in os.listdir(pd) if keypose.key_of(f[:-4]) == key] if os.path.isdir(pd) else []
            same = [f for f in cands if (keypose.parse(f[:-4])[1] or main_v) == base_view]
            cands = sorted(same or cands, key=lambda f: os.path.getmtime(os.path.join(pd, f)))
            bp = os.path.join(pd, cands[-1]) if cands else ""
        if not bp:
            patch(rp, status="error", error="Không có prompt gốc cho key này: Claude cần viết prompt (--prompt)")
            sys.exit("thiếu prompt gốc")
        prompt = open(bp, encoding="utf8").read().rstrip()
        if new_view:
            prompt = re.sub(r"(?m)^Camera:.*$", "Camera: " + keypose.CAMERA[view], prompt)
            prompt += ("\n\nVIEW CHANGE: this image is the SAME key pose seen from another camera. The LAST attached image shows the approved pose from "
                       + keypose.VIEW_EN[base_view] + ": reproduce exactly that pose (limbs, prop, weight, facial expression) seen " + keypose.VIEW_EN[view]
                       + ". Do not change the pose, only the camera.")
            if r.get("text") or a.extra:
                prompt += "\nAlso: " + (a.extra or r["text"])
        else:
            prompt += ("\n\nREVISION REQUEST (apply exactly; keep character design, camera, framing and everything else unchanged):\n"
                       + (a.extra or r["text"]))
    refs = keypose.refs_for(jd)
    cr = keypose.camref(jd, view)
    if cr:   # ảnh render model thật ở đúng góc: khung camera
        refs = refs + [cr]
        prompt += "\nOne attached image (" + os.path.basename(cr) + ") is a render of the real model from exactly this camera: match its camera angle and framing."
    base_img = os.path.join(kd, base + ".png")
    if base and os.path.isfile(base_img):
        refs = refs + [base_img]
        if not new_view:
            prompt += "\nThe LAST attached image is the previous version of this key pose: start from it and apply the revision."
    if a.markup and os.path.isfile(a.markup):   # ảnh người duyệt khoanh chỗ cần sửa (góp ý vẽ trong workspace Image Key)
        refs = refs + [a.markup]
        prompt += ("\nThe VERY LAST attached image is the reviewer's markup of the previous version: the coloured hand-drawn strokes circle the areas"
                   " to change as described above. Use it only to locate the problems; never draw strokes, circles or markup in the new image.")
    n = max(1, min(4, int(r.get("n") or 1)))
    results = list(r.get("results") or [])
    patch(rp, status="working", progress=f"0/{n}", error="")
    os.makedirs(os.path.join(kd, "prompts"), exist_ok=True)
    for i in range(n):
        name = f"{stem}_r{next_r(kd, stem)}"
        pf = os.path.join(kd, "prompts", name + ".txt")
        open(pf, "w", encoding="utf8").write(prompt)
        cmd = [PY, "-I", os.path.join(ROOT, "tools", "codex_img.py"), pf, "--out", os.path.join(kd, name + ".png")]
        for x in refs:
            cmd += ["--ref", x]
        t = time.time()
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        ok = p.returncode == 0 and os.path.isfile(os.path.join(kd, name + ".png"))
        print(f"{name}: {'OK' if ok else 'LỖI'} {time.time() - t:.0f}s", flush=True)
        if ok:
            results.append(name)
        else:
            os.remove(pf)
            print((p.stdout + p.stderr)[-600:])
        patch(rp, progress=f"{i + 1}/{n}", results=results)
    st = "done" if results else "error"
    patch(rp, status=st, progress="", done_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
          error="" if results else "Codex không tạo được ảnh (xem log Claude)", **({"reply": a.reply} if a.reply else {}))
    print(json.dumps({"status": st, "results": results}, ensure_ascii=False))


if __name__ == "__main__":
    main()
