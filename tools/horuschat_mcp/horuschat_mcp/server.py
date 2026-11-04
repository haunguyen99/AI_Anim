"""HorusChat MCP server (Developer API of chat.horusjsc.com).

Tools: hc_me, hc_rooms, hc_room, hc_history, hc_event, hc_events, hc_users, hc_send, hc_dm,
hc_edit, hc_react, hc_delete, hc_download.
Rooms are given as room id ('!abc:host'), alias ('#name:host') or (part of) the room name.
Sending posts as the key owner: Claude asks the user in chat before every send/dm/edit/delete,
except replies the user pre-approved (see README).
"""
from __future__ import annotations

from pathlib import Path

from mcp.server.fastmcp import FastMCP

from .client import ENV_FILE, HCError, HorusChat, q, slim

mcp = FastMCP("horuschat")
hc = HorusChat()


def _err(e: Exception) -> dict:
    return {"error": str(e)}


def _events(r: dict) -> list:
    return r.get("events") or r.get("messages") or []


@mcp.tool()
def hc_me() -> dict:
    """Check the connection: who the API key acts as, its scopes, config file path."""
    try:
        return hc.me() | {"url": hc.url, "watch": hc.watch, "config": str(ENV_FILE)}
    except HCError as e:
        return _err(e) | {"url": hc.url, "config": str(ENV_FILE)}


@mcp.tool()
def hc_rooms(filter: str = "", limit: int = 200) -> dict:
    """List rooms the key owner has joined. filter: optional substring of name/alias."""
    try:
        rows = hc.rooms(refresh=True)
        if filter:
            f = filter.lower()
            rows = [r for r in rows if f in (r.get("name") or "").lower()
                    or f in (r.get("canonical_alias") or "").lower()]
        return {"rooms": [{k: r.get(k) for k in ("room_id", "name", "canonical_alias") if r.get(k)}
                          for r in rows[:limit]], "total": len(rows)}
    except HCError as e:
        return _err(e)


@mcp.tool()
def hc_room(room: str, members: bool = False) -> dict:
    """Room info (is_direct, encrypted, member_count, topic); members=True also lists members."""
    try:
        rid = hc.room_id(room)
        out = hc.get(f"/v1/developer/rooms/{q(rid)}")
        if members:
            out["members"] = hc.get(f"/v1/developer/rooms/{q(rid)}/members", limit=200).get("members", [])
        return out
    except HCError as e:
        return _err(e)


@mcp.tool()
def hc_history(room: str, limit: int = 30, thread_root_event_id: str = "", before: str = "") -> dict:
    """Read recent messages of a room (returned oldest first).
    thread_root_event_id: read one thread. before: 'next_before' from a previous call for older pages."""
    try:
        rid = hc.room_id(room)
        r = hc.get(f"/v1/developer/rooms/{q(rid)}/history", limit=max(1, min(limit, 100)),
                   before=before or None, thread_root_event_id=thread_root_event_id or None)
        evs = [slim(e) for e in _events(r)]
        evs.reverse()
        return {"room_id": rid, "messages": evs, "next_before": r.get("next_before")}
    except HCError as e:
        return _err(e)


@mcp.tool()
def hc_event(room: str, event_id: str) -> dict:
    """Read one event (message) by id."""
    try:
        rid = hc.room_id(room)
        return hc.get(f"/v1/developer/rooms/{q(rid)}/events/{q(event_id)}")
    except HCError as e:
        return _err(e)


@mcp.tool()
def hc_events(after: str = "now", wait: int = 0, rooms: list[str] | None = None,
              addressed_only: bool = False, include_own: bool = False, limit: int = 100) -> dict:
    """New events (messages, edits, reactions, redactions, invites) since a cursor.
    after: 'now' or next_cursor from the previous call. wait: long-poll seconds (0-30)."""
    try:
        rids = [hc.room_id(r) for r in (rooms or [])]
        r = hc.call("GET", "/v1/developer/events", params={
            "after": after, "wait": max(0, min(wait, 30)), "limit": limit, "room_id": rids,
            "addressed_only": addressed_only or None, "include_own": include_own or None},
            timeout=max(45, wait + 15))
        return {"events": [slim(e) for e in _events(r)], "next_cursor": r.get("next_cursor"),
                "has_more": r.get("has_more")}
    except HCError as e:
        return _err(e)


@mcp.tool()
def hc_users(query: str, limit: int = 20) -> dict:
    """Search users by name; returns Matrix user ids ('@name:host') for hc_dm / mentions."""
    try:
        return hc.get("/v1/developer/users", q=query, limit=limit)
    except HCError as e:
        return _err(e)


@mcp.tool()
def hc_send(room: str, body: str, thread_root_event_id: str = "", mentions: list[str] | None = None,
            markdown: bool = True, msgtype: str = "m.text") -> dict:
    """Post a message in a room (as the key owner). thread_root_event_id: reply inside that thread.
    mentions: Matrix user ids to notify. markdown: bold/italic/code/lists/links."""
    try:
        rid = hc.room_id(room)
        b = {"body": body, "msgtype": msgtype, "format": "markdown" if markdown else "plain"}
        if thread_root_event_id:
            b["thread_root_event_id"] = thread_root_event_id
        if mentions:
            b["mentions"] = mentions
        return hc.call("POST", f"/v1/developer/rooms/{q(rid)}/messages", body=b, idempotent=True) | {"room_id": rid}
    except HCError as e:
        return _err(e)


@mcp.tool()
def hc_dm(user_id: str, body: str) -> dict:
    """Send a direct message to one user ('@name:host'); creates the DM room if needed."""
    try:
        return hc.call("POST", "/v1/developer/messages",
                       body={"user_id": user_id, "body": body, "msgtype": "m.text"}, idempotent=True)
    except HCError as e:
        return _err(e)


@mcp.tool()
def hc_edit(room: str, event_id: str, body: str, markdown: bool = True) -> dict:
    """Edit a message the key owner sent."""
    try:
        rid = hc.room_id(room)
        return hc.call("PUT", f"/v1/developer/rooms/{q(rid)}/messages/{q(event_id)}",
                       body={"body": body, "format": "markdown" if markdown else "plain"}, idempotent=True)
    except HCError as e:
        return _err(e)


@mcp.tool()
def hc_react(room: str, event_id: str, key: str = "👀") -> dict:
    """Add a reaction (emoji) to a message."""
    try:
        rid = hc.room_id(room)
        return hc.call("POST", f"/v1/developer/rooms/{q(rid)}/messages/{q(event_id)}/reactions",
                       body={"key": key}, idempotent=True)
    except HCError as e:
        return _err(e)


@mcp.tool()
def hc_delete(room: str, event_id: str) -> dict:
    """Retract (redact) a message or reaction the key owner sent."""
    try:
        rid = hc.room_id(room)
        return hc.call("DELETE", f"/v1/developer/rooms/{q(rid)}/messages/{q(event_id)}", idempotent=True) or {"ok": True}
    except HCError as e:
        return _err(e)


@mcp.tool()
def hc_download(room: str, event_id: str, media_url: str, out_dir: str, filename: str = "") -> dict:
    """Download an attachment. media_url: 'mxc://server/mediaId' from the message's attachments."""
    try:
        rid = hc.room_id(room)
        if not media_url.startswith("mxc://"):
            raise HCError("media_url phải dạng mxc://server/mediaId")
        server, media = media_url[6:].split("/", 1)
        data, headers = hc.call("GET", f"/v1/developer/media/{q(server)}/{q(media)}",
                                params={"room_id": rid, "event_id": event_id}, raw=True, timeout=120)
        name = filename
        cd = headers.get("Content-Disposition") or headers.get("content-disposition") or ""
        if not name and "filename=" in cd:
            name = cd.split("filename=", 1)[1].strip('"; ')
        name = Path(name or media).name
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / name).write_bytes(data)
        return {"path": str(out / name), "bytes": len(data)}
    except HCError as e:
        return _err(e)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
