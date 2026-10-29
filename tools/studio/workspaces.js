// AI Anim Studio — workspace = bố cục: panel mở sẵn (tab dock), shelf, hộp công cụ, panel hiện / ẩn, kích thước, module focus mặc định.
// Không khoá công cụ: lệnh, panel (Cửa sổ → Panel), lớp (Outliner) dùng được ở mọi workspace. General làm được mọi việc.
// Thêm workspace mới = thêm một mục ở đây (về sau lưu được workspace tự tạo, bước S6).
// Panel: id = "<module>:<tab của module>" (module tự vẽ), "channel" = Channel Box của module đang focus.
ST.PANELS = {
  channel: { label: "Channel Box" },
  "mesh:tool": { label: "Công cụ mesh", short: "Công cụ", mod: "mesh" }, "mesh:check": { label: "Kiểm tra mesh", short: "Kiểm tra", mod: "mesh" },
  // tab = chữ trên tab (chỉ số bước), title = tiêu đề ở đầu panel (user 2026-10-28: "Chỗ này để hiện số thôi. tên bước để dưới panel")
  "rig:s1": { label: "Rig 1 · Mesh", short: "1 Mesh", tab: "1", title: "Bước 1 · Mesh", mod: "rig" },
  "rig:s2": { label: "Rig 2 · Khớp", short: "2 Khớp", tab: "2", title: "Bước 2 · Khớp", mod: "rig" },
  "rig:s3": { label: "Rig 3 · Xương", short: "3 Xương", tab: "3", title: "Bước 3 · Xương", mod: "rig" },
  "rig:s4": { label: "Rig 4 · Skin", short: "4 Skin", tab: "4", title: "Bước 4 · Skin", mod: "rig" },
  "rig:s5": { label: "Rig 5 · Thử khớp", short: "5 Thử", tab: "5", title: "Bước 5 · Thử khớp", mod: "rig" },
  "rig:s6": { label: "Rig 6 · Vật lý", short: "6 Vật lý", tab: "6", title: "Bước 6 · Vật lý", mod: "rig" },
  "pose:joint": { label: "Pose · Khớp", short: "Khớp", mod: "pose" }, "pose:phys": { label: "Pose · Vật lý", short: "Vật lý", mod: "pose" },
  "pose:notes": { label: "Pose · Ghi chú", short: "Ghi chú", mod: "pose" },
  "pose:feedback": { label: "Góp ý cho AI", short: "Góp ý cho AI", mod: "pose" },   // ghi chú vẽ + điều chỉnh key, một nút gửi (user 2026-10-28 "gộp lại làm 1")
  "notes:list": { label: "Ghi chú vẽ", short: "Ghi chú vẽ", mod: "notes", nofocus: true }, "pose:versions": { label: "Pose · Phiên bản", short: "Phiên bản", mod: "pose" },
};
ST.WS_ALIAS = { mesh: "general" };   // link / pref cũ ?ws=mesh
ST.WS = {
  general: {   // như Maya "General": workspace chung, không giới hạn ở mesh
    id: "general", label: "General", icon: "mesh", focus: "mesh",
    tools: ["tool.sel", "tool.move", "tool.rot", "tool.scl", "tool.free"],
    modes: ["mesh.mode.o", "mesh.mode.v", "mesh.mode.f", "mesh.mode.i"],
    shelf: ["selmask.joint", "selmask.mesh", "|", "edit.undo", "edit.redo", "|", "mesh.delete", "mesh.separate", "mesh.merge", "mesh.dup", "|", "mesh.flip", "mesh.smooth", "mesh.flipx", "mesh.weld", "mesh.clean", "|",
      "mesh.ground", "mesh.height", "|", "mesh.pivEdit", "mesh.pivCenter", "|", "sel.sym", "sel.soft", "sel.front", "|", "mesh.wire", "view.tex", "view.toggle4", "view.frameAll", "view.frameSel", "|", "notes.draw", "file.fbx", "file.save", "edit.search"],
    tabs: ["channel", "mesh:tool", "mesh:check", "notes:list"],
    ui: { outliner: true, dock: true, shelf: true, timeline: false },
  },
  rig: {
    id: "rig", label: "Rig", icon: "rig", focus: "rig",
    tools: ["tool.sel", "tool.move", "tool.rot", "tool.scl"],
    modes: ["rig.step1", "rig.step2", "rig.step3", "rig.step4", "rig.step5"],
    shelf: ["edit.undo", "edit.redo", "|", "rig.mirror", "rig.guestJ", "rig.reset", "|", "skin.compute", "skin.brush", "skin.island", "skin.hammer", "skin.test", "|",
      "rig.toPose", "rig.export", "|", "view.toggle4", "view.frameAll", "view.frameSel", "|", "notes.draw", "edit.search"],
    tabs: ["rig:s1", "rig:s2", "rig:s3", "rig:s4", "rig:s5", "rig:s6", "notes:list"],
    drop: ["channel"],   // Rig không cần Channel Box (user 2026-10-28)
    size: { dockW: 360 },
    ui: { outliner: true, dock: true, shelf: true, timeline: false },
  },
  pose: {
    id: "pose", label: "Pose", icon: "pose", focus: "pose",
    tools: [], modes: [], shelf: "@pose",   // shelf = thanh công cụ Pose Lab (khối của modules/pose.js)
    tabs: ["pose:joint", "pose:phys", "pose:feedback"],   // pose:feedback = ghi chú vẽ ✎ + điều chỉnh gửi AI gộp một tab (2026-10-28)
    merge: { "pose:notes": "pose:feedback", "notes:list": "pose:feedback" },   // bố cục cũ đã lưu tự đổi sang tab gộp
    left: ["pose:versions"],   // Phiên bản dưới Outliner (user 2026-10-28: "Pose phiên bản đặt sang phía cùng với outliner")
    size: { dockW: 340 },
    ui: { outliner: true, dock: true, shelf: true, timeline: true },
  },

};
