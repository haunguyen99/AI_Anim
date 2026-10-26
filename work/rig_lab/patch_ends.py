# Joint *_End: HeadEnd_M (cfg.headEnd, đã có), ToesEnd_R/L khi rig không có Toes (cfg.toesEnd), <Ngón>FingerEnd_R/L ở đầu ngón (cfg.fingerEnd)
import os
R = os.path.dirname(os.path.abspath(__file__)); p = f"{R}/template.html"; s = open(p, encoding="utf8").read()
assert "toesEnd" not in s
def sub(old, new):
    global s
    assert s.count(old) == 1, old[:70]; s = s.replace(old, new)
sub("toes: true, dress: true,", "toes: true, toesEnd: false, fingerEnd: false, dress: true,")
sub('const SIDE_J = ["Scapula", "Shoulder", "Elbow", "Wrist", "Hip", "Knee", "Ankle", ...(CFG.toes ? ["Toes", "ToesEnd"] : [])];',
    'const SIDE_J = ["Scapula", "Shoulder", "Elbow", "Wrist", "Hip", "Knee", "Ankle", ...(CFG.toes ? ["Toes", "ToesEnd"] : CFG.toesEnd ? ["ToesEnd"] : [])];')
sub('const LEG_J = ["Hip", "Knee", "Ankle", ...(CFG.toes ? ["Toes", "ToesEnd"] : [])];',
    'const LEG_J = ["Hip", "Knee", "Ankle", ...(CFG.toes ? ["Toes", "ToesEnd"] : CFG.toesEnd ? ["ToesEnd"] : [])];')
sub('const FKEYS = FINGERS.flatMap(f => FSEG.map(i => f + "Finger" + i));',
    'const FKEYS = FINGERS.flatMap(f => [...FSEG.map(i => f + "Finger" + i), ...(CFG.fingerEnd ? [f + "FingerEnd"] : [])]);')
sub("const isFinger = k => /Finger\d_/.test(k);", "const isFinger = k => /Finger(\d|End)_/.test(k);")
sub('for (const f of FINGERS) for (const i of FSEG) add(f + "Finger" + i + "_" + s, i > 1 ? f + "Finger" + (i - 1) + "_" + s : "Wrist_" + s, P(f + "Finger" + i + "_" + s));',
    'for (const f of FINGERS) { for (const i of FSEG) add(f + "Finger" + i + "_" + s, i > 1 ? f + "Finger" + (i - 1) + "_" + s : "Wrist_" + s, P(f + "Finger" + i + "_" + s));\n      if (CFG.fingerEnd) add(f + "FingerEnd_" + s, f + "Finger" + FSEG[FSEG.length - 1] + "_" + s, P(f + "FingerEnd_" + s)); }')
sub('if (force || !L[k]) L[k] = [w[0] + sg * o[0] * len, w[1] + o[1] * len, w[2] + o[2] * len]; });',
    'if (force || !L[k]) L[k] = [w[0] + sg * o[0] * len, w[1] + o[1] * len, w[2] + o[2] * len]; });\n    if (CFG.fingerEnd) for (const f of FINGERS) { const k = f + "FingerEnd_" + s; if (force || !L[k]) L[k] = f === "Middle" ? t.slice() : [t[0], t[1] - 0.2 * len, t[2]]; }')
sub('extra = [...mine].filter(n => !refNames.has(n) && !/Twist\d/.test(n));', 'extra = [...mine].filter(n => !refNames.has(n) && !/Twist\d/.test(n) && !/End_/.test(n));')
sub('if (CFG.toes) { const ground = Math.min(idx.ToesEnd_R.pos[1], idx.ToesEnd_L.pos[1]);', 'if (CFG.toes || CFG.toesEnd) { const ground = Math.min(idx.ToesEnd_R.pos[1], idx.ToesEnd_L.pos[1]);')
sub('front = CFG.toes ? LM.ToesEnd_R[2] > LM.Ankle_R[2] : footFront(),', 'front = CFG.toes || CFG.toesEnd ? LM.ToesEnd_R[2] > LM.Ankle_R[2] : footFront(),')
open(p, "w", encoding="utf8").write(s); print("ok")
