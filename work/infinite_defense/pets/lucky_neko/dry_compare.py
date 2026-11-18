# Is the current skin identical to what rig_skin.py would write? (detect hand edits before rebinding)
src = open(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\lucky_neko\rig_skin.py", encoding="utf-8").read()
real = api; diffs = []
import json
class Fake:
    cur = None
    def __getattr__(self, k): return getattr(real, k)
    def select(self, l): Fake.cur = l[0] if l else None; return real.select(l)
    def rotate(self, *a): pass
    def move(self, *a): pass
    def set_frame(self, *a): pass
    def bind_skin(self, *a): pass
    def unbind_skin(self, *a): pass
    def set_skin_weights(self, idx, rows):
        n = 0; pp = real.mesh_data(Fake.cur)["positions"]
        for v, r in zip(idx, rows):
            cur = dict(real.vertex_weights(v)); new = dict(r)
            if any(abs(cur.get(j, 0) - new.get(j, 0)) > 0.02 for j in set(cur) | set(new)):
                n += 1; diffs.append(int(v))
                if Fake.cur == 'Pet_lucky_neko': print(' ', v, [round(c, 3) for c in pp[3*v:3*v+3]], {j: round(w, 2) for j, w in cur.items()}, '->', {j: round(w, 2) for j, w in new.items()})
        if Fake.cur == 'Pet_lucky_neko': json.dump(diffs, open(r'C:\Users\Admin\AppData\Local\Temp\_lucky_user_ids.json', 'w'))
        print("compare", Fake.cur, "verts differing:", n, "of", len(idx))
exec(compile(src, "rig_skin", "exec"), {"api": Fake(), "__name__": "x"})
