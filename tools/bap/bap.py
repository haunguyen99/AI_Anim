"""Client cho BAP (Bug And Plan) https://bap.horusjsc.com, mục Phản hồi (/feedback).

Key (dạng wap_…) nằm trong tools/bap/.env, dòng BAP_KEY=… (không in ra, không vào git).
Tạo key: BAP → trang API tokens → Tạo token, dán vào .env.

  bap.py me                         kiểm key còn dùng được
  bap.py projects                   danh sách dự án (id + tên)
  bap.py list [--project ID] [-n 20]   phản hồi gần đây
  bap.py show <id>                  xem một phản hồi
  bap.py send --project ID --title "..." [--content "..."|--content-file f.md]
              [--place "..."] [--file ảnh.png ...]
                                    gửi phản hồi mới (kèm tệp nếu có), in số #seq + link
  bap.py spec                       tải openapi.json về tools/bap/
  bap.py get <đường dẫn>            GET /api/v1/<đường dẫn> (gỡ lỗi)
"""
import argparse
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.request
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = "https://bap.horusjsc.com"
BASE = SITE + "/api/v1"
UA = "AIAnimation-Claude/1.0"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def load_env():
    env = {}
    p = os.path.join(HERE, ".env")
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def load_key():
    key = os.environ.get("BAP_KEY") or load_env().get("BAP_KEY")
    if not key:
        raise SystemExit("Không thấy BAP_KEY trong tools/bap/.env")
    return key


def _send(method, path, data=None, ctype=None):
    headers = {"Authorization": "Bearer " + load_key(), "Accept": "application/json", "User-Agent": UA}
    if ctype:
        headers["Content-Type"] = ctype
    req = urllib.request.Request(BASE + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    return _send(method, path, data, "application/json" if data else None)


def api(method, path, body=None):
    st, txt = call(method, path, body)
    if st == 401:
        raise SystemExit("BAP từ chối key (401 Chưa đăng nhập): key sai / đã thu hồi. Tạo key mới trong BAP rồi dán vào tools/bap/.env")
    if st >= 300:
        raise SystemExit(f"BAP lỗi HTTP {st}: {txt[:300]}")
    return json.loads(txt) if txt.strip() else None


def upload(fid, files):
    b = uuid.uuid4().hex
    parts = []
    for f in files:
        name = os.path.basename(f)
        ct = mimetypes.guess_type(name)[0] or "application/octet-stream"
        parts.append((f"--{b}\r\nContent-Disposition: form-data; name=\"files\"; filename=\"{name}\"\r\n"
                      f"Content-Type: {ct}\r\n\r\n").encode() + open(f, "rb").read() + b"\r\n")
    data = b"".join(parts) + f"--{b}--\r\n".encode()
    st, txt = _send("POST", f"/feedback/{fid}/attachments", data, f"multipart/form-data; boundary={b}")
    if st >= 300:
        raise SystemExit(f"Đã tạo phản hồi nhưng tải tệp lỗi HTTP {st}: {txt[:300]}")


def items(res):
    if isinstance(res, dict):
        for k in ("items", "data", "results", "feedback", "projects"):
            if isinstance(res.get(k), list):
                return res[k]
    return res if isinstance(res, list) else []


def send_feedback(project, title, content="", place="", files=()):
    """Gửi một phản hồi; trả về dict phản hồi (có id, seq). Dùng được từ script khác."""
    fb = api("POST", "/feedback", {"project_id": project, "title": title.strip(),
                                   "content": content, "place": place.strip()})
    if files:
        upload(fb["id"], files)
    return fb


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="me")
    ap.add_argument("arg", nargs="?")
    ap.add_argument("--project")
    ap.add_argument("--title")
    ap.add_argument("--content", default="")
    ap.add_argument("--content-file")
    ap.add_argument("--place", default="")
    ap.add_argument("--file", nargs="*", default=[])
    ap.add_argument("-n", type=int, default=20)
    a = ap.parse_args()

    if a.cmd == "me":
        print(json.dumps(api("GET", "/me"), ensure_ascii=False, indent=1)[:800])
    elif a.cmd == "projects":
        for p in items(api("GET", "/projects")):
            print(p.get("id"), "|", p.get("name") or p.get("title"), "|", p.get("code") or p.get("key") or "")
    elif a.cmd == "list":
        q = f"?limit={a.n}" + (f"&project_id={a.project}" if a.project else "")
        for f in items(api("GET", "/feedback" + q)):
            print(f"#{f.get('seq')} [{f.get('status', '')}] {f.get('title')}  (id {f.get('id')})")
    elif a.cmd == "show":
        print(json.dumps(api("GET", f"/feedback/{a.arg}"), ensure_ascii=False, indent=1))
    elif a.cmd == "send":
        if not (a.project and a.title):
            raise SystemExit("Cần --project và --title")
        content = open(a.content_file, encoding="utf-8").read() if a.content_file else a.content
        try:
            pid = int(a.project)
        except ValueError:
            pid = a.project
        fb = send_feedback(pid, a.title, content, a.place, a.file)
        print(f"Đã gửi phản hồi #{fb.get('seq')} (id {fb.get('id')}) {SITE}/feedback/{fb.get('id')}")
    elif a.cmd == "spec":
        st, txt = call("GET", "/openapi.json")
        print("HTTP", st)
        if st == 200:
            open(os.path.join(HERE, "openapi.json"), "w", encoding="utf-8").write(txt)
            for p, m in json.loads(txt).get("paths", {}).items():
                for k, v in m.items():
                    print(k.upper(), p, "-", v.get("summary", ""))
        else:
            print(txt[:300])
    elif a.cmd == "get":
        st, txt = call("GET", a.arg if a.arg.startswith("/") else "/" + a.arg)
        print("HTTP", st)
        print(txt[:3000])
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
