"""Vòng khuỷu cứng (Ninja 2026-10-29, ghi chú vẽ khoanh khuỷu trái gập 90°: "đây này sửa lại skin weight").
Tay low-poly chỉ có một vòng đỉnh ở khuỷu: chia đôi vai/khuỷu thì gập 90° vòng đó co còn ~một nửa, đầu cẳng tay bị bóp như phễu.
Cách sửa: vòng khuỷu (t ∈ [-1, 4) cm dọc trục cánh tay tính từ khuỷu) đi gần hết theo khuỷu (mặc định 0,9),
vòng ngay phía trên (t ∈ [-6, -1)) chia một phần (0,3) để làm nếp gấp. Chỉ đổi tỉ lệ Shoulder/Elbow, xương khác giữ nguyên.
Số đo cạnh (lbs_test) xấu đi vì nếp gấp dồn vào một vòng, nhưng độ dày tay giữ được: kiểm bằng mắt (studio_cmd joint + snap).

    .venv/Scripts/python.exe -I -X utf8 work/rig_lab/elbow_ring.py <vòng trên> <vòng khuỷu> <ra.json>     # ví dụ 0.3 0.9
Đọc kho Ninja; ghi ra file, chép đè work/store/ninja_rig_lab/rig/skin.json khi đã duyệt (sao lưu trước), rồi nạp lại mọi trang Studio.
"""
import json, sys, collections, numpy as np
R = r"C:\Users\Admin\Documents\AI_animation"
up, mid, out = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
sk = json.load(open(R + r"\work\store\ninja_rig_lab\rig\skin.json")); names = sk["names"]
I = np.array(sk["I"]).reshape(-1, 4); W = np.array(sk["W"], float).reshape(-1, 4)
auto = json.load(open(R + r"\work\rig_lab\chars\ninja\landmarks_auto.json"))["landmarks"]
L = {k: np.array(v, float) for k, v in {**auto, **json.load(open(R + r"\work\store\ninja_rig_lab\rig\landmarks.json"))["lm"]}.items()}
CF = json.load(open(R + r"\work\rig_lab\chars\ninja.json", encoding="utf8"))
V = np.array(next(m for m in json.load(open(R + r"\work\store\ninja_mesh_lab\mesh\edit.json"))["meshes"] if m["name"] == CF["body"])["verts"]).reshape(-1, 3)
for s in "LR":
    Sh, El = L["Shoulder_" + s], L["Elbow_" + s]; du = (El - Sh) / np.linalg.norm(El - Sh)
    for i, p in enumerate(V):
        t = np.dot(p - El, du); r = np.linalg.norm(p - El - t * du)
        if r > 10 or t < -6 or t >= 4: continue
        cur = collections.Counter()
        for k in range(4):
            if W[i, k] > 0: cur[names[I[i, k]]] += W[i, k]
        ms = cur["Shoulder_" + s] + cur["Elbow_" + s]
        if ms < 0.3: continue
        w = up if t < -1 else mid
        cur["Shoulder_" + s] = ms * (1 - w); cur["Elbow_" + s] = ms * w
        top = [(b, x) for b, x in cur.most_common(4) if x > 0.01]; tot = sum(x for _, x in top)
        I[i] = [names.index(b) for b, _ in top] + [0] * (4 - len(top)); W[i] = [x / tot for _, x in top] + [0] * (4 - len(top))
sk["I"] = I.flatten().tolist(); sk["W"] = [round(float(x), 4) for x in W.flatten()]
json.dump(sk, open(out, "w"), separators=(",", ":"))
