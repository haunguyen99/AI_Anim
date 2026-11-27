"""Máy chủ xem slide trong mạng nội bộ, không cho trình duyệt lưu đệm (ảnh luôn mới).
    python3 -I tools/slides_rigging_deck/serve_nocache.py [cổng=8799]   (thư mục gốc = docs/slides)"""
import http.server, os, sys
class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control','no-store, no-cache, must-revalidate, max-age=0'); self.send_header('Pragma','no-cache'); super().end_headers()
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','docs','slides'))
http.server.ThreadingHTTPServer(('0.0.0.0',int(sys.argv[1]) if len(sys.argv)>1 else 8799),H).serve_forever()
