import cv2, sys
D, x0, y0, x1, y1 = sys.argv[1], *map(int, sys.argv[2:6]); s = float(sys.argv[6]); name = sys.argv[7]
step = int(sys.argv[8]) if len(sys.argv) > 8 else 20
im = cv2.imread(f"{D}/src/source.jpg")[y0:y1, x0:x1]
im = cv2.resize(im, None, fx=s, fy=s, interpolation=cv2.INTER_CUBIC)
for x in range((x0 // step + 1) * step, x1, step):
    X = int((x - x0) * s); big = x % (step*2) == 0
    cv2.line(im, (X, 0), (X, im.shape[0]), (0, 0, 255) if big else (255, 160, 0), 1)
    if big: cv2.putText(im, str(x), (X + 2, 12), cv2.FONT_HERSHEY_SIMPLEX, .42, (0, 0, 255), 1)
for y in range((y0 // step + 1) * step, y1, step):
    Y = int((y - y0) * s); big = y % (step*2) == 0
    cv2.line(im, (0, Y), (im.shape[1], Y), (0, 0, 255) if big else (255, 160, 0), 1)
    if big: cv2.putText(im, str(y), (2, Y - 2), cv2.FONT_HERSHEY_SIMPLEX, .42, (0, 0, 255), 1)
cv2.imwrite(f"{D}/preview/{name}.png", im)
