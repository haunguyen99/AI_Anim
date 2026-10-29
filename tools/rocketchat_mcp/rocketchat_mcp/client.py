"""Small Rocket.Chat REST client (stdlib only). Shared by the MCP server and tools/rocketchat_watch.py.

Config comes from environment variables or tools/rocketchat_mcp/.env:
  ROCKETCHAT_URL, ROCKETCHAT_USER_ID, ROCKETCHAT_TOKEN (Personal Access Token), ROCKETCHAT_WATCH
"""
from __future__ import annotations

import json
import mimetypes
import os
import uuid
from pathlib import Path
from urllib import error, parse, request

PKG_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = PKG_DIR / ".env"


def load_env() -> dict:
    cfg = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip().strip('"').strip("'")
    for k in ("ROCKETCHAT_URL", "ROCKETCHAT_USER_ID", "ROCKETCHAT_TOKEN", "ROCKETCHAT_WATCH"):
        if os.environ.get(k):
            cfg[k] = os.environ[k]
    return cfg


class RCError(RuntimeError):
    pass


class RocketChat:
    def __init__(self, cfg: dict | None = None):
        cfg = cfg or load_env()
        self.url = (cfg.get("ROCKETCHAT_URL") or "").rstrip("/")
        self.uid = cfg.get("ROCKETCHAT_USER_ID") or ""
        self.token = cfg.get("ROCKETCHAT_TOKEN") or ""
        self.watch = [c.strip().lstrip("#") for c in (cfg.get("ROCKETCHAT_WATCH") or "").split(",") if c.strip()]
        self._room_cache: dict[str, dict] = {}

    def check(self):
        missing = [n for n, v in (("ROCKETCHAT_URL", self.url), ("ROCKETCHAT_USER_ID", self.uid),
                                  ("ROCKETCHAT_TOKEN", self.token)) if not v]
        if missing:
            raise RCError(f"Thiếu {', '.join(missing)} trong {ENV_FILE} (xem .env.example)")

    # ---------------- HTTP ----------------
    def _headers(self) -> dict:
        return {"X-User-Id": self.uid, "X-Auth-Token": self.token, "Accept": "application/json"}

    def _send(self, req: request.Request, timeout: float = 30) -> dict:
        try:
            with request.urlopen(req, timeout=timeout) as r:
                body = r.read()
        except error.HTTPError as e:
            body = e.read()
            try:
                msg = json.loads(body).get("error") or json.loads(body).get("message") or body[:300]
            except ValueError:
                msg = body[:300]
            raise RCError(f"HTTP {e.code} {req.full_url.split('?')[0]}: {msg}") from None
        except error.URLError as e:
            raise RCError(f"Không kết nối được {self.url}: {e.reason}") from None
        data = json.loads(body or b"{}")
        if isinstance(data, dict) and data.get("success") is False:
            raise RCError(data.get("error") or str(data))
        return data

    def get(self, path: str, **params) -> dict:
        self.check()
        q = parse.urlencode({k: v for k, v in params.items() if v is not None})
        req = request.Request(f"{self.url}/api/v1/{path}" + (f"?{q}" if q else ""), headers=self._headers())
        return self._send(req)

    def post(self, path: str, payload: dict) -> dict:
        self.check()
        h = self._headers() | {"Content-Type": "application/json"}
        req = request.Request(f"{self.url}/api/v1/{path}", data=json.dumps(payload).encode(), headers=h, method="POST")
        return self._send(req)

    def post_multipart(self, path: str, fields: dict, file_path: Path) -> dict:
        self.check()
        boundary = uuid.uuid4().hex
        parts = []
        for k, v in fields.items():
            if v is None:
                continue
            parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
        ctype = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        parts.append((f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{file_path.name}"\r\n'
                      f"Content-Type: {ctype}\r\n\r\n").encode() + file_path.read_bytes() + b"\r\n")
        parts.append(f"--{boundary}--\r\n".encode())
        h = self._headers() | {"Content-Type": f"multipart/form-data; boundary={boundary}"}
        req = request.Request(f"{self.url}/api/v1/{path}", data=b"".join(parts), headers=h, method="POST")
        return self._send(req, timeout=300)

    def download(self, url_path: str, out: Path) -> Path:
        self.check()
        full = url_path if url_path.startswith("http") else f"{self.url}{url_path}"
        req = request.Request(full, headers=self._headers())
        with request.urlopen(req, timeout=300) as r:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(r.read())
        return out

    # ---------------- rooms ----------------
    def room(self, name: str) -> dict:
        """Find a room by id, '#channel', 'channel' or '@username' (DM). Returns {_id, t, name}."""
        key = name.strip()
        if key in self._room_cache:
            return self._room_cache[key]
        if key.startswith("@"):
            r = self.post("im.create", {"username": key[1:]})["room"]
            info = {"_id": r.get("rid") or r["_id"], "t": "d", "name": key}
        else:
            bare = key.lstrip("#")
            try:
                r = self.get("rooms.info", roomName=bare)["room"]
            except RCError:
                r = self.get("rooms.info", roomId=bare)["room"]
            info = {"_id": r["_id"], "t": r.get("t", "c"), "name": r.get("fname") or r.get("name") or bare}
        self._room_cache[key] = info
        return info

    def history(self, name: str, count: int = 30, oldest: str | None = None) -> list[dict]:
        r = self.room(name)
        ep = {"c": "channels.history", "p": "groups.history", "d": "im.history"}.get(r["t"], "channels.history")
        return self.get(ep, roomId=r["_id"], count=count, oldest=oldest).get("messages", [])


def slim(m: dict) -> dict:
    """Short message dict for Claude to read."""
    out = {"id": m.get("_id"), "ts": m.get("ts"), "user": (m.get("u") or {}).get("username"),
           "text": m.get("msg", "")}
    if m.get("tmid"):
        out["thread"] = m["tmid"]
    if m.get("tcount"):
        out["replies"] = m["tcount"]
    files = m.get("files") or ([m["file"]] if m.get("file") else [])
    atts = []
    for a in m.get("attachments") or []:
        link = a.get("title_link") or a.get("image_url") or a.get("video_url")
        if link or a.get("text") or a.get("description"):
            atts.append({k: v for k, v in {"title": a.get("title"), "url": link,
                                           "text": a.get("text") or a.get("description")}.items() if v})
    if files:
        out["files"] = [{"id": f.get("_id"), "name": f.get("name"), "type": f.get("type")} for f in files]
    if atts:
        out["attachments"] = atts
    return out
