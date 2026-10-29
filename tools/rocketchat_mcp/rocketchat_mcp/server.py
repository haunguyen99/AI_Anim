"""Rocket.Chat MCP server.

Tools: rc_me, rc_rooms, rc_history, rc_thread, rc_search, rc_unread, rc_send, rc_upload, rc_download.
Rooms are named '#channel', 'channel', '@username' (DM) or by room id.
Sending posts as the token owner: Claude asks the user in chat before every rc_send / rc_upload.
"""
from __future__ import annotations

from pathlib import Path

from mcp.server.fastmcp import FastMCP

from .client import ENV_FILE, RCError, RocketChat, slim

mcp = FastMCP("rocketchat")
rc = RocketChat()


def _err(e: Exception) -> dict:
    return {"error": str(e)}


@mcp.tool()
def rc_me() -> dict:
    """Check the connection: server URL, logged-in user, config file path."""
    try:
        me = rc.get("me")
        return {"url": rc.url, "username": me.get("username"), "name": me.get("name"),
                "status": me.get("status"), "watch": rc.watch, "config": str(ENV_FILE)}
    except RCError as e:
        return _err(e) | {"config": str(ENV_FILE)}


@mcp.tool()
def rc_rooms(filter: str = "", limit: int = 100) -> dict:
    """List rooms the user is in (channels, private groups, DMs) with unread counts.
    filter: optional substring of the room name."""
    try:
        subs = rc.get("subscriptions.get").get("update", [])
        rows = []
        for s in subs:
            name = s.get("fname") or s.get("name") or ""
            if filter and filter.lower() not in name.lower():
                continue
            rows.append({"name": ("@" if s.get("t") == "d" else "#") + (s.get("name") or name),
                         "title": name, "id": s.get("rid"), "type": s.get("t"),
                         "unread": s.get("unread", 0), "mentions": s.get("userMentions", 0)})
        rows.sort(key=lambda r: (-r["mentions"], -r["unread"], r["title"].lower()))
        return {"rooms": rows[:limit], "total": len(rows)}
    except RCError as e:
        return _err(e)


@mcp.tool()
def rc_history(room: str, count: int = 30, oldest: str | None = None) -> dict:
    """Read the latest messages of a room, oldest first.
    room: '#channel', '@username', or room id. oldest: ISO date to read only newer messages."""
    try:
        msgs = rc.history(room, count=count, oldest=oldest)
        return {"room": rc.room(room)["name"], "messages": [slim(m) for m in reversed(msgs)]}
    except RCError as e:
        return _err(e)


@mcp.tool()
def rc_thread(message_id: str, count: int = 50) -> dict:
    """Read the replies of a thread (message_id = the thread's first message id)."""
    try:
        msgs = rc.get("chat.getThreadMessages", tmid=message_id, count=count).get("messages", [])
        return {"thread": message_id, "messages": [slim(m) for m in msgs]}
    except RCError as e:
        return _err(e)


@mcp.tool()
def rc_search(room: str, text: str, count: int = 20) -> dict:
    """Search messages in a room by text."""
    try:
        r = rc.room(room)
        msgs = rc.get("chat.search", roomId=r["_id"], searchText=text, count=count).get("messages", [])
        return {"room": r["name"], "messages": [slim(m) for m in msgs]}
    except RCError as e:
        return _err(e)


@mcp.tool()
def rc_unread(limit_per_room: int = 20) -> dict:
    """Unread messages in every room that has some (does not mark them read)."""
    try:
        out = []
        for s in rc.get("subscriptions.get").get("update", []):
            n = s.get("unread", 0)
            if not n:
                continue
            name = ("@" if s.get("t") == "d" else "#") + (s.get("name") or "")
            rc._room_cache[name] = {"_id": s["rid"], "t": s.get("t", "c"), "name": name}
            msgs = rc.history(name, count=min(n, limit_per_room))
            out.append({"room": name, "unread": n, "messages": [slim(m) for m in reversed(msgs)]})
        return {"rooms": out}
    except RCError as e:
        return _err(e)


@mcp.tool()
def rc_send(room: str, text: str, thread_id: str | None = None) -> dict:
    """Send a message as the token owner. ASK THE USER IN CHAT BEFORE CALLING (show room + exact text).
    room: '#channel', '@username' or room id. thread_id: reply inside a thread."""
    try:
        r = rc.room(room)
        msg = {"rid": r["_id"], "msg": text}
        if thread_id:
            msg["tmid"] = thread_id
        m = rc.post("chat.sendMessage", {"message": msg})["message"]
        return {"sent": True, "room": r["name"], "id": m.get("_id"), "ts": m.get("ts")}
    except RCError as e:
        return _err(e)


@mcp.tool()
def rc_upload(room: str, file_path: str, message: str = "", thread_id: str | None = None) -> dict:
    """Upload a file (playblast, image, FBX...) to a room with an optional message.
    ASK THE USER IN CHAT BEFORE CALLING (room, file, message)."""
    p = Path(file_path).expanduser().resolve()
    if not p.is_file():
        return {"error": f"Không thấy file {p}"}
    try:
        r = rc.room(room)
        try:   # Rocket.Chat 6.8+: rooms.media then rooms.mediaConfirm
            up = rc.post_multipart(f"rooms.media/{r['_id']}", {}, p)
            fid = up["file"]["_id"]
            rc.post(f"rooms.mediaConfirm/{r['_id']}/{fid}", {"msg": message, "tmid": thread_id} if thread_id
                    else {"msg": message})
        except RCError as e:
            if "404" not in str(e) and "not found" not in str(e).lower():
                raise
            rc.post_multipart(f"rooms.upload/{r['_id']}", {"msg": message, "tmid": thread_id}, p)
        return {"sent": True, "room": r["name"], "file": p.name, "bytes": p.stat().st_size}
    except RCError as e:
        return _err(e)


@mcp.tool()
def rc_download(url: str, out_path: str) -> dict:
    """Download a file attached to a message (url from rc_history attachments, e.g. /file-upload/...)."""
    try:
        p = rc.download(url, Path(out_path).expanduser().resolve())
        return {"saved": str(p), "bytes": p.stat().st_size}
    except (RCError, OSError) as e:
        return _err(e)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
