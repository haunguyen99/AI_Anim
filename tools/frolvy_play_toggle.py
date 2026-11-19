"""Phím tắt play / dừng cho Frolvy trên Linux (Mint, X11): bấm hộ nút Play trên thanh thời gian.

Frolvy chưa có lệnh Play/Pause để gán phím (chỉ có Space: giữ = play), nên script này tìm nút Play bằng màu
rồi click, xong trả chuột về chỗ cũ. Chỉ chạy khi cửa sổ đang focus là Frolvy (không thì báo, không click bậy).
Gán phím: tools/frolvy_play_toggle.py --install  (mặc định Alt+1);  gỡ: --uninstall.
Cần python3-xlib và Pillow (máy này có sẵn).
"""
import json, os, subprocess, sys, time

CACHE = os.path.expanduser("~/.cache/frolvy_play_toggle.json")
PLAY = (87, 143, 242)       # màu icon Play (tam giác xanh) của Frolvy 0.9.69
BTN_BG = (50, 57, 75)       # nền nút, dùng để kiểm lại vị trí đã nhớ khi icon đổi sang Pause
BINDING = "<Alt>1"
KB_PATH = "/org/cinnamon/desktop/keybindings/custom-keybindings/frolvy-play/"


def notify(msg):
    subprocess.run(["notify-send", "-t", "2500", "Frolvy Play", msg], check=False)


def active_window(d):
    from Xlib import X
    root = d.screen().root
    prop = root.get_full_property(d.intern_atom("_NET_ACTIVE_WINDOW"), X.AnyPropertyType)
    if not prop or not prop.value[0]:
        return None
    return d.create_resource_object("window", prop.value[0])


def window_title(w):
    try:
        return (w.get_wm_name() or "")
    except Exception:
        return ""


def window_origin(w, d):
    """Góc trên-trái của vùng nội dung cửa sổ so với màn hình (gồm cả đa màn hình)."""
    root = d.screen().root
    g = w.get_geometry()
    c = w.translate_coords(root, 0, 0)
    return -c.x, -c.y, g.width, g.height


def wait_alt_release(d, timeout=1.0):
    """Hotkey chạy lúc Alt còn đang giữ: đợi nhả Alt, không thì click thành Alt+click (xoay camera)."""
    from Xlib import XK
    codes = [d.keysym_to_keycode(XK.string_to_keysym(k)) for k in ("Alt_L", "Alt_R")]
    end = time.time() + timeout
    while time.time() < end:
        km = d.query_keymap()
        if not any(km[c // 8] & (1 << (c % 8)) for c in codes if c):
            return
        time.sleep(0.01)


def find_button(img, cached):
    pix = img.load()
    w, h = img.size
    xs, ys = [], []
    for y in range(h // 2, h):
        for x in range(w):
            if pix[x, y] == PLAY:
                xs.append(x); ys.append(y)
    if len(xs) >= 20:
        return (min(xs) + max(xs)) // 2, (min(ys) + max(ys)) // 2
    if cached:                       # đang Pause: icon khác màu, kiểm nền nút ở chỗ đã nhớ
        cx, cy = cached
        n = sum(1 for y in range(cy - 14, cy + 14) for x in range(cx - 14, cx + 14)
                if 0 <= x < w and 0 <= y < h and pix[x, y] == BTN_BG)
        if n > 150:
            return cx, cy
    return None


def toggle():
    from Xlib import X, display
    from Xlib.ext import xtest
    from PIL import ImageGrab
    d = display.Display()
    win = active_window(d)
    if win is None or "Frolvy" not in window_title(win):
        notify("Cửa sổ đang chọn không phải Frolvy")
        return 1
    ox, oy, w, h = window_origin(win, d)
    img = ImageGrab.grab(bbox=(ox, oy, ox + w, oy + h)).convert("RGB")
    key = f"{w}x{h}"
    cache = {}
    if os.path.exists(CACHE):
        try:
            cache = json.load(open(CACHE))
        except Exception:
            cache = {}
    pos = find_button(img, tuple(cache[key]) if key in cache else None)
    if not pos:
        notify("Không thấy nút Play (timeline bị ẩn hoặc bị che)")
        return 2
    cache[key] = list(pos)
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    json.dump(cache, open(CACHE, "w"))
    wait_alt_release(d)
    root = d.screen().root
    p = root.query_pointer()
    ax, ay = ox + pos[0], oy + pos[1]
    xtest.fake_input(d, X.MotionNotify, x=ax, y=ay); d.sync(); time.sleep(0.03)
    xtest.fake_input(d, X.ButtonPress, 1); d.sync(); time.sleep(0.03)
    xtest.fake_input(d, X.ButtonRelease, 1); d.sync(); time.sleep(0.03)
    xtest.fake_input(d, X.MotionNotify, x=p.root_x, y=p.root_y); d.sync()
    return 0


def gs(*a):
    return subprocess.run(["gsettings", *a], capture_output=True, text=True).stdout.strip()


def install(binding=BINDING):
    schema = "org.cinnamon.desktop.keybindings.custom-keybinding:" + KB_PATH
    gs("set", schema, "name", "Frolvy Play")
    gs("set", schema, "command", f"python3 -I {os.path.abspath(__file__)}")
    gs("set", schema, "binding", f"['{binding}']")
    lst = eval(gs("get", "org.cinnamon.desktop.keybindings", "custom-list").replace("@as ", "") or "[]")
    if "frolvy-play" not in lst:
        lst.append("frolvy-play")
        gs("set", "org.cinnamon.desktop.keybindings", "custom-list", str(lst))
    print("đã gán", binding)


def uninstall():
    lst = eval(gs("get", "org.cinnamon.desktop.keybindings", "custom-list").replace("@as ", "") or "[]")
    lst = [x for x in lst if x != "frolvy-play"]
    gs("set", "org.cinnamon.desktop.keybindings", "custom-list", str(lst))
    print("đã gỡ")


if __name__ == "__main__":
    if "--install" in sys.argv:
        i = sys.argv.index("--install")
        install(sys.argv[i + 1] if len(sys.argv) > i + 1 else BINDING)
    elif "--uninstall" in sys.argv:
        uninstall()
    else:
        sys.exit(toggle())
