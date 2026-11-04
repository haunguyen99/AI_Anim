"""Số liệu một phiên làm việc Claude cho /skillreport: lượt prompt, thời gian AI gen, thời gian người, ghi file Spine Live.

  python tools/report/session_stats.py find <từ khoá> [--days 14]
        # liệt kê log phiên (~/.claude/projects/<dự án>/*.jsonl) có từ khoá, kèm khoảng giờ có từ khoá
  python tools/report/session_stats.py stats --session <id|đường dẫn .jsonl> [--session ...]
        [--from "2026-11-02 16:40"] [--to "2026-11-03 09:00"] [--versions <json dự án>] [--gap 15] [--out <thư mục>]
        [--phases "1-4=Rig,5-10=Idle,11-15=Active,16=Xuất"]
        # in bảng từng lượt + tổng (+ tổng theo giai đoạn); --out ghi thêm stats.json + timeline.md

Quy tắc tính (giống 3 báo cáo cừu, giữ nguyên để các báo cáo so được với nhau):
- Lượt = một prompt của người (bỏ tool_result, task-notification, "[Request interrupted", tóm tắt nối phiên,
  tin nhắn chỉ có system-reminder). Prompt cách nhau < 5 s (ảnh dán kèm chữ) gộp làm một.
- AI gen = từ lúc gửi prompt tới tin nhắn cuối của AI trước prompt kế, TRỪ lúc chờ người trả lời AskUserQuestion.
- Người = khoảng từ lúc AI xong tới prompt kế, chỉ tính khi <= --gap phút (mặc định 15); dài hơn là nghỉ.
- Giờ in theo giờ máy (Việt Nam, +7). --from / --to cũng theo giờ máy.
- --versions: đường dẫn file JSON skeleton (vd work/test/spine/X/x.json); đọc sổ phiên bản Spine Live
  work/store/_sys/spine_live/versions/<đường dẫn thay / bằng __>/index.json: đếm lần ghi của claude / user trong khung giờ,
  gán mỗi bản vào lượt (trong lúc gen = của lượt đó; sau khi gen = người sửa trước prompt kế).
"""
import argparse, datetime as dt, glob, json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
PROJ = os.path.join(os.path.expanduser("~"), ".claude", "projects",
                    re.sub(r"[^A-Za-z0-9]", "-", ROOT.replace("\\", "/").replace("/", "-")))
TZ = dt.timezone(dt.timedelta(hours=7))
SKIP = ("<task-notification>", "[Request interrupted", "This session is being continued", "<command-name>",
        "<local-command", "Caveat:")


def ts(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(TZ)


def rel(p):
    try:
        return os.path.relpath(p, ROOT).replace("\\", "/")
    except ValueError:  # other drive (e.g. memory on C:, Unity project elsewhere)
        return p.replace("\\", "/")


def local(s):
    return dt.datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=TZ) if s else None


def session_path(s):
    if os.path.isfile(s):
        return s
    p = os.path.join(PROJ, s if s.endswith(".jsonl") else s + ".jsonl")
    if not os.path.isfile(p):
        sys.exit(f"không thấy log phiên {s} (tìm trong {PROJ})")
    return p


def text_of(content):
    if isinstance(content, str):
        return content, 0, False
    t, img, res = "", 0, False
    for b in content or []:
        k = b.get("type")
        if k == "text":
            t += b.get("text", "")
        elif k == "image":
            img += 1
        elif k == "tool_result":
            res = True
    return t, img, res


def clean(t):
    t = re.sub(r"<system-reminder>.*?</system-reminder>", "", t, flags=re.S)
    t = re.sub(r"<ide_[a-z_]+>.*?</ide_[a-z_]+>", "", t, flags=re.S)
    return t.strip()


def load(paths):
    ev = []
    for p in paths:
        for line in open(p, encoding="utf-8"):
            try:
                o = json.loads(line)
            except ValueError:
                continue
            if o.get("type") not in ("user", "assistant") or not o.get("timestamp"):
                continue
            ev.append(o)
    ev.sort(key=lambda o: o["timestamp"])
    return ev


def turns_of(ev, t0, t1):
    turns, asks = [], {}
    for o in ev:
        t = ts(o["timestamp"])
        if (t0 and t < t0) or (t1 and t > t1):
            continue
        m = o.get("message", {})
        c = m.get("content")
        if o["type"] == "user":
            txt, img, res = text_of(c)
            if res:   # câu trả lời AskUserQuestion: cộng thời gian chờ vào lượt
                for b in c:
                    if b.get("type") == "tool_result" and b.get("tool_use_id") in asks and turns:
                        turns[-1]["wait"] += (t - asks.pop(b["tool_use_id"])).total_seconds()
                continue
            txt = clean(txt)
            if o.get("isMeta") or o.get("isCompactSummary") or (not txt and not img) or txt.startswith(SKIP):
                continue
            if turns and (t - turns[-1]["start"]).total_seconds() < 5 and turns[-1]["n_ai"] == 0:
                turns[-1]["prompt"] = (turns[-1]["prompt"] + " " + txt).strip()
                turns[-1]["images"] += img
                continue
            turns.append({"start": t, "end": t, "prompt": txt, "images": img, "wait": 0.0, "n_ai": 0,
                          "tools": {}, "files": set(), "last_text": ""})
        elif turns:
            tr = turns[-1]
            tr["end"] = t
            tr["n_ai"] += 1
            for b in c or []:
                k = b.get("type")
                if k == "text" and b.get("text", "").strip():
                    tr["last_text"] = b["text"].strip()
                elif k == "tool_use":
                    name = b.get("name", "")
                    tr["tools"][name] = tr["tools"].get(name, 0) + 1
                    inp = b.get("input") or {}
                    if name in ("Write", "Edit") and inp.get("file_path"):
                        tr["files"].add(rel(inp["file_path"]))
                    if name == "AskUserQuestion":
                        asks[b.get("id")] = t
    return turns


def versions(js, t0, t1):
    key = js.replace("\\", "/").replace("/", "__")
    p = os.path.join(ROOT, "work", "store", "_sys", "spine_live", "versions", key, "index.json")
    if not os.path.isfile(p):
        sys.exit(f"không có sổ phiên bản {p}")
    out = []
    for e in json.load(open(p, encoding="utf-8")):
        t = dt.datetime.strptime(e["t"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=TZ)
        if (t0 and t < t0) or (t1 and t > t1):
            continue
        out.append({**e, "time": t})
    return out


def mmss(s):
    s = int(round(s))
    return f"{s // 3600}:{s // 60 % 60:02d}:{s % 60:02d}" if s >= 3600 else f"{s // 60}:{s % 60:02d}"


def cmd_find(a):
    since = dt.datetime.now(TZ) - dt.timedelta(days=a.days)
    kw = a.keyword.lower()
    for p in sorted(glob.glob(os.path.join(PROJ, "*.jsonl")), key=os.path.getmtime):
        if dt.datetime.fromtimestamp(os.path.getmtime(p), TZ) < since:
            continue
        hits, first, last = 0, None, None
        for line in open(p, encoding="utf-8"):
            if kw in line.lower():
                m = re.search(r'"timestamp":"([^"]+)"', line)
                if m:
                    t = ts(m.group(1)); hits += 1
                    first = first or t; last = t
        if hits:
            print(f"{os.path.basename(p)[:-6]}  {hits:4d} dòng  {first:%Y-%m-%d %H:%M} → {last:%Y-%m-%d %H:%M}")


def cmd_stats(a):
    t0, t1 = local(a.from_), local(a.to)
    turns = turns_of(load([session_path(s) for s in a.session]), t0, t1)
    if not turns:
        sys.exit("không có lượt prompt nào trong khung giờ")
    vers = versions(a.versions, t0 or turns[0]["start"] - dt.timedelta(minutes=10),
                    t1 or turns[-1]["end"] + dt.timedelta(minutes=30)) if a.versions else []
    gap = a.gap * 60
    tot = {"gen": 0.0, "wait": 0.0, "human": 0.0, "breaks": []}
    rows = []
    for i, tr in enumerate(turns):
        nxt = turns[i + 1]["start"] if i + 1 < len(turns) else None
        gen = max(0.0, (tr["end"] - tr["start"]).total_seconds() - tr["wait"])
        after = (nxt - tr["end"]).total_seconds() if nxt else 0.0
        human = after if after <= gap else 0.0
        if after > gap:
            tot["breaks"].append(f"{tr['end']:%m-%d %H:%M} → {nxt:%m-%d %H:%M} ({mmss(after)})")
        tot["gen"] += gen; tot["wait"] += tr["wait"]; tot["human"] += human
        in_gen = [v for v in vers if tr["start"] <= v["time"] <= tr["end"] + dt.timedelta(seconds=5)]
        between = [v for v in vers if tr["end"] + dt.timedelta(seconds=5) < v["time"] < (nxt or tr["end"] + dt.timedelta(minutes=30))]
        rows.append({
            "n": i + 1, "start": f"{tr['start']:%Y-%m-%d %H:%M:%S}", "end": f"{tr['end']:%H:%M:%S}",
            "gen_s": round(gen), "wait_s": round(tr["wait"]), "human_after_s": round(human), "break_after": after > gap,
            "images": tr["images"], "prompt": tr["prompt"][:600], "ai_last": tr["last_text"][:600],
            "tools": tr["tools"], "files": sorted(tr["files"]),
            "versions_ai": [f"#{v['id']} {v['time']:%H:%M:%S} {v['what']}" for v in in_gen if v["who"] == "claude"],
            "versions_user": [f"#{v['id']} {v['time']:%H:%M:%S} {v['what']}" for v in between if v["who"] == "user"],
        })
    n_ai = sum(1 for v in vers if v["who"] == "claude"); n_user = sum(1 for v in vers if v["who"] == "user")
    summary = {
        "turns": len(turns), "first": rows[0]["start"], "last": f"{turns[-1]['end']:%Y-%m-%d %H:%M:%S}",
        "gen": mmss(tot["gen"]), "gen_min": round(tot["gen"] / 60, 1),
        "human": mmss(tot["human"]), "human_min": round(tot["human"] / 60, 1),
        "answer_wait": mmss(tot["wait"]), "present": mmss(tot["gen"] + tot["human"] + tot["wait"]),
        "breaks": tot["breaks"], "versions_ai": n_ai, "versions_user": n_user,
    }
    for r in rows:
        print(f"\n#{r['n']:2d} {r['start'][5:16]}  gen {mmss(r['gen_s'])}" + (f" (chờ trả lời {mmss(r['wait_s'])})" if r["wait_s"] else "")
              + f"  người {mmss(r['human_after_s'])}" + ("  [NGHỈ sau lượt]" if r["break_after"] else "")
              + (f"  ảnh {r['images']}" if r["images"] else ""))
        print("   prompt:", r["prompt"][:300].replace("\n", " "))
        print("   AI    :", r["ai_last"][:240].replace("\n", " "))
        if r["versions_ai"]:
            print(f"   Spine Live AI ghi {len(r['versions_ai'])}: " + "; ".join(r["versions_ai"][-3:]))
        if r["versions_user"]:
            print(f"   Spine Live NGƯỜI ghi {len(r['versions_user'])}: " + "; ".join(r["versions_user"][:4])
                  + (" …" if len(r["versions_user"]) > 4 else ""))
    phases = []
    if a.phases:   # "1-4=Rig,5-10=Idle,11=Khác" -> tổng theo giai đoạn
        for part in a.phases.split(","):
            rng, name = part.split("=", 1)
            lo, _, hi = rng.partition("-")
            sel = [r for r in rows if int(lo) <= r["n"] <= int(hi or lo)]
            phases.append({"phase": name.strip(), "turns": len(sel), "gen_min": round(sum(r["gen_s"] for r in sel) / 60, 1),
                           "human_min": round(sum(r["human_after_s"] for r in sel) / 60, 1),
                           "ai_writes": sum(len(r["versions_ai"]) for r in sel),
                           "user_writes": sum(len(r["versions_user"]) for r in sel)})
        summary["phases"] = phases
    print("\n== TỔNG ==")
    for k, v in summary.items():
        if k != "phases":
            print(f"  {k}: {v}")
    for p in phases:
        print(f"  [{p['phase']}] {p['turns']} lượt · AI gen {p['gen_min']}′ · người {p['human_min']}′ · "
              f"Spine Live AI {p['ai_writes']} / người {p['user_writes']}")
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        json.dump({"summary": summary, "turns": rows}, open(os.path.join(a.out, "stats.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        with open(os.path.join(a.out, "timeline.md"), "w", encoding="utf-8") as f:
            f.write("| # | Giờ | Prompt | AI gen | Người sau lượt | Spine Live AI / người |\n|---|---|---|---|---|---|\n")
            for r in rows:
                p = r["prompt"][:120].replace("|", "/").replace("\n", " ")
                f.write(f"| {r['n']} | {r['start'][5:16]} | {p} | {mmss(r['gen_s'])} | "
                        f"{mmss(r['human_after_s'])}{' (nghỉ)' if r['break_after'] else ''} | {len(r['versions_ai'])} / {len(r['versions_user'])} |\n")
        print("ghi", os.path.join(a.out, "stats.json"), "+ timeline.md")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("find"); f.add_argument("keyword"); f.add_argument("--days", type=int, default=14)
    s = sub.add_parser("stats")
    s.add_argument("--session", action="append", required=True)
    s.add_argument("--from", dest="from_"); s.add_argument("--to")
    s.add_argument("--versions"); s.add_argument("--gap", type=float, default=15); s.add_argument("--out")
    s.add_argument("--phases", help='gán lượt vào giai đoạn: "1-4=Rig,5-10=Idle,11=Khác,12-16=Active,17=Xuất"')
    a = ap.parse_args()
    cmd_find(a) if a.cmd == "find" else cmd_stats(a)


if __name__ == "__main__":
    main()
