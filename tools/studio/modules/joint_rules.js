// AI Anim Studio — Liên động khớp (2026-10-31, user: "khi muốn giơ tay lên đầu thì cầu vai cũng phải đi theo... AI cần phân
// tích và phán đoán để tạo sự liên kết giữa các bộ phận"). Cùng luật với tools/joint_rules.py (tools/joint_rules/biped.json,
// ghi đè theo nhân vật: work/rig_lab/chars/<id>/joint_rules.json; Home phát ở /api/joint-rules?char=<id>).
// - Kéo / xoay xong một khớp trong Pose (gizmo) hoặc lệnh AI anim rot / pos: lõi Pose gọi after(ctx) (bản vá jrRun trong
//   pose_patches.py) → bả vai theo tay (nhún + ra trước / sau), đốt sống chia góc Spine1 / Chest, cổ chia góc với đầu.
//   Đo theo phần THAY ĐỔI của lần sửa này (so pose trước khi kéo), nên không cãi lại pose đã chỉnh từ trước.
//   Dời bàn tay (W, IK): bàn tay giữ chỗ, bả vai theo, tay giải IK lại. Xoay vai (E): giữ hướng cánh tay, tay dời theo điểm vai.
// - Nút "Liên động" cạnh "Khóa chân" bật / tắt (nhớ theo máy). Cầu nối: anim rules {do: on|off|status|audit|apply}.
// Khung ngực lấy từ hình học (cổ − ngực = lên, bả vai trái − phải = trái), không cần T-pose, đúng cả glTF lẫn FBX.
(function () {
  const JR = window.__jointRules = { on: () => on && !!R, after, cmd, rules: () => R };
  const V3 = THREE.Vector3, Q = THREE.Quaternion, deg = THREE.MathUtils.radToDeg, rad = THREE.MathUtils.degToRad;
  let R = null, on = true, force = false, last = null;
  try { on = localStorage.getItem("st:jointRules") !== "0"; } catch (e) {}

  async function load() {
    try { const r = await fetch("/api/joint-rules?char=" + encodeURIComponent(ST.char ? ST.char.id : "")); if (r.ok) R = await r.json(); } catch (e) { R = null; }
    button(); return R;
  }
  ST.on && ST.on("filled", load);
  if (ST.char) load();

  // ---- nút bật / tắt trong thanh công cụ Pose
  function button() {
    const lock = document.getElementById("tLock"); if (!lock) return;
    let b = document.getElementById("tJR");
    if (!b) {
      b = document.createElement("button"); b.id = "tJR"; b.className = "ibtn tool";
      b.onclick = () => setOn(!on); lock.after(b);
    }
    b.textContent = "Liên động"; b.classList.toggle("on", on && !!R); b.disabled = !R;
    b.title = R ? "Bật: kéo / xoay xong một khớp thì các khớp liên quan đi theo (tay giơ → bả vai nhún + ra trước; thân → chia đều Spine1 / Chest; đầu → cổ góp 40 %). Luật: tools/joint_rules/biped.json"
      : "Chưa nạp được luật khớp (Home cần bản mới có /api/joint-rules: tắt và mở lại Home)";
  }
  function setOn(v) { on = !!v; try { localStorage.setItem("st:jointRules", on ? "1" : "0"); } catch (e) {} button(); return { on: JR.on() }; }
  new MutationObserver(() => { if (!document.getElementById("tJR") && document.getElementById("tLock")) button(); }).observe(document.body, { childList: true, subtree: true });

  // ---- số đo (pose = { pos(n) → V3 world, lq(n) → Quaternion local })
  const curve = (c, x) => { if (x <= c[0][0]) return c[0][1]; for (let i = 1; i < c.length; i++) if (x <= c[i][0]) { const [a, b] = [c[i - 1], c[i]]; return a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0]); } return c[c.length - 1][1]; };
  const smooth = (x, a, b) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
  function axes(S, s) {
    const up = S.pos("Neck_M").sub(S.pos("Chest_M")).normalize(), left = S.pos("Scapula_L").sub(S.pos("Scapula_R"));
    left.addScaledVector(up, -left.dot(up)).normalize();
    const fwd = new V3().crossVectors(left, up);
    return { up, fwd, lat: s === "R" ? left.clone().negate() : left };
  }
  function arm(S, s) {
    const { up, fwd, lat } = axes(S, s), u = S.pos("Elbow_" + s).sub(S.pos("Shoulder_" + s)).normalize();
    return { elev: deg(u.angleTo(up.clone().negate())), hflex: deg(Math.atan2(u.dot(fwd), u.dot(lat))) };
  }
  function clav(S, s) {
    const { up, fwd, lat } = axes(S, s), v = S.pos("Shoulder_" + s).sub(S.pos("Scapula_" + s)).normalize();
    return { clav_elev: deg(Math.asin(Math.max(-1, Math.min(1, v.dot(up))))), clav_prot: deg(Math.atan2(v.dot(fwd), v.dot(lat))) };
  }
  function expect(cp, S, s) {
    const a = arm(S, s);
    if (cp.driver === "arm_elev") return curve(cp.curve, a.elev);
    return (cp.weight_by_elev ? smooth(a.elev, 20, 70) : 1) * curve(cp.curve, a.hflex);
  }
  const follows = () => (R ? R.couplings : []).filter(c => (c.type || "follow") === "follow");
  const shares = () => (R ? R.couplings : []).filter(c => c.type === "share");
  function chainShare(cp, S, Sb) {   // góc mỗi đốt so pose b + tổng góc cả chuỗi (độ)
    const a = cp.chain.map(n => deg(S.lq(n).angleTo(Sb.lq(n))));
    const rel = X => cp.chain.reduce((q, n) => q.multiply(X.lq(n)), new Q());
    return { a, tot: deg(rel(S).angleTo(rel(Sb))), sum: a.reduce((x, y) => x + y, 0) };
  }
  const has = (B, ns) => ns.every(n => B[n]);

  // pose sống / pose trước khi kéo / pose mẫu từ sampleBones
  const live = c => ({ pos: n => c.wp(c.B[n]), lq: n => c.B[n].quaternion.clone() });
  const before = c => ({ pos: n => c.base[n].p.clone(), lq: n => c.base[n].lq.clone() });
  function sampled(w) {      // w = { n: {p, q world} } → local từ world của cha
    const par = n => { const o = w[n] && w.__B[n].parent; return o && w[o.name] ? o.name : null; };
    return { pos: n => w[n].p.clone(), lq: n => { const p = par(n); return p ? w[p].q.clone().invert().multiply(w[n].q) : w[n].q.clone(); } };
  }

  // ---- sửa: S0 = pose so sánh (trước khi kéo, hoặc F1 khi apply cả pose); trả danh sách khớp đã đổi + ghi chú
  function couple(c, S0, opt) {
    const B = c.B, S = live(c), changed = new Set(), msg = [];
    for (const cp of shares()) {
      if (!has(B, cp.chain.concat(cp.parent)) || !opt.share(cp)) continue;
      const { a, tot, sum } = chainShare(cp, S, S0);
      if (tot < (cp.min_total || 10) || sum < 1e-6) continue;
      const sh = a.map(x => x / sum), [lo, hi] = cp.band;
      if (!sh.some(x => x < lo || x > hi)) continue;
      const end = cp.chain[cp.chain.length - 1], parts = [], acc = c.wq(B[cp.parent]);
      cp.chain.forEach(n => parts.push(acc.multiply(S0.lq(n)).clone()));
      const D = c.wq(B[end]).multiply(parts[parts.length - 1].clone().invert());
      let k = 0; cp.chain.forEach((n, i) => { k += cp.weights[i]; c.setWorldQuat(B[n], new Q().slerp(D, k).multiply(parts[i])); changed.add(n); });
      c.model.updateMatrixWorld(true);
      msg.push(cp.chain.join("/") + " chia " + cp.weights.map(w => Math.round(w * 100) + "%").join("/"));
    }
    for (const s of opt.sides) {
      const sc = "Scapula_" + s, sh = "Shoulder_" + s, wr = "Wrist_" + s;
      if (!has(B, [sc, sh, "Elbow_" + s, wr, "Neck_M", "Chest_M", "Scapula_L", "Scapula_R"])) continue;
      const keep = opt.keep(s), hand = keep === "hand" ? { p: c.wp(B[wr]), q: c.wq(B[wr]) } : null, add = {};
      for (let it = 0; it < 3; it++) {
        for (const cp of follows()) {
          if (!cp.fix || !(cp.side || "LR").includes(s)) continue;
          const want = expect(cp, S, s) - expect(cp, S0, s), got = clav(S, s)[cp.driven] - clav(S0, s)[cp.driven], need = want - got;
          if (Math.abs(need) < 0.3) continue;
          const { up, fwd, lat } = axes(S, s), v = S.pos(sh).sub(S.pos(sc)).normalize(), cl = clav(S, s);
          let e = cl.clav_elev, p = cl.clav_prot; if (cp.driven === "clav_elev") e += need; else p += need;
          const vt = lat.clone().multiplyScalar(Math.cos(rad(e)) * Math.cos(rad(p))).addScaledVector(fwd, Math.cos(rad(e)) * Math.sin(rad(p))).addScaledVector(up, Math.sin(rad(e)));
          const qs = c.wq(B[sh]);
          c.setWorldQuat(B[sc], new Q().setFromUnitVectors(v, vt.normalize()).multiply(c.wq(B[sc])));
          if (keep === "dir") c.setWorldQuat(B[sh], qs);
          add[cp.driven] = (add[cp.driven] || 0) + need; changed.add(sc);
        }
        if (hand) { c.solveArm(s, hand.p, hand.q); ["Shoulder_", "Elbow_", "Wrist_"].forEach(k => changed.add(k + s)); }
        c.model.updateMatrixWorld(true);
      }
      const sd = s === "R" ? "phải" : "trái", t = [];
      if (Math.abs(add.clav_elev || 0) >= 0.5) t.push((add.clav_elev > 0 ? "nhún " : "hạ ") + Math.abs(add.clav_elev).toFixed(0) + "°");
      if (Math.abs(add.clav_prot || 0) >= 0.5) t.push((add.clav_prot > 0 ? "ra trước " : "ra sau ") + Math.abs(add.clav_prot).toFixed(0) + "°");
      if (t.length) msg.push("bả vai " + sd + " " + t.join(", "));
    }
    return { changed: [...changed], msg: msg.length ? "Liên động: " + msg.join(" · ") + " (Ctrl+Z bỏ)" : "" };
  }

  // ---- lõi Pose gọi sau mỗi lần kéo / lệnh AI (ctx = jrCtx() của lõi)
  function after(c) {
    if (!R) return null;
    let r;
    if (force) {       // anim rules apply: cả pose so F1 (P0 của clip), mọi luật
      force = false;
      const w = c.sample(1); w.__B = c.B;
      r = couple(c, sampled(w), { sides: "LR", keep: () => "hand", share: () => true });
    } else {
      const sel = new Set(c.selSet.length ? c.selSet : [c.sel]);
      const armSide = s => ["Shoulder_", "Elbow_", "Wrist_"].some(k => sel.has(k + s)) && !sel.has("Scapula_" + s);
      const sides = ["L", "R"].filter(armSide).join("");
      r = couple(c, before(c), {
        sides, keep: s => sel.has("Wrist_" + s) ? "hand" : "dir",   // cổ tay chọn = dời tay IK (W hoặc lệnh pos): bàn tay giữ chỗ
        share: cp => cp.chain.some(n => sel.has(n)) && !sel.has(cp.parent),
      });
    }
    if (r.changed.length) c.mark(r.changed);
    last = Object.assign({ at: new Date().toISOString(), frame: c.frame }, r);
    return r;
  }

  // ---- kiểm một frame so F1 (cùng luật, như joint_rules.py audit, chưa có giới hạn khớp)
  function audit(c, f, S1) {
    const w = c.sample(f); w.__B = c.B; const S = sampled(w), out = [];
    for (const cp of follows()) for (const s of cp.side || "LR") {
      if (!has(c.B, ["Scapula_" + s, "Shoulder_" + s, "Elbow_" + s, "Neck_M", "Chest_M"])) continue;
      const want = expect(cp, S, s) - expect(cp, S1, s), got = clav(S, s)[cp.driven] - clav(S1, s)[cp.driven];
      if (Math.abs(want - got) > (cp.tol || 5)) out.push({ f, rule: cp.id, joint: "Scapula_" + s, want: +want.toFixed(1), got: +got.toFixed(1),
        msg: cp.label + ": xương đòn " + s + " nên " + (want >= 0 ? "+" : "") + want.toFixed(0) + "°, đang " + (got >= 0 ? "+" : "") + got.toFixed(0) + "°" });
    }
    for (const cp of shares()) {
      if (!has(c.B, cp.chain.concat(cp.parent))) continue;
      const { a, tot, sum } = chainShare(cp, S, S1); if (tot < (cp.min_total || 10) || sum < 1e-6) continue;
      const sh = a.map(x => x / sum), [lo, hi] = cp.band;
      if (sh.some(x => x < lo || x > hi)) out.push({ f, rule: cp.id, joint: cp.chain.join("/"), share: sh.map(x => +x.toFixed(2)),
        msg: cp.label + ": tổng " + tot.toFixed(0) + "°, chia " + sh.map(x => Math.round(100 * x) + "%").join("/") + " (nên ~" + cp.weights.map(x => Math.round(100 * x) + "%").join("/") + ")" });
    }
    return out;
  }

  // ---- cầu nối: anim rules {do: on|off|status|audit|apply, f}
  async function cmd(a) {
    const E = ST.poseEng && ST.poseEng(); if (!R) await load();
    if (!R) throw new Error("Chưa nạp được luật khớp: Home chưa có /api/joint-rules (tắt và mở lại Home)");
    const d = a.do || "status";
    if (d === "on" || d === "off") return setOn(d === "on");
    if (d === "status") return { on: JR.on(), rules: R.couplings.map(c => c.id), last };
    if (!E || !E.jrCtx) throw new Error("Lõi Pose chưa nạp (hoặc bản cũ không có jrCtx: chạy port_pose.py rồi tải lại trang)");
    const c = E.jrCtx(), info = E.ai.info();
    if (d === "audit") {
      const w1 = c.sample(1); w1.__B = c.B; const S1 = sampled(w1);
      const fs = a.f === "all" ? Array.from({ length: info.frames }, (_, i) => i + 1) : a.f === "keys" || a.f == null ? (info.keys.length ? info.keys : [info.frame]) : [].concat(a.f).map(Number);
      const errs = fs.flatMap(f => audit(c, f, S1)), by = {};
      errs.forEach(e => (by[e.rule + " " + e.joint] = by[e.rule + " " + e.joint] || []).push(e.f));
      return { frames: fs.length, errors: errs.length, by, list: errs.slice(0, 80) };
    }
    if (d === "apply") {     // frame đang xem (hoặc a.f): mọi luật so F1, qua đường sửa của lõi (Hoàn tác + Auto key như thao tác tay)
      if (a.f) E.ai.frame(a.f);
      force = true; E.ai.rot("Chest_M", [0, 0, 0]); force = false;
      return last;
    }
    throw new Error("anim rules: on | off | status | audit [f: số | keys | all] | apply [f]");
  }
})();
