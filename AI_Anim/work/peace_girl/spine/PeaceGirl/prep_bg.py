import cv2, numpy as np, sys
D = sys.argv[1]
im = cv2.imread(f"{D}/src/source.jpg")
h, w = im.shape[:2]
print(w, h, "corner colors", im[2,2], im[2,-3], im[-3,2], im[-3,-3])
# nền xám sáng: loang từ viền, ngưỡng theo khoảng cách màu tới nền
bg = np.median(np.concatenate([im[:6].reshape(-1,3), im[:, :6].reshape(-1,3), im[:, -6:].reshape(-1,3)]), axis=0)
print("bg", bg)
d = np.abs(im.astype(int) - bg).max(axis=2)
cand = (d < 24).astype(np.uint8)
n, lab = cv2.connectedComponents(cand, connectivity=4)
border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:,0], lab[:,-1]])))
border.discard(0)
bgm = np.isin(lab, list(border))
fg = (~bgm).astype(np.uint8)*255
fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((3,3),np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(fg)
big = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])
fg = ((lab == big)*255).astype(np.uint8)
# túi nền kẹt giữa cổ / tóc / ngón tay (không nối với viền ảnh): bỏ mảng màu nền >= 15 px
# trừ vệt sáng nằm trong tóc (vòng quanh toàn tóc tím)
hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
hair = ((hsv[..., 0] >= 118) & (hsv[..., 0] <= 152) & (hsv[..., 1] >= 70)) | (hsv[..., 2] < 60)
pk = ((d < 14) & (fg > 0)).astype(np.uint8)
n2, lab2, st2, cen2 = cv2.connectedComponentsWithStats(pk, connectivity=4)
for i in range(1, n2):
    if st2[i, cv2.CC_STAT_AREA] < 15:
        continue
    cm = (lab2 == i).astype(np.uint8)
    ring = (cv2.dilate(cm, np.ones((7, 7), np.uint8)) > 0) & (cm == 0)
    frac = hair[ring].mean()
    print("túi", i, "area", st2[i, cv2.CC_STAT_AREA], "tâm", cen2[i].astype(int), "tóc quanh %.2f" % frac)
    if frac < 0.5:
        fg[lab2 == i] = 0
cv2.imwrite(f"{D}/src/fg_mask.png", fg)
print("fg area", (fg>0).sum(), "bbox", st[big,:4])
# lưới toạ độ để xem
g = im.copy()
for x in range(0, w, 50):
    cv2.line(g, (x,0), (x,h), (0,0,255) if x%100==0 else (255,160,0), 1)
    if x%100==0: cv2.putText(g, str(x), (x+2, 12), cv2.FONT_HERSHEY_SIMPLEX, .4, (0,0,255), 1)
for y in range(0, h, 50):
    cv2.line(g, (0,y), (w,y), (0,0,255) if y%100==0 else (255,160,0), 1)
    if y%100==0: cv2.putText(g, str(y), (2, y-2), cv2.FONT_HERSHEY_SIMPLEX, .4, (0,0,255), 1)
cv2.imwrite(f"{D}/preview/grid.png", g)
