"""Tham số anim chỉnh được trên Spine Live (2026-10-31).

Tự đánh giá Spine Live: sửa nhỏ ("nhắm mắt từ F20", "ô cao thêm chút") phải qua Claude sửa script rồi dựng lại, trong khi
kéo key trong Spine chỉ mất vài giây. Ở đây script dựng anim khai báo tham số; Spine Live hiện thanh trượt (mục "Tham số
anim"), người dùng kéo -> server ghi giá trị rồi chạy lại script -> anim cập nhật ngay (Hoàn tác được).

Dùng trong script dựng anim:
    sys.path.insert(0, <gốc dự án>/tools/spine); from anim_params import Params
    P = Params(<thư mục skeleton>, "active", "Active", anim="active", run=["active/build_active.py"])
    H = P.num("rise", 70, 0, 200, 1, "Ô bay lên cao (px)")
    ...
    P.save()   # ghi định nghĩa vào <thư mục skeleton>/params.json, giữ giá trị người dùng đã chỉnh
anim="*": nhóm hiện ở mọi anim (vd physics dùng chung). run: script (tính từ thư mục skeleton) chạy lại khi đổi nhóm này,
theo thứ tự (vd đổi idle thì dựng lại idle rồi active vì active nối từ idle).
"""
import json, os

FILE = "params.json"


class Params:
    def __init__(self, folder, group, label, anim, run):
        self.path = os.path.join(os.path.abspath(folder), FILE)
        self.group, self.label, self.anim, self.run = group, label, anim, list(run)
        self.defs = []
        try:
            self.data = json.load(open(self.path, encoding="utf-8"))
        except (OSError, ValueError):
            self.data = {}
        self.values = ((self.data.get("groups") or {}).get(group) or {}).get("values") or {}

    def num(self, key, default, lo, hi, step=1, label="", unit=""):
        self.defs.append({"key": key, "label": label or key, "default": default, "min": lo, "max": hi, "step": step, "unit": unit})
        v = self.values.get(key, default)
        try:
            v = float(v)
        except (TypeError, ValueError):
            v = default
        v = min(hi, max(lo, v))
        return int(round(v)) if isinstance(default, int) and float(step).is_integer() else v

    def save(self):
        g = self.data.setdefault("groups", {})
        cur = g.get(self.group) or {}
        keys = {d["key"] for d in self.defs}
        g[self.group] = {"label": self.label, "anim": self.anim, "run": self.run, "defs": self.defs,
                         "values": {k: v for k, v in (cur.get("values") or {}).items() if k in keys}}
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(self.data, fh, ensure_ascii=False, indent=1)
        os.replace(tmp, self.path)
