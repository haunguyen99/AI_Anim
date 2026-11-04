"""Đường dẫn trong Unity G-DieLoop (Shoot Die Repeat, E:\\Horus\\shot-die-repeat) theo map.

2026-11-03 Tùng đổi tên folder map từ số sang tên riêng (commit a28ec191 trên Dev/TungNV):
Map01 → Jungle, Map02 → Roma, Map03 → Mayah, Map04 → Pirate, Map05 → Western, Map06 → London
(cả Animations/MapNN, 3D/Model/MAPn, Prefabs/Actors/Map n, 2D/Gameplay/Maps/Map n).
Nhánh đang checkout có thể còn tên cũ hoặc đã có tên mới, nên tra folder nào đang có thật: tên mới trước, rồi các kiểu tên cũ.

    import sdr_paths as SP
    SP.anim(5, "MC_char_map5_shoot.fbx")     # .../Animations/Western/... (hoặc .../Animations/Map05/...)
    SP.anim("Western")                        # nhận cả số map lẫn tên
    SP.model(5, "MC_char_map5.fbx")           # .../3D/Model/Western/...
    SP.git_path(5, "Animations", "X.fbx")     # đường dẫn tương đối trong repo theo tên MỚI (để đẩy lên nhánh đã đổi tên)
"""
import os

UNITY = r"E:\Horus\shot-die-repeat"
GAME = os.path.join(UNITY, "Assets", "_Game")
NAMES = {1: "Jungle", 2: "Roma", 3: "Mayah", 4: "Pirate", 5: "Western", 6: "London"}
_IDX = {v.lower(): k for k, v in NAMES.items()}

# thư mục gốc chứa các folder map (tương đối với Assets/_Game)
BASES = {
    "Animations": "Animations",
    "Model": os.path.join("3D", "Model"),
    "Actors": os.path.join("Prefabs", "Actors"),
    "Maps2D": os.path.join("2D", "Gameplay", "Maps"),
}


def idx(m):
    """Số map (1..6) từ số hoặc tên ('Western', 'map05', 5)."""
    if isinstance(m, int):
        return m
    s = str(m).strip().lower()
    if s in _IDX:
        return _IDX[s]
    return int("".join(c for c in s if c.isdigit()))


def name(m):
    return NAMES[idx(m)]


def _candidates(n):
    return [NAMES[n], f"Map{n:02d}", f"Map {n}", f"MAP{n}", f"map{n:02d}", f"Map{n}"]


def folder(base, m):
    """Folder map đang có thật trên ổ dưới Assets/_Game/<base>; không thấy thì trả tên mới."""
    root = os.path.join(GAME, BASES.get(base, base))
    n = idx(m)
    for c in _candidates(n):
        p = os.path.join(root, c)
        if os.path.isdir(p):
            return p
    return os.path.join(root, NAMES[n])


def anim(m, *rest):
    return os.path.join(folder("Animations", m), *rest)


def model(m, *rest):
    return os.path.join(folder("Model", m), *rest)


def actors(m, *rest):
    return os.path.join(folder("Actors", m), *rest)


def git_path(m, base="Animations", *rest, new=True):
    """Đường dẫn tương đối trong repo (dấu /). new=True: tên mới (Western); False: tên cũ MapNN (chỉ đúng cho Animations)."""
    n = idx(m)
    sub = NAMES[n] if new else f"Map{n:02d}"
    return "/".join(["Assets", "_Game", BASES.get(base, base).replace(os.sep, "/"), sub, *rest])


if __name__ == "__main__":
    for n in NAMES:
        print(n, NAMES[n], anim(n), os.path.isdir(anim(n)))
