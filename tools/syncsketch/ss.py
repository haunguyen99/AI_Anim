"""SyncSketch (dự án review video của team) bằng HTTP thuần, không cài thư viện ngoài. Dựa trên API chính thức syncsketch/python-api.

Khóa: tools/syncsketch/.env (git-ignored, KHÔNG gửi vào chat):
  SYNCSKETCH_USER=<tên người dùng hoặc email>
  SYNCSKETCH_KEY=<API key của tài khoản (Settings -> API key)>
  SYNCSKETCH_PROJECT=604066
  SYNCSKETCH_HOST=https://www.syncsketch.com        (tuỳ chọn)

  python -I tools/syncsketch/ss.py check                         # thử đăng nhập + đọc dự án
  python -I tools/syncsketch/ss.py reviews                       # danh sách review của dự án
  python -I tools/syncsketch/ss.py review <tên> [--create]       # tìm review theo tên (--create: tạo nếu chưa có), in id + link
  python -I tools/syncsketch/ss.py upload <tên review | id> <file> [--name <tên item>] [--parent <item id>]   # tải video lên (tạo review nếu chưa có); --parent = thêm thành PHIÊN BẢN MỚI của item đó
  python -I tools/syncsketch/ss.py notes <item id>               # đọc ghi chú / bình luận của người xem (theo frame)

Mỗi lệnh in một dòng JSON. Chưa kiểm với máy chủ thật nếu chưa có khóa.
"""
import json, mimetypes, os, sys, urllib.error, urllib.parse, urllib.request, uuid

HERE = os.path.dirname(os.path.abspath(__file__))


def env():
    cfg = {}
    f = os.path.join(HERE, ".env")
    if not os.path.exists(f):
        sys.exit(f"Thiếu {f}: tạo file với SYNCSKETCH_USER=... SYNCSKETCH_KEY=... SYNCSKETCH_PROJECT=604066 (khóa từ Settings -> API key của tài khoản SyncSketch)")
    for line in open(f, encoding="utf8").read().splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            cfg[k.strip()] = v.strip().strip('"').strip("'")
    for k in ("SYNCSKETCH_USER", "SYNCSKETCH_KEY"):
        if not cfg.get(k):
            sys.exit(f"Thiếu {k} trong {f}")
    cfg.setdefault("SYNCSKETCH_PROJECT", "604066")
    cfg.setdefault("SYNCSKETCH_HOST", "https://www.syncsketch.com")
    return cfg


def call(cfg, method, path, params=None, body=None, files=None, form=None, timeout=120):
    q = dict(params or {})
    url = cfg["SYNCSKETCH_HOST"].rstrip("/") + path
    if q:
        url += "?" + urllib.parse.urlencode(q)
    headers = {"Authorization": f"apikey {cfg['SYNCSKETCH_USER']}:{cfg['SYNCSKETCH_KEY']}", "Accept": "application/json",
               "User-Agent": "AI-Animation-syncsketch/1.0"}
    data = None
    if files is not None:  # multipart
        b = "----ss" + uuid.uuid4().hex
        CRLF = "\r\n"
        parts = []
        for k, v in (form or {}).items():
            if v is not None:
                parts.append(f'--{b}{CRLF}Content-Disposition: form-data; name="{k}"{CRLF}{CRLF}{v}{CRLF}'.encode("utf8"))
        for k, (fname, content) in files.items():
            ct = mimetypes.guess_type(fname)[0] or "application/octet-stream"
            parts.append(f'--{b}{CRLF}Content-Disposition: form-data; name="{k}"; filename="{fname}"{CRLF}Content-Type: {ct}{CRLF}{CRLF}'.encode("utf8"))
            parts.append(content)
            parts.append(CRLF.encode())
        parts.append(f"--{b}--{CRLF}".encode())
        data = b"".join(parts)
        headers["Content-Type"] = f"multipart/form-data; boundary={b}"
    elif body is not None:
        data = json.dumps(body).encode("utf8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            txt = r.read().decode("utf8", "replace")
            return json.loads(txt) if txt.strip().startswith(("{", "[")) else {"raw": txt[:300]}
    except urllib.error.HTTPError as e:
        sys.exit(f"SyncSketch {method} {path}: {e.code} {e.read().decode('utf8', 'replace')[:300]}")


def out(o):
    print(json.dumps(o, ensure_ascii=False))


def project_reviews(cfg):
    r = call(cfg, "GET", "/api/v1/review/", {"project__id": cfg["SYNCSKETCH_PROJECT"], "project__active": 1,
                                             "project__is_archived": 0, "limit": 200, "offset": 0})
    return r.get("objects") or []


def find_review(cfg, name):
    n = str(name).strip().lower()
    for r in project_reviews(cfg):
        if str(r.get("id")) == n or (r.get("name") or "").strip().lower() == n:
            return r
    return None


def create_review(cfg, name, desc=""):
    return call(cfg, "POST", "/api/v1/review/", body={"project": f"/api/v1/project/{cfg['SYNCSKETCH_PROJECT']}/",
                                                      "name": name, "description": desc})


def review_url(r):
    return r.get("reviewURL") or r.get("review_url") or (f"https://syncsketch.com/sketch/{r['uuid']}/" if r.get("uuid") else "")


def opt(a, name, default=None):
    if name in a:
        i = a.index(name)
        v = a[i + 1] if i + 1 < len(a) else default
        del a[i:i + 2]
        return v
    return default


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    cmd, a = a[0], a[1:]
    cfg = env()
    if cmd == "check":
        r = call(cfg, "GET", f"/api/v1/project/{cfg['SYNCSKETCH_PROJECT']}/")
        out({"ket_noi": "OK", "du_an": r.get("name"), "id": r.get("id")})
    elif cmd == "reviews":
        for r in project_reviews(cfg):
            out({"id": r.get("id"), "name": r.get("name"), "url": review_url(r)})
    elif cmd == "review":
        create = "--create" in a
        a = [x for x in a if x != "--create"]
        name = " ".join(a)
        r = find_review(cfg, name)
        if not r and create:
            r = create_review(cfg, name)
        if not r:
            sys.exit(f"Chưa có review '{name}' (thêm --create để tạo)")
        out({"id": r.get("id"), "name": r.get("name"), "url": review_url(r)})
    elif cmd == "upload":
        name = opt(a, "--name")
        parent = opt(a, "--parent")
        rev, fp = a[0], a[1]
        if not os.path.isfile(fp):
            sys.exit(f"Không thấy file {fp}")
        r = find_review(cfg, rev) or create_review(cfg, rev)
        rid = r.get("id")
        data = open(fp, "rb").read()
        fname = name or os.path.basename(fp)
        params = {"api_key": cfg["SYNCSKETCH_KEY"], "username": cfg["SYNCSKETCH_USER"]}
        if parent:
            params["itemParentId"] = parent
        res = call(cfg, "POST", f"/items/uploadToReview/{rid}/", params=params,
                   files={"reviewFile": (os.path.basename(fp), data)}, form={"artist": "AI Animation", "name": fname}, timeout=600)
        item = res.get("id") or (res.get("objects") or [{}])[0].get("id") if isinstance(res, dict) else None
        out({"review_id": rid, "review_url": review_url(r), "item_id": item, "raw": str(res)[:200]})
    elif cmd == "notes":
        item = a[0]
        r = call(cfg, "GET", "/api/v1/frame/", {"item__id": item, "active": 1, "limit": 500})
        for fr in r.get("objects") or []:
            for c in fr.get("comments") or []:
                out({"frame": fr.get("frame") if fr.get("frame") is not None else fr.get("number"),
                     "author": (c.get("user") or {}).get("username") if isinstance(c.get("user"), dict) else c.get("creator") or c.get("user"),
                     "text": c.get("text"), "id": c.get("id"), "created": c.get("created")})
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
