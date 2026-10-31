"""Tạo ảnh cho một yêu cầu ở trang Key Pose (/keypose): đọc work/store/keypose/requests/<id>.json,
ghép prompt = prompt của ảnh gốc + phần sửa, gọi tools/codex_img.py lần lượt n ảnh, ghi trạng thái để trang hiện tiến độ.

  .venv/Scripts/python.exe -I tools/keypose_gen.py <id>                     # dùng chữ người yêu cầu làm phần sửa
  .venv/Scripts/python.exe -I tools/keypose_gen.py <id> --extra "English"   # Claude viết lại phần sửa cho rõ (nên dùng)
  .venv/Scripts/python.exe -I tools/keypose_gen.py <id> --prompt file.txt   # thay cả prompt (key mới không có ảnh gốc)
  .venv/Scripts/python.exe -I tools/keypose_gen.py <id> --extra "..." --markup note.jpg   # góp ý vẽ ở workspace Image Key: ảnh có nét khoanh làm ref cuối

Ảnh ra: keys/<key>_r<N>.png, góc khác góc chính: keys/<key>__<góc>_r<N>.png (+ prompts/…txt). Yêu cầu có "view" (right / left / front /
back / top / q34): ảnh gốc ở góc khác thì dựng lại đúng pose đó ở góc mới (VIEW CHANGE), kèm ảnh render model thật ở góc đó nếu có. Ref: keys/keypose.json {"refs": [...]} hoặc model_ref/ (xem tools/home/keypose.py).
Mỗi ảnh khoảng 1,5 phút, không chạy song song (codex_img tự xếp hàng).
Chuỗi flipbook (2026-10-31, tools/keypose_chain.py): key mới chưa có ảnh (base rỗng) dựng từ ảnh + prompt của key liền trước trong bảng pha,
kèm key chủ; mỗi ảnh ra được đo + căn khung ngay (keys/chain.json, ảnh gốc ở keys/_raw/); key trước đang lệch thì không tạo (--force bỏ qua).
  --dry: chỉ in prompt và danh sách ref để soát.
"""
import argparse, json, os, re, subprocess, sys, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "home"))
import keypose  # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "tools"))
import keypose_chain  # noqa: E402

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
    ap.add_argument("--dry", action="store_true", help="chỉ in prompt + ref + key trước/key chủ, không gọi Codex")
    ap.add_argument("--force", action="store_true", help="vẫn tạo dù key trước đang lệch chuỗi")
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
    # chuỗi flipbook (2026-10-31): key trước / key chủ theo bảng pha của anim
    suffix = "" if view == main_v else "__" + view
    me, master, prev = keypose_chain.neighbours(jd, r["job"], r.get("clip"), key, suffix)
    if prev and not a.force:
        pr = keypose_chain.book(jd).get(prev["name"]) or {}
        if pr and not pr.get("ok", True):
            patch(rp, status="error", error=f"Key trước {prev['name']} đang lệch chuỗi ({'; '.join(pr.get('bad') or [])}): sửa key đó trước")
            sys.exit("key trước lệch chuỗi")
    chain_new = not base and not a.prompt and prev is not None and not new_view
    if a.prompt:
        prompt = open(a.prompt, encoding="utf8").read()
    elif chain_new:   # key mới: prompt = prompt của ảnh key trước (bỏ khối Pose) + chỉ phần thay đổi
        head = keypose_chain.base_prompt(jd, prev["name"])
        if not head:
            patch(rp, status="error", error=f"Ảnh key trước {prev['name']} không có prompt: Claude cần viết prompt (--prompt)")
            sys.exit("key trước thiếu prompt")
        prompt = head + keypose_chain.next_key_block(prev, me, a.extra or r["text"])
    else:
        bp = os.path.join(kd, "prompts", base + ".txt")
        if not os.path.isfile(bp):   # ảnh gốc không có prompt: lấy prompt mới nhất cùng key (ưu tiên cùng góc)
            pd = os.path.join(kd, "prompts")
            cands = [f for f in os.listdir(pd) if keypose.key_of(f[:-4]) == key] if os.path.isdir(pd) else []
            same = [f for f in cands if (keypose.parse(f[:-4])[1] or main_v) == base_view]
            cands = sorted(same or cands, key=lambda f: os.path.getmtime(os.path.join(pd, f)))
            bp = os.path.join(pd, cands[-1]) if cands else ""
        if not bp:
            patch(rp, status="error", error="Không có prompt gốc cho key này và chưa có key trước trong bảng pha: Claude cần viết prompt (--prompt)")
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
    # concept gốc bắt buộc (người dùng 2026-10-31: "nhất định phải gửi theo concept gốc ... để không tạo ra đối tượng khác")
    concepts = keypose.concept_for(jd)
    if not concepts:
        patch(rp, status="error", error="Thiếu concept gốc của nhân vật: thêm file concept*.png vào thư mục job (hoặc keypose.json \"concept\")")
        sys.exit("thiếu concept gốc")
    # thứ tự ảnh: ref model (giữ số image 1/2/3 của prompt cũ) → concept → key chủ → key trước (khi sửa) → camref → ảnh gốc / key trước (CUỐI) → nét khoanh
    refs = [x for x in keypose.refs_for(jd) if x not in concepts]
    first = len(refs) + 1
    refs += concepts
    if keypose.CONCEPT_TAG not in prompt:
        prompt += keypose.concept_text(list(range(first, first + len(concepts))))
    prev_img = keypose_chain.img_path(jd, prev["name"]) if prev else None
    if master and (not prev or master["name"] != prev["name"]) and not new_view:
        refs.append(keypose_chain.img_path(jd, master["name"]))
        prompt += (f"\nAttached image {len(refs)} is the MASTER key of this animation ({master['name']}, approved): same character design, same size"
                   " in the frame, same ground line and framing as it.")
    if prev_img and not chain_new and not new_view:   # sửa key: key trước làm mốc khung (luật sửa mà vẫn giữ chuỗi)
        refs.append(prev_img)
        prompt += (f"\nAttached image {len(refs)} is the previous key of the animation ({prev['name']}): keep exactly its framing, character size,"
                   " ground line and planted-foot position.")
    cr = keypose.camref(jd, view)
    if cr and not chain_new:   # key mới theo chuỗi: khung lấy từ key trước, không lấy từ render
        refs = refs + [cr]
        prompt += "\nOne attached image (" + os.path.basename(cr) + ") is a render of the real model from exactly this camera: match its camera angle and framing."
    base_img = os.path.join(kd, base + ".png")
    if chain_new:
        refs.append(prev_img)   # câu "The LAST attached image is the previous key pose" đã nằm trong khối NEXT KEY
    elif base and os.path.isfile(base_img):
        refs = refs + [base_img]
        if not new_view:
            prompt += "\nThe LAST attached image is the previous version of this key pose: start from it and apply the revision."
    if a.markup and os.path.isfile(a.markup):   # ảnh người duyệt khoanh chỗ cần sửa (góp ý vẽ trong workspace Image Key)
        refs = refs + [a.markup]
        prompt += ("\nThe VERY LAST attached image is the reviewer's markup of the previous version: the coloured hand-drawn strokes circle the areas"
                   " to change as described above. Use it only to locate the problems; never draw strokes, circles or markup in the new image.")
    if a.dry:
        print(prompt)
        print("\nREFS:", *[os.path.relpath(x, ROOT) for x in refs], sep="\n  ")
        print("\nchuỗi:", {"pha": me and me.get("name"), "key chủ": master and master["name"], "key trước": prev and prev["name"], "key mới theo chuỗi": chain_new})
        return
    n = max(1, min(4, int(r.get("n") or 1)))
    results = list(r.get("results") or [])
    checks = dict(r.get("chain") or {})
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
            if prev or master:   # đo + căn khung ngay (vài ms), trước khi sinh ảnh tiếp
                rec = keypose_chain.check_one(jd, name, (prev or master)["name"], master and master["name"])
                checks[name] = {"ok": rec["ok"], "text": keypose_chain.summary(rec)}
                print("  chuỗi:", checks[name]["text"], flush=True)
        else:
            os.remove(pf)
            print((p.stdout + p.stderr)[-600:])
        patch(rp, progress=f"{i + 1}/{n}", results=results, chain=checks)
    # nhiều bản: bản đạt chuỗi lên trước
    results.sort(key=lambda x: not (checks.get(x) or {"ok": True})["ok"])
    st = "done" if results else "error"
    bad = [x for x in results if not (checks.get(x) or {"ok": True})["ok"]]
    note = ("Lệch chuỗi: " + "; ".join(f"{x}: {checks[x]['text']}" for x in bad)) if bad else ""
    reply = " | ".join(s for s in [a.reply, note] if s)
    patch(rp, status=st, progress="", done_at=time.strftime("%Y-%m-%dT%H:%M:%S"), results=results,
          error="" if results else "Codex không tạo được ảnh (xem log Claude)", **({"reply": reply} if reply else {}))
    print(json.dumps({"status": st, "results": results, "chain": checks}, ensure_ascii=False))

if __name__ == "__main__":
    main()
