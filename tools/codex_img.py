"""Tạo ảnh qua Codex CLI (gói ChatGPT, không tốn phí API).

Dùng codex.exe đi kèm app Codex (không cần Node/npm). Mỗi ảnh là một lần
`codex exec`, khoảng 60–90 giây.

    .venv/Scripts/python.exe -I tools/codex_img.py "prompt" --out work/x/key_f12.png
    .venv/Scripts/python.exe -I tools/codex_img.py prompt.txt --out work/x/f12.png --ref char_front.png --ref char_side.png -n 3

- prompt: chuỗi, hoặc đường dẫn file .txt/.md chứa prompt.
- --ref: ảnh tham chiếu (nhân vật chụp từ Studio...), gửi kèm để giữ tạo hình.
- -n: số phương án; ra <out>_v1.png, _v2.png... (n = 1 thì đúng <out>).
In ra đường dẫn các ảnh đã lưu (mỗi dòng một ảnh), mã thoát 1 nếu thiếu ảnh.

KHÔNG chạy song song: nhiều codex exec cùng lúc làm mới token ChatGPT chồng nhau → 401 Unauthorized
(2026-10-28, 5 ảnh song song hỏng cả 5). Tool tự xếp hàng bằng file khóa trong %TEMP%.
"""
import argparse
import glob
import json
import os
import subprocess
import sys
import time


def find_codex():
    root = os.path.join(os.environ.get("LOCALAPPDATA", ""), "OpenAI", "Codex", "bin")
    cands = glob.glob(os.path.join(root, "*", "codex.exe"))
    if not cands:
        sys.exit("Không thấy codex.exe trong %s (app Codex chưa cài?)" % root)
    return max(cands, key=os.path.getmtime)  # app tự cập nhật → lấy bản mới nhất


def run_one(codex, prompt, out, refs, timeout):
    out = os.path.abspath(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if os.path.exists(out):
        os.remove(out)
    task = (
        "Generate exactly ONE image with your built-in image generation tool (not the CLI fallback). "
        + ("The attached image(s) are REFERENCE images of the character: keep its design, proportions, "
           "armor and props exactly; only change the pose. " if refs else "")
        + "Image request:\n" + prompt.strip()
        + "\n\nThen copy the generated PNG to this exact path: " + out
        + "\nReply with only that path. Do not create any other files."
    )
    cmd = [codex, "exec", "--skip-git-repo-check", "-s", "workspace-write",
           "-C", os.path.dirname(out), "--json"]
    for r in refs:
        cmd += ["-i", os.path.abspath(r)]
    cmd.append("-")  # prompt qua stdin: -i nhận nhiều file nên sẽ nuốt prompt đứng sau
    t0 = time.time()
    try:
        p = subprocess.run(cmd, input=task, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=timeout)
    except subprocess.TimeoutExpired:
        sys.stderr.write("[codex_img] FAIL timeout %ds\n" % timeout)
        return False
    last = ""
    for line in p.stdout.splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        it = ev.get("item") or {}
        if it.get("type") == "agent_message":
            last = it.get("text", "")
    ok = os.path.exists(out)
    sys.stderr.write("[codex_img] %s %.0fs %s\n" % ("OK" if ok else "FAIL", time.time() - t0,
                                                   "" if ok else (last or p.stderr[-800:])))
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt")
    ap.add_argument("--out", required=True)
    ap.add_argument("--ref", action="append", default=[])
    ap.add_argument("-n", type=int, default=1)
    ap.add_argument("--timeout", type=int, default=400)
    a = ap.parse_args()
    prompt = a.prompt
    if os.path.isfile(prompt):
        with open(prompt, encoding="utf-8") as f:
            prompt = f.read()
    for r in a.ref:
        if not os.path.isfile(r):
            sys.exit("Không thấy ảnh ref: " + r)
    codex = find_codex()
    lock = os.path.join(os.environ.get("TEMP", "."), "codex_img.lock")
    while True:  # xếp hàng: một codex exec mỗi lúc
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            if time.time() - os.path.getmtime(lock) > a.timeout * a.n + 60:
                os.remove(lock)  # khóa mồ côi
            time.sleep(3)
    try:
        _run_all(a, prompt, codex)
    finally:
        os.close(fd)
        os.remove(lock)


def _run_all(a, prompt, codex):
    base, ext = os.path.splitext(a.out)
    outs = [a.out] if a.n == 1 else ["%s_v%d%s" % (base, i + 1, ext or ".png") for i in range(a.n)]
    bad = 0
    for o in outs:
        if run_one(codex, prompt, o, a.ref, a.timeout):
            print(os.path.abspath(o))
        else:
            bad += 1
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
