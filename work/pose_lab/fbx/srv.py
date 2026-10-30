import http.server, os, sys
class H(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers["Content-Length"]); data = self.rfile.read(n)
        name = os.path.basename(self.path.split("?name=")[1])
        open(os.path.join("out", name), "wb").write(data)
        self.send_response(200); self.send_header("Access-Control-Allow-Origin", "*"); self.end_headers(); self.wfile.write(b"ok %d" % n)
    def log_message(self, *a): pass
os.makedirs("out", exist_ok=True)
http.server.ThreadingHTTPServer(("127.0.0.1", 8123), H).serve_forever()
