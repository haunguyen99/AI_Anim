"""Small HorusChat Developer API client (stdlib only).

HorusChat = Matrix homeserver behind a Gateway with a Developer API (docs: in-app, Settings → API Keys).
Auth: `Authorization: Bearer <API_KEY>`. Config from env vars or tools/horuschat_mcp/.env:
  HORUSCHAT_BASE_URL, HORUSCHAT_API_KEY, HORUSCHAT_WATCH
"""
from __future__ import annotations

import http.client
import json
import os
import uuid
from pathlib import Path
from urllib import error, parse, request

PKG_DIR = Path(__file__).resolve().parent.parent
# Danh tính: AI_PROFILE (mặc định "ai") -> .env.<tên>; xem tools/identity.py
def _saved_profile():
    try:
        return (PKG_DIR.parent / ".profile").read_text(encoding="utf8").strip()
    except OSError:
        return ""


PROFILE = (os.environ.get("AI_PROFILE") or _saved_profile() or "ai").strip().lower() or "ai"
ENV_FILE = PKG_DIR / (".env." + PROFILE)
KEYS = ("HORUSCHAT_BASE_URL", "HORUSCHAT_API_KEY", "HORUSCHAT_WATCH")


def load_env() -> dict:
    cfg = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip().strip('"').strip("'")
    for k in KEYS:
        if os.environ.get(k):
            cfg[k] = os.environ[k]
    return cfg


class HCError(RuntimeError):
    def __init__(self, msg: str, status: int = 0, code: str = "", retry_after: float = 0):
        super().__init__(msg)
        self.status, self.code, self.retry_after = status, code, retry_after


def q(s: str) -> str:
    """URL-encode one path segment (room id '!abc:host', event id '$x:host', user id '@a:host')."""
    return parse.quote(s, safe="")


class HorusChat:
    def __init__(self, cfg: dict | None = None):
        cfg = cfg or load_env()
        self.url = (cfg.get("HORUSCHAT_BASE_URL") or "https://chat.horusjsc.com").rstrip("/")
        self.key = cfg.get("HORUSCHAT_API_KEY") or ""
        self.watch = [c.strip() for c in (cfg.get("HORUSCHAT_WATCH") or "").split(",") if c.strip()]
        self._rooms: list[dict] | None = None

    def check(self):
        if not self.key:
            raise HCError(f"Thiếu HORUSCHAT_API_KEY trong {ENV_FILE} (xem .env.example)")

    # ---------------- HTTP ----------------
    def call(self, method: str, path: str, params: dict | None = None, body: dict | None = None,
             idempotent: bool = False, timeout: float = 45, raw: bool = False):
        self.check()
        url = self.url + path
        if params:
            pairs = []
            for k, v in params.items():
                if v is None or v == "":
                    continue
                for item in (v if isinstance(v, (list, tuple)) else [v]):
                    pairs.append((k, str(item).lower() if isinstance(item, bool) else str(item)))
            if pairs:
                url += "?" + parse.urlencode(pairs)
        headers = {"Authorization": f"Bearer {self.key}", "Accept": "application/json",
                   "User-Agent": "horuschat-mcp/0.1"}
        data = None
        if body is not None:
            data = json.dumps(body, ensure_ascii=False).encode("utf8")
            headers["Content-Type"] = "application/json"
        if idempotent:
            headers["Idempotency-Key"] = uuid.uuid4().hex
        req = request.Request(url, data=data, headers=headers, method=method)
        try:
            with request.urlopen(req, timeout=timeout) as r:
                payload = r.read()
                if raw:
                    return payload, dict(r.headers)
        except error.HTTPError as e:
            text = e.read().decode("utf8", "replace")
            code, msg = "", text.strip()[:300]
            try:
                j = json.loads(text)
                code = j.get("code", "") or ""
                msg = j.get("error") or j.get("message") or msg
            except ValueError:
                pass
            ra = float(e.headers.get("Retry-After") or 0) if e.headers else 0
            raise HCError(f"HTTP {e.code} {code}: {msg}".strip(), e.code, code, ra) from None
        except error.URLError as e:
            raise HCError(f"Không kết nối được {self.url}: {e.reason}") from None
        except (OSError, http.client.HTTPException) as e:   # ngắt kết nối giữa chừng, timeout
            raise HCError(f"Mất kết nối {self.url}: {type(e).__name__} {e}") from None
        if not payload:
            return {}
        try:
            return json.loads(payload)
        except ValueError:
            return {"raw": payload.decode("utf8", "replace")[:500]}

    def get(self, path: str, **params):
        return self.call("GET", path, params=params)

    # ---------------- helpers ----------------
    def me(self) -> dict:
        return self.get("/v1/developer/me")

    def rooms(self, refresh: bool = False) -> list[dict]:
        if self._rooms is None or refresh:
            out, frm = [], None
            for _ in range(50):
                r = self.get("/v1/developer/rooms", limit=100, **({"from": frm} if frm else {}))
                out += r.get("rooms", [])
                frm = r.get("next_from")
                if not frm:
                    break
            self._rooms = out
        return self._rooms

    def room_id(self, room: str) -> str:
        """Accept '!roomid:host', '#alias:host', or (part of) a room name."""
        room = room.strip()
        if room.startswith("!"):
            return room
        rows = self.rooms()
        for refresh in (False, True):
            if refresh:
                rows = self.rooms(refresh=True)
            exact = [r for r in rows if room in (r.get("canonical_alias"), r.get("name"))]
            if exact:
                return exact[0]["room_id"]
            low = room.lower().lstrip("#")
            part = [r for r in rows if low in (r.get("name") or "").lower()
                    or low in (r.get("canonical_alias") or "").lower()]
            if len(part) == 1:
                return part[0]["room_id"]
            if len(part) > 1:
                names = ", ".join(f"{p.get('name')} ({p['room_id']})" for p in part[:10])
                raise HCError(f"Tên phòng '{room}' khớp nhiều phòng: {names}")
        raise HCError(f"Không thấy phòng '{room}' trong danh sách phòng đã tham gia")


def slim(ev: dict) -> dict:
    """Short form of one event for the model."""
    m = ev.get("message") or {}
    s = ev.get("sender") or {}
    out = {"event_id": ev.get("event_id"), "type": ev.get("type"), "room_id": ev.get("room_id"),
           "ts": ev.get("origin_ts"), "from": s.get("display_name") or s.get("user_id"),
           "user_id": s.get("user_id")}
    if s.get("is_bot"):
        out["bot"] = True
    if m:
        out["text"] = m.get("body")
        for k in ("thread_root_event_id", "reply_to_event_id"):
            if m.get(k):
                out[k.replace("_event_id", "")] = m[k]
        if m.get("attachments"):
            out["attachments"] = m["attachments"]
        mt = m.get("mentions") or {}
        if mt.get("user_ids") or mt.get("room"):
            out["mentions"] = mt
        if m.get("truncated"):
            out["truncated"] = True
    for k in ("reaction", "relates_to", "redacts", "edit", "invite"):
        if ev.get(k):
            out[k] = ev[k]
    rm = ev.get("room") or {}
    if rm.get("name"):
        out["room"] = rm["name"]
    return out
