import json, sys
from PIL import Image, ImageDraw
d = json.load(open(sys.argv[1])); out = sys.argv[2]
def col(w):
    s = {"w": 0, "e": 0, "h": 0}
    for j, x in w:
        if "Wing" in j: s["w"] += x
        elif "Ear" in j: s["e"] += x
        elif "Head" in j or "Jaw" in j: s["h"] += x
    return (int(255 * s["w"]), int(255 * s["e"]), int(255 * s["h"]))
S = 900
def draw(name, fx, fy, sc, ox, oy):
    im = Image.new("RGB", (S, S), (20, 20, 20)); dr = ImageDraw.Draw(im)
    for p, w in d:
        x = ox + fx(p) * sc; y = oy - fy(p) * sc; c = col(w)
        if c == (0, 0, 0): c = (110, 110, 110)
        dr.ellipse((x - 3, y - 3, x + 3, y + 3), fill=c)
    im.save(name)
draw(out + "_front.png", lambda p: p[0], lambda p: p[1], 850, 450, 800)
draw(out + "_side.png", lambda p: -p[2], lambda p: p[1], 850, 600, 800)
