"""Kho dữ liệu chung của các Lab (Rig / Pose / Review), thay cho db của artifact khi chạy trên máy.
Mỗi trang có một vùng tên (ns). Dữ liệu là file JSON thật: work/store/<ns>/<collection>/<id>.json
(đọc, sao lưu, đưa vào git được). API do Home server phục vụ, xem handle().

  GET    /api/store                      → {"namespaces": [...]}
  GET    /api/store/<ns>                 → {"collections": {"col": số_doc}}
  GET    /api/store/<ns>/<col>           → {"docs": [{"id", "data"}]}
  POST   /api/store/<ns>/<col>           → thêm doc, id tự sinh → {"id"}
  GET    /api/store/<ns>/<col>/<id>      → {"exists", "data"}
  PUT    /api/store/<ns>/<col>/<id>      → ghi đè doc
  PATCH  /api/store/<ns>/<col>/<id>      → gộp trường vào doc
  DELETE /api/store/<ns>/<col>/<id>      → xoá doc
"""
import json, os, re, time, uuid

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
BASE = os.path.join(ROOT, "work", "store")
SAFE = re.compile(r"[^A-Za-z0-9_.\-]")


def _seg(s):
    s = SAFE.sub("_", s or "").strip(".")
    if not s:
        raise ValueError("tên rỗng")
    return s[:120]


def _dir(ns, col):
    return os.path.join(BASE, _seg(ns), _seg(col))


def _file(ns, col, id_):
    return os.path.join(_dir(ns, col), _seg(id_) + ".json")


def _read(p):
    with open(p, encoding="utf8") as f:
        return json.load(f)


def _write(p, data):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, p)


def handle(method, parts, body):
    """parts = phần đường dẫn sau /api/store/. Trả (mã, đối tượng)."""
    if parts == [""] or parts == []:
        ns = sorted(d for d in os.listdir(BASE)) if os.path.isdir(BASE) else []
        return 200, {"namespaces": ns}
    if parts[0] == "_ping":
        return 200, {"ok": True, "base": os.path.relpath(BASE, ROOT).replace("\\", "/")}
    ns = parts[0]
    if len(parts) == 1:
        d = os.path.join(BASE, _seg(ns))
        cols = {}
        if os.path.isdir(d):
            for c in sorted(os.listdir(d)):
                cd = os.path.join(d, c)
                if os.path.isdir(cd):
                    cols[c] = sum(1 for f in os.listdir(cd) if f.endswith(".json"))
        return 200, {"collections": cols}
    col = parts[1]
    if len(parts) == 2:
        if method == "GET":
            d = _dir(ns, col)
            docs = []
            if os.path.isdir(d):
                for f in sorted(os.listdir(d)):
                    if f.endswith(".json"):
                        try:
                            docs.append({"id": f[:-5], "data": _read(os.path.join(d, f))})
                        except Exception:
                            pass
            return 200, {"docs": docs}
        if method == "POST":
            id_ = "%x%s" % (int(time.time() * 1000), uuid.uuid4().hex[:6])
            _write(_file(ns, col, id_), body)
            return 200, {"id": id_}
        return 405, {"error": "method"}
    id_ = "/".join(parts[2:])
    p = _file(ns, col, id_)
    if method == "GET":
        return 200, ({"exists": True, "data": _read(p)} if os.path.isfile(p) else {"exists": False, "data": None})
    if method == "PUT":
        _write(p, body)
        return 200, {"ok": True}
    if method == "PATCH":
        cur = _read(p) if os.path.isfile(p) else {}
        cur.update(body)
        _write(p, cur)
        return 200, {"ok": True}
    if method == "DELETE":
        if os.path.isfile(p):
            os.remove(p)
        return 200, {"ok": True}
    return 405, {"error": "method"}
