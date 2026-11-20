"""Auto mix: build a Mix Lab recipe from a short brief (art lead 2026-11-02: "mix sẽ để thành auto").

  python -I auto_mix.py <brief.json | ->  [--project <Unity project, default cwd>] [--out <recipe.json>]

Reads component lengths from <project>/Docs/VFX/_ArtDirection/tools/mix_lab/mix_data.js (Unity MixCapture) and writes
<project>/Docs/VFX/_Recipes/<name>.json by default.

Brief (settle SPACE first, vfx-maker §1a; ask the art lead when context is unknown):
  {"name": "IceSlam_Ground",
   "context": "ground" | "air" | "dir",          # where the hit happens (required)
   "element": "fire" | "ice" | "poison" | "lightning" | "arcane" | "holy" | "physical",
   "weight":  "light" | "medium" | "heavy",      # how strong the blow reads
   "smoke":   "auto" | "none" | "dust" | "fire" | "fire2smoke",
   "mark":    "auto" | "none" | "scorch"}         # ground mark (ground only)

Rules (choreography from pixelfx + our component specs):
  - always: Impact flash (t 0) + Glow (t 0) + Sparks (t 0.02). Ring from medium up (t 0.03), echo ring on heavy (+0.1 s, 0.7x).
  - smoke: auto = none for light; fire element on the ground -> fire2smoke (explosion); otherwise dust of the context (t 0.05).
  - mark: auto = scorch (burn + cracks) on the ground for heavy or fire blows. Its heat colours follow the palette:
    MixRecipeBuild re-renders the codefx sheet with the recipe palette (art lead 2026-11-03).
  - weight: size light 0.8 / medium 1 / heavy 1.25 (ring 1.3); duration light x0.85 / heavy x1.15 (impact flash stays snappy).
  - air / dir hits sit at chest height (offset y 1.1).
Prints the recipe and the reason for every choice, so the art lead can ask for changes.
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MIX_DATA_REL = os.path.join("Docs", "VFX", "_ArtDirection", "tools", "mix_lab", "mix_data.js")
PROJECT = os.getcwd()
PALETTES = {
    "fire": dict(Core="#FFF3C4", Mid="#FF9A3C", Outer="#C8281E", Dust="#CDBBA6"),
    "ice": dict(Core="#F2FCFF", Mid="#7FD6FF", Outer="#2A6FD1", Dust="#C9D6DE"),
    "poison": dict(Core="#F4FFD6", Mid="#9BE04A", Outer="#2F8A2A", Dust="#A9B58E"),
    "lightning": dict(Core="#FFFBE0", Mid="#FFE24A", Outer="#C79200", Dust="#BDB7A0"),
    "arcane": dict(Core="#FBEFFF", Mid="#C77DFF", Outer="#6A1BB0", Dust="#B9AFC6"),
    "holy": dict(Core="#FFFFFF", Mid="#FFE7A3", Outer="#E0A93A", Dust="#E3DCCB"),
    "physical": dict(Core="#FFFFFF", Mid="#FFE2B0", Outer="#B07A4A", Dust="#CDBBA6"),
}
SIZE = {"light": 0.8, "medium": 1.0, "heavy": 1.25}
DURK = {"light": 0.85, "medium": 1.0, "heavy": 1.15}
CTXN = {"ground": "Ground", "air": "Air", "dir": "Dir"}
SMOKES = ("auto", "none", "dust", "fire", "fire2smoke")
MARKS = ("auto", "none", "scorch")


def check_brief(b):
    """Stop on unknown brief values instead of silently dropping layers."""
    if not isinstance(b, dict):
        sys.exit("Brief phải là một object JSON.")
    if b.get("context") not in CTXN:
        sys.exit("Thiếu / sai 'context' (ground | air | dir) — xác định không gian trước, hỏi art lead nếu chưa rõ.")
    bad = []
    for key, allowed, default in (("element", tuple(PALETTES), "fire"), ("weight", tuple(SIZE), "medium"),
                                  ("smoke", SMOKES, "auto"), ("mark", MARKS, "auto")):
        v = b.get(key, default)
        if v not in allowed:
            bad.append(f"  - '{key}': {json.dumps(v, ensure_ascii=False)} không hợp lệ, chọn một trong: {' | '.join(allowed)}")
    if bad:
        sys.exit("Brief có giá trị sai:\n" + "\n".join(bad))


def component_durations():
    """Base durations from the Mix Lab data (mix_data.js written by Unity MixCapture)."""
    path = os.path.join(PROJECT, MIX_DATA_REL)
    if not os.path.exists(path):
        path = os.path.join(HERE, "mix_data.js")          # copy living next to the script (project tools folder)
    t = open(path, encoding="utf-8").read()
    d = json.loads(t[t.index("{"):t.rindex("}") + 1])
    return {c["id"]: c["dur"] for c in d["comps"]}


def auto_mix(b):
    check_brief(b)
    ctx = b["context"]
    el = b.get("element", "fire")
    w = b.get("weight", "medium")
    C = CTXN[ctx]
    dur = component_durations()
    off = [0, 0, 0] if ctx == "ground" else [0, 1.1, 0]
    items, why = [], []

    def add(cid, delay, reason, size=None, dk=None, intensity=1.0):
        if cid not in dur:
            why.append(f"  ! bỏ {cid}: chưa có thành phần này")
            return
        items.append(dict(id=cid, delay=round(delay, 3), duration=round(dur[cid] * (DURK[w] if dk is None else dk), 3),
                          size=round(SIZE[w] if size is None else size, 3), intensity=intensity, rotation=0, offset=list(off)))
        why.append(f"  + {cid:<26} t {delay:.2f}s  {reason}")

    add(f"IMP_Hit_{C}_01", 0.0, "chớp trúng — frame hero, luôn có", dk=1.0)
    add(f"GLW_{C}_01", 0.0, "quầng sáng nền cho chớp — luôn có")
    add(f"SPK_{C}_01", 0.02, "tia lửa bắn ra ngay sau chớp — luôn có")
    if w != "light":
        add(f"RNG_{C}_01", 0.03, "vòng sóng cho đòn vừa / nặng", size=SIZE[w] * (1.04 if w == "heavy" else 1))
    if w == "heavy":
        add(f"RNG_{C}_01", 0.13, "vòng vọng (nhịp thứ 2) cho đòn nặng", size=SIZE[w] * 0.7, intensity=0.6)

    smoke = b.get("smoke", "auto")
    if smoke == "auto":
        smoke = "none" if w == "light" else ("fire2smoke" if el == "fire" and ctx == "ground" else "dust")
    if smoke == "fire2smoke" and ctx == "ground":
        add("DST_FireSmoke_Ground_01", 0.03, "lửa → khói (cú nổ) — nguyên tố lửa tại đất")
    elif smoke == "fire" and ctx == "ground":
        add("DST_Fire_Ground_01", 0.03, "cụm lửa — theo yêu cầu")
    elif smoke in ("dust", "fire", "fire2smoke"):
        add(f"DST_{C}_01", 0.05, "khói bụi sau va chạm" + (" (bản lửa chỉ có tại đất)" if smoke != "dust" else ""))
    else:
        why.append("  - không khói: đòn nhẹ" if w == "light" else "  - không khói: theo yêu cầu")

    mark = b.get("mark", "auto")
    if ctx == "ground" and (mark == "scorch" or (mark == "auto" and (w == "heavy" or el == "fire"))):
        add("SCR_Ground_01", 0.03, "vết cháy + nứt trên đất (phần nóng theo màu nguyên tố)" if el != "fire" else "vết cháy + nứt trên đất")

    # list front-most first (same as Mix Lab / AE); Unity draws by the ComponentKit sorting table anyway
    rank = {"IMP": 5, "SPK": 3, "RNG": 2, "GLW": 0, "DST": -2, "SCR": -7}
    items.sort(key=lambda it: -(-3 if it["id"] == "RNG_Ground_01" else rank.get(it["id"].split("_")[0], 0)))
    name = re.sub(r"[^A-Za-z0-9_]", "_", b.get("name") or f"{el.capitalize()}Hit_{C}")
    rec = dict(name=name, version=1, palette=PALETTES.get(el, PALETTES["fire"]), items=items)
    head = f"Auto mix {name}: {ctx} · {el} · {w}"
    return rec, head + "\n" + "\n".join(why)


def main():
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("brief")
    ap.add_argument("--out")
    ap.add_argument("--project", default=os.getcwd())
    a = ap.parse_args()
    global PROJECT
    PROJECT = os.path.abspath(a.project)
    b = json.load(sys.stdin if a.brief == "-" else open(a.brief, encoding="utf-8"))
    rec, report = auto_mix(b)
    print(report)
    out = a.out or os.path.join(PROJECT, "Docs", "VFX", "_Recipes", rec["name"] + ".json")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=2)
    print("→", os.path.normpath(out))


if __name__ == "__main__":
    main()
