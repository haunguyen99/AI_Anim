"""Spine Live: server riêng (tách khỏi Home từ 2026-11-05).

Chạy:  .venv\\Scripts\\python.exe -I tools\\spine_live\\server.py   rồi mở http://127.0.0.1:8781/spine
       thêm --lan để máy khác cùng mạng mở được (không mật khẩu, chỉ dùng trong mạng tin cậy).
Cổng: SPINE_PORT (mặc định 8781). Code xử lý vẫn là tools/home/spine_live.py + spine_edit.py + spine_bridge.py;
Home (cổng 8780) không còn phục vụ Spine Live, /spine trên Home chỉ chuyển sang đây.
"""
import json, os, re, sys, time, traceback
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, unquote, parse_qs

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "home"))
import spine_live

PORT = int(os.environ.get("SPINE_PORT") or "8781")
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
LOG = os.path.join(ROOT, "work", "store", "_sys", "spine_live", "server.log")
STARTED = time.strftime("%Y-%m-%d %H:%M:%S")


def log(msg):
    """server.log (2026-11-10, rà soát: server tắt mà không có dấu vết nào): lúc bật, lỗi xử lý (kèm traceback)."""
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        if os.path.exists(LOG) and os.path.getsize(LOG) > 2_000_000:   # giữ log nhỏ
            os.replace(LOG, LOG + ".1")
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(time.strftime("%Y-%m-%d %H:%M:%S") + f" [{os.getpid()}] " + msg.rstrip() + "\n")
    except Exception:
        pass


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send_json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_bytes(self, data, ctype, nocache=False):
        total = len(data)
        code, start, end = 200, 0, total - 1
        m = re.match(r"bytes=(\d*)-(\d*)", self.headers.get("Range") or "")
        if m and total:
            a, b = m.group(1), m.group(2)
            start = int(a) if a else max(0, total - int(b or 0))
            end = min(int(b) if (a and b) else total - 1, total - 1)
            if start > end:
                self.send_response(416)
                self.send_header("Content-Range", "bytes */%d" % total)
                self.end_headers()
                return
            code = 206
        chunk = data[start:end + 1]
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        if code == 206:
            self.send_header("Content-Range", "bytes %d-%d/%d" % (start, end, total))
        self.send_header("Content-Length", str(len(chunk)))
        self.send_header("Cache-Control", "no-store" if nocache or ctype.startswith("text/html") else "max-age=60")
        self.end_headers()
        self.wfile.write(chunk)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        try:
            self._get()
        except (ConnectionError, BrokenPipeError):
            pass
        except Exception:
            log("LỖI GET " + self.path + "\n" + traceback.format_exc())
            try:
                self.send_json({"ok": False, "error": "lỗi server, xem work/store/_sys/spine_live/server.log"}, 500)
            except Exception:
                pass

    def do_POST(self):
        try:
            self._post()
        except (ConnectionError, BrokenPipeError):
            pass
        except Exception:
            log("LỖI POST " + self.path + "\n" + traceback.format_exc())
            try:
                self.send_json({"ok": False, "error": "lỗi server, xem work/store/_sys/spine_live/server.log"}, 500)
            except Exception:
                pass

    def _get(self):
        u = urlparse(self.path)
        path = unquote(u.path)
        if path in ("", "/", "/index.html"):   # gốc = trang Spine Live
            self.send_response(302)
            self.send_header("Location", "/spine" + ("?" + u.query if u.query else ""))
            self.end_headers()
            return
        if path == "/favicon.ico":
            return self.send_error(404)
        if path == "/api/spine/ping":   # còn sống không (ensure_server.py, đèn báo trên trang)
            return self.send_json({"ok": True, "pid": os.getpid(), "since": STARTED, "port": PORT})
        if spine_live.handle_get(self, path, parse_qs(u.query)):
            return
        self.send_error(404)

    def _post(self):
        path = unquote(urlparse(self.path).path)
        if path.startswith("/api/spine/"):
            n = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(n) or b"{}"
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:   # curl trên Windows đổi tham số dòng lệnh sang bảng mã ANSI (rà soát 2026-11-10)
                return self.send_json({"ok": False, "error": "body không phải UTF-8: ghi JSON ra file rồi gửi bằng "
                                       "curl --data-binary @file.json (hoặc dùng tools/spine_live_cmd.py)"}, 400)
            try:
                body = json.loads(text)
            except ValueError as e:
                return self.send_json({"ok": False, "error": f"JSON không hợp lệ: {e}"}, 400)
            if spine_live.handle_post(self, path, body):
                return
        self.send_error(404)


if __name__ == "__main__":
    lan = "--lan" in sys.argv
    print(f"Spine Live: http://127.0.0.1:{PORT}/spine")
    log(f"bật server cổng {PORT}" + (" (LAN)" if lan else ""))
    try:
        ThreadingHTTPServer(("0.0.0.0" if lan else "127.0.0.1", PORT), H).serve_forever()
    except BaseException as e:
        log(f"server dừng: {type(e).__name__}: {e}")
        raise
