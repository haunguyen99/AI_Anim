/* Pose Lab -> animation-only binary FBX 7.4 (Armature + skeleton, Lcl T / R(XYZ euler) / S curves, no meshes).
   JS port of fbxbin.py + fbxwrite.py (same output). Usage:
     const bytes = PoseLabFBX.build({ take, bones: [{name, parent}], worlds: [Float64Array(nb*16) per frame] });
   bones: skeleton in parent-first order, root bone first with parent -1 (it hangs under the 'Armature' null node).
   worlds[f][b*16..] = three.js matrixWorld.elements (column-major, meters, may carry a uniform scale from ancestors).
   FBX bone world = [R (unit scale) | 100 * t]  (calibrated against Blender's own FBX of the same rig). */
(function (root) {
  const DT = 1539538600; // ticks per frame at 30 fps
  const enc = new TextEncoder();
  const SENT = new Uint8Array(13);
  const E = (id, props, kids) => ({ id, props: props || [], kids: kids || [] });

  function encProp(t, v) {
    if (t === "S" || t === "R") {
      const b = t === "S" ? enc.encode(v) : v;
      const o = new Uint8Array(5 + b.length); o[0] = t.charCodeAt(0);
      new DataView(o.buffer).setUint32(1, b.length, true); o.set(b, 5); return o;
    }
    if (t === "C") return Uint8Array.of(67, v.charCodeAt(0));
    if (t === "I") { const o = new Uint8Array(5); o[0] = 73; new DataView(o.buffer).setInt32(1, v, true); return o; }
    if (t === "L") { const o = new Uint8Array(9); o[0] = 76; new DataView(o.buffer).setBigInt64(1, BigInt(v), true); return o; }
    if (t === "D") { const o = new Uint8Array(9); o[0] = 68; new DataView(o.buffer).setFloat64(1, v, true); return o; }
    const sz = { i: 4, l: 8, f: 4, d: 8 }[t];
    const o = new Uint8Array(13 + v.length * sz); o[0] = t.charCodeAt(0);
    const dv = new DataView(o.buffer); dv.setUint32(1, v.length, true); dv.setUint32(5, 0, true); dv.setUint32(9, v.length * sz, true);
    for (let i = 0; i < v.length; i++) {
      const p = 13 + i * sz;
      if (t === "i") dv.setInt32(p, v[i], true);
      else if (t === "l") dv.setBigInt64(p, BigInt(v[i]), true);
      else if (t === "f") dv.setFloat32(p, v[i], true);
      else dv.setFloat64(p, v[i], true);
    }
    return o;
  }

  function encElem(el, pos, isLast, out) {
    const pb = el.props.map(p => encProp(p[0], p[1]));
    const plen = pb.reduce((a, b) => a + b.length, 0);
    const idb = enc.encode(el.id);
    let p = pos + 12 + 1 + idb.length + plen;
    const sub = [];
    if (el.kids.length) {
      for (const k of el.kids) p = encElem(k, p, false, sub);
      sub.push(SENT); p += 13;
    } else if ((!el.props.length && !isLast) || el.id === "AnimationStack" || el.id === "AnimationLayer") {
      sub.push(SENT); p += 13;
    }
    const head = new Uint8Array(13 + idb.length);
    const dv = new DataView(head.buffer); dv.setUint32(0, p, true); dv.setUint32(4, el.props.length, true); dv.setUint32(8, plen, true);
    head[12] = idb.length; head.set(idb, 13);
    out.push(head); for (const b of pb) out.push(b); for (const s of sub) out.push(s);
    return p;
  }

  function serialize(top) {
    const HEAD = enc.encode("Kaydara FBX Binary  "); // 20 bytes
    const head = new Uint8Array(27); head.set(HEAD, 0); head[20] = 0; head[21] = 0x1a; head[22] = 0;
    new DataView(head.buffer).setUint32(23, 7400, true);
    const out = [head]; let pos = 27;
    top.forEach((el, i) => { const sub = []; pos = encElem(el, pos, i === top.length - 1, sub); for (const s of sub) out.push(s); });
    out.push(SENT); pos += 13;
    const fid = Uint8Array.of(0xfa, 0xbc, 0xab, 0x09, 0xd0, 0xc8, 0xd4, 0x66, 0xb1, 0x76, 0xfb, 0x83, 0x1c, 0xf7, 0x26, 0x7e, 0, 0, 0, 0);
    out.push(fid); pos += 20;
    let pad = ((pos + 15) & ~15) - pos; if (pad === 0) pad = 16;
    out.push(new Uint8Array(pad));
    const ver = new Uint8Array(4); new DataView(ver.buffer).setUint32(0, 7400, true); out.push(ver);
    out.push(new Uint8Array(120));
    out.push(Uint8Array.of(0xf8, 0x5a, 0x8c, 0x6a, 0xde, 0xf5, 0xd9, 0x7e, 0xec, 0xe9, 0x0c, 0xe3, 0x75, 0x8f, 0x29, 0x0b));
    let n = 0; for (const b of out) n += b.length;
    const res = new Uint8Array(n); let o = 0; for (const b of out) { res.set(b, o); o += b.length; }
    return res;
  }

  // 3x3 row-major rotation -> euler XYZ degrees (R = Rz*Ry*Rx), continuous with prev
  function eulerFrom(R, prev) {
    const r20 = R[6], ry = Math.asin(Math.max(-1, Math.min(1, -r20)));
    let rx, rz;
    if (Math.abs(r20) < 0.99999) { rx = Math.atan2(R[7], R[8]); rz = Math.atan2(R[3], R[0]); }
    else { rx = Math.atan2(-R[5], R[4]); rz = 0; }
    const D = 180 / Math.PI;
    const cands = [[rx * D, ry * D, rz * D], [(rx + Math.PI) * D, (Math.PI - ry) * D, (rz + Math.PI) * D]];
    let best = null;
    for (const e of cands) {
      const e2 = e.slice();
      if (prev) for (let i = 0; i < 3; i++) { while (e2[i] - prev[i] > 180) e2[i] -= 360; while (e2[i] - prev[i] < -180) e2[i] += 360; }
      const d = prev ? Math.abs(e2[0] - prev[0]) + Math.abs(e2[1] - prev[1]) + Math.abs(e2[2] - prev[2]) : 0;
      if (!best || d < best.d) best = { d, e: e2 };
    }
    return best.e;
  }

  // 4x4 row-major helpers (arrays of 16)
  function inv_rigid(m) { // inverse of [R|t] with R orthonormal
    const r = [m[0], m[4], m[8], m[1], m[5], m[9], m[2], m[6], m[10]];
    const t = [m[3], m[7], m[11]];
    const it = [-(r[0] * t[0] + r[1] * t[1] + r[2] * t[2]), -(r[3] * t[0] + r[4] * t[1] + r[5] * t[2]), -(r[6] * t[0] + r[7] * t[1] + r[8] * t[2])];
    return [r[0], r[1], r[2], it[0], r[3], r[4], r[5], it[1], r[6], r[7], r[8], it[2], 0, 0, 0, 1];
  }
  function mul(a, b) {
    const o = new Array(16).fill(0);
    for (let i = 0; i < 4; i++) for (let j = 0; j < 4; j++) { let s = 0; for (let k = 0; k < 4; k++) s += a[i * 4 + k] * b[k * 4 + j]; o[i * 4 + j] = s; }
    return o;
  }

  function build(opt) {
    const take = opt.take, bones = opt.bones, worlds = opt.worlds, nk = worlds.length;
    const names = ["Armature"].concat(bones.map(b => b.name));
    const parentName = names.map((n, i) => i === 0 ? null : (bones[i - 1].parent < 0 ? "Armature" : bones[bones[i - 1].parent].name));
    const nm = names.length;
    const T = names.map(() => []), Rr = names.map(() => []), prev = names.map(() => null);
    for (let k = 0; k < nk; k++) {
      const FW = [[1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]];
      for (let b = 0; b < bones.length; b++) {
        const e = worlds[k], o = b * 16;
        // three.js elements are column-major: element(row i, col j) = e[j*4+i]
        const s = Math.hypot(e[o + 0], e[o + 1], e[o + 2]);
        const m = [e[o + 0] / s, e[o + 4] / s, e[o + 8] / s, e[o + 12] * 100,
                   e[o + 1] / s, e[o + 5] / s, e[o + 9] / s, e[o + 13] * 100,
                   e[o + 2] / s, e[o + 6] / s, e[o + 10] / s, e[o + 14] * 100, 0, 0, 0, 1];
        FW.push(m);
      }
      for (let i = 0; i < nm; i++) {
        let loc;
        if (i === 0) loc = FW[0];
        else { const pi = bones[i - 1].parent < 0 ? 0 : bones[i - 1].parent + 1; loc = mul(inv_rigid(FW[pi]), FW[i]); }
        const R3 = [loc[0], loc[1], loc[2], loc[4], loc[5], loc[6], loc[8], loc[9], loc[10]];
        const e = eulerFrom(R3, prev[i]); prev[i] = e;
        T[i].push([loc[3], loc[7], loc[11]]); Rr[i].push(e);
      }
    }
    let nid = 1000; const nw = () => ++nid;
    const ids = names.map(nw), attr = names.map(nw), stack = nw(), layer = nw();
    const cnode = names.map(() => ({ T: nw(), R: nw(), S: nw() }));
    const curves = names.map(() => ({ T: [nw(), nw(), nw()], R: [nw(), nw(), nw()], S: [nw(), nw(), nw()] }));
    const times = []; for (let k = 0; k < nk; k++) times.push((k + 1) * DT);
    const t0 = times[0], t1 = times[nk - 1];
    const P = (name, typ, label, flags, ...vals) => E("P", [["S", name], ["S", typ], ["S", label], ["S", flags]].concat(vals));
    const top = [];
    top.push(E("FBXHeaderExtension", [], [E("FBXHeaderVersion", [["I", 1003]]), E("FBXVersion", [["I", 7400]]), E("EncryptionType", [["I", 0]]), E("Creator", [["S", "Pose Lab"]])]));
    const fid = new Uint8Array(16); for (let i = 0; i < 16; i++) fid[i] = i;
    top.push(E("FileId", [["R", fid]]));
    top.push(E("CreationTime", [["S", "1970-01-01 10:00:00:000"]]));
    top.push(E("Creator", [["S", "Pose Lab FBX"]]));
    const gs = [P("UpAxis", "int", "Integer", "", ["I", 1]), P("UpAxisSign", "int", "Integer", "", ["I", 1]),
      P("FrontAxis", "int", "Integer", "", ["I", 2]), P("FrontAxisSign", "int", "Integer", "", ["I", 1]),
      P("CoordAxis", "int", "Integer", "", ["I", 0]), P("CoordAxisSign", "int", "Integer", "", ["I", 1]),
      P("OriginalUpAxis", "int", "Integer", "", ["I", -1]), P("OriginalUpAxisSign", "int", "Integer", "", ["I", 1]),
      P("UnitScaleFactor", "double", "Number", "", ["D", 1]), P("OriginalUnitScaleFactor", "double", "Number", "", ["D", 1]),
      P("TimeMode", "enum", "", "", ["I", 6]), P("TimeSpanStart", "KTime", "Time", "", ["L", t0]),
      P("TimeSpanStop", "KTime", "Time", "", ["L", t1]), P("CustomFrameRate", "double", "Number", "", ["D", 30])];
    top.push(E("GlobalSettings", [], [E("Version", [["I", 1000]]), E("Properties70", [], gs)]));
    top.push(E("Documents", [], [E("Count", [["I", 1]]), E("Document", [["L", 1], ["S", take], ["S", take]],
      [E("Properties70", [], [P("SourceObject", "object", "", ""), P("ActiveAnimStackName", "KString", "", "", ["S", take])]), E("RootNode", [["L", 0]])])]));
    top.push(E("References"));
    const defs = [E("Version", [["I", 100]]), E("Count", [["I", 1 + nm + nm + 1 + 1 + nm * 3 + nm * 9]])];
    [["GlobalSettings", 1], ["NodeAttribute", nm], ["Model", nm], ["AnimationStack", 1], ["AnimationLayer", 1], ["AnimationCurveNode", nm * 3], ["AnimationCurve", nm * 9]]
      .forEach(([n, c]) => defs.push(E("ObjectType", [["S", n]], [E("Count", [["I", c]])])));
    top.push(E("Definitions", [], defs));
    const obj = [];
    names.forEach((n, i) => {
      const kind = i === 0 ? "Null" : "LimbNode";
      const kids = [E("TypeFlags", [["S", i === 0 ? "Null" : "Skeleton"]])];
      if (i > 0) kids.push(E("Properties70", [], [P("Size", "double", "Number", "", ["D", 3.3])]));
      obj.push(E("NodeAttribute", [["L", attr[i]], ["S", n + "\x00\x01NodeAttribute"], ["S", kind]], kids));
    });
    names.forEach((n, i) => {
      const kind = i === 0 ? "Null" : "LimbNode";
      const pr = [P("Lcl Translation", "Lcl Translation", "", "A+", ...T[i][0].map(v => ["D", v])),
        P("Lcl Rotation", "Lcl Rotation", "", "A+", ...Rr[i][0].map(v => ["D", v])),
        P("Lcl Scaling", "Lcl Scaling", "", "A+", ["D", 1], ["D", 1], ["D", 1]),
        P("DefaultAttributeIndex", "int", "Integer", "", ["I", 0]), P("InheritType", "enum", "", "", ["I", 1])];
      obj.push(E("Model", [["L", ids[i]], ["S", n + "\x00\x01Model"], ["S", kind]],
        [E("Version", [["I", 232]]), E("Properties70", [], pr), E("MultiLayer", [["I", 0]]), E("MultiTake", [["I", 0]]),
         E("Shading", [["C", "T"]]), E("Culling", [["S", "CullingOff"]])]));
    });
    obj.push(E("AnimationStack", [["L", stack], ["S", take + "\x00\x01AnimStack"], ["S", ""]],
      [E("Properties70", [], [P("LocalStart", "KTime", "Time", "", ["L", t0]), P("LocalStop", "KTime", "Time", "", ["L", t1]),
        P("ReferenceStart", "KTime", "Time", "", ["L", t0]), P("ReferenceStop", "KTime", "Time", "", ["L", t1])])]));
    obj.push(E("AnimationLayer", [["L", layer], ["S", take + "\x00\x01AnimLayer"], ["S", ""]]));
    names.forEach((n, i) => {
      for (const p of "TRS") {
        const d = p === "T" ? T[i][0] : p === "R" ? Rr[i][0] : [1, 1, 1];
        obj.push(E("AnimationCurveNode", [["L", cnode[i][p]], ["S", p + "\x00\x01AnimCurveNode"], ["S", ""]],
          [E("Properties70", [], ["X", "Y", "Z"].map((ax, a) => P("d|" + ax, "Number", "", "A", ["D", d[a]])))]));
      }
    });
    names.forEach((n, i) => {
      for (const p of "TRS") for (let a = 0; a < 3; a++) {
        const vals = []; for (let k = 0; k < nk; k++) vals.push(p === "S" ? 1 : (p === "T" ? T[i][k][a] : Rr[i][k][a]));
        obj.push(E("AnimationCurve", [["L", curves[i][p][a]], ["S", "\x00\x01AnimCurve"], ["S", ""]],
          [E("Default", [["D", 0]]), E("KeyVer", [["I", 4008]]), E("KeyTime", [["l", times]]), E("KeyValueFloat", [["f", vals]]),
           E("KeyAttrFlags", [["i", [24836]]]), E("KeyAttrDataFloat", [["f", [0, 0, 0, 0]]]), E("KeyAttrRefCount", [["i", [nk]]])]));
      }
    });
    top.push(E("Objects", [], obj));
    const con = [];
    const C = (kind, a, b, prop) => con.push(E("C", [["S", kind], ["L", a], ["L", b]].concat(prop ? [["S", prop]] : [])));
    names.forEach((n, i) => {
      C("OO", attr[i], ids[i]);
      C("OO", ids[i], i === 0 ? 0 : ids[bones[i - 1].parent < 0 ? 0 : bones[i - 1].parent + 1]);
    });
    C("OO", layer, stack);
    names.forEach((n, i) => {
      [["T", "Lcl Translation"], ["R", "Lcl Rotation"], ["S", "Lcl Scaling"]].forEach(([p, pn]) => {
        C("OO", cnode[i][p], layer); C("OP", cnode[i][p], ids[i], pn);
        ["X", "Y", "Z"].forEach((ax, a) => C("OP", curves[i][p][a], cnode[i][p], "d|" + ax));
      });
    });
    top.push(E("Connections", [], con));
    top.push(E("Takes", [], [E("Current", [["S", take]]), E("Take", [["S", take]],
      [E("FileName", [["S", take + ".tak"]]), E("LocalTime", [["L", t0], ["L", t1]]), E("ReferenceTime", [["L", t0], ["L", t1]])])]));
    return serialize(top);
  }
  // minimal ZIP (store, no compression): the downloads capability only allows a few extensions, not .fbx
  let CRC = null;
  function crc32(b) {
    if (!CRC) { CRC = new Uint32Array(256); for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; CRC[n] = c >>> 0; } }
    let c = 0xffffffff; for (let i = 0; i < b.length; i++) c = CRC[(c ^ b[i]) & 255] ^ (c >>> 8); return (c ^ 0xffffffff) >>> 0;
  }
  function zip(name, data) {
    const nb = enc.encode(name), crc = crc32(data), n = data.length;
    const lh = new Uint8Array(30 + nb.length), l = new DataView(lh.buffer);
    l.setUint32(0, 0x04034b50, true); l.setUint16(4, 20, true); l.setUint16(6, 0x0800, true); l.setUint16(8, 0, true); l.setUint16(10, 0, true); l.setUint16(12, 0x21, true);
    l.setUint32(14, crc, true); l.setUint32(18, n, true); l.setUint32(22, n, true); l.setUint16(26, nb.length, true); l.setUint16(28, 0, true); lh.set(nb, 30);
    const cd = new Uint8Array(46 + nb.length), c = new DataView(cd.buffer);
    c.setUint32(0, 0x02014b50, true); c.setUint16(4, 20, true); c.setUint16(6, 20, true); c.setUint16(8, 0x0800, true); c.setUint16(10, 0, true); c.setUint16(12, 0, true); c.setUint16(14, 0x21, true);
    c.setUint32(16, crc, true); c.setUint32(20, n, true); c.setUint32(24, n, true); c.setUint16(28, nb.length, true); c.setUint32(42, 0, true); cd.set(nb, 46);
    const end = new Uint8Array(22), e = new DataView(end.buffer);
    e.setUint32(0, 0x06054b50, true); e.setUint16(8, 1, true); e.setUint16(10, 1, true); e.setUint32(12, cd.length, true); e.setUint32(16, lh.length + n, true);
    const out = new Uint8Array(lh.length + n + cd.length + 22); out.set(lh, 0); out.set(data, lh.length); out.set(cd, lh.length + n); out.set(end, lh.length + n + cd.length);
    return out;
  }
  root.PoseLabFBX = { build, zip };
})(typeof window !== "undefined" ? window : globalThis);
