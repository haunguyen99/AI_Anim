"""Đặt mức suy nghĩ mặc định của Claude = high trên máy này (Claude Code + Paseo).

    .venv/Scripts/python.exe -I tools/ai_effort_high.py          # đặt (có sao lưu .bak), chạy lại nhiều lần vẫn được
    .venv/Scripts/python.exe -I tools/ai_effort_high.py --check  # chỉ báo, không ghi

Vì sao: mức "medium" làm Claude nghĩ ngắn, việc rig / pose / tool dễ hời hợt (2026-11-13).
- ~/.claude/settings.json : effortLevel = high (+ modelSettings.claude-opus.effortLevel)
- ~/.paseo/config.json    : mỗi model opus / sonnet của provider llmpro có thinkingOptions low…max, mặc định high
Không đọc / in key.
"""
import json, pathlib, shutil, sys, time

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

LEVELS = [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("xhigh", "Extra high"), ("max", "Max")]
DEFAULT = "high"


def _save(path, data, check):
    if check:
        return
    shutil.copy2(path, f"{path}.bak.{time.strftime('%Y%m%d_%H%M%S')}")
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def claude_code(check):
    p = pathlib.Path.home() / ".claude/settings.json"
    if not p.exists():
        return "Claude Code: chưa có settings.json (chạy tools/setup_vscode.ps1 trước)"
    d = json.loads(p.read_text(encoding="utf-8-sig"))
    ms = d.setdefault("modelSettings", {}).setdefault("claude-opus", {})
    if d.get("effortLevel") == DEFAULT and ms.get("effortLevel") == DEFAULT:
        return "Claude Code: đã là high"
    d["effortLevel"] = DEFAULT
    ms["effortLevel"] = DEFAULT
    _save(p, d, check)
    return "Claude Code: " + ("CHƯA high" if check else "đã đặt high")


def paseo(check):
    p = pathlib.Path.home() / ".paseo/config.json"
    if not p.exists():
        return "Paseo: chưa cài, bỏ qua"
    d = json.loads(p.read_text(encoding="utf-8-sig"))
    models = d.get("agents", {}).get("providers", {}).get("llmpro", {}).get("models", [])
    changed = 0
    for m in models:
        if "haiku" in m.get("id", ""):
            continue
        want = [{"id": i, "label": l, **({"isDefault": True} if i == DEFAULT else {})} for i, l in LEVELS]
        if m.get("thinkingOptions") != want:
            m["thinkingOptions"] = want
            changed += 1
    if not models:
        return "Paseo: chưa có provider llmpro, bỏ qua"
    if not changed:
        return "Paseo: đã là high"
    _save(p, d, check)
    return f"Paseo: {'CHƯA high' if check else 'đã đặt high'} ({changed} model); mở lại app Paseo hoặc chạy 'paseo reload'"


if __name__ == "__main__":
    check = "--check" in sys.argv
    print(claude_code(check))
    print(paseo(check))
