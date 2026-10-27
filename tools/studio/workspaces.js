// AI Anim Studio — workspace = cấu hình sẵn: module nhận chuột, hộp công cụ, shelf, tab dock, panel hiện / ẩn, kiểu hiển thị mesh.
// Thêm workspace mới = thêm một mục ở đây (về sau lưu được workspace tự tạo, bước S6).
ST.WS_ALIAS = { mesh: "general" };   // link / pref cũ ?ws=mesh
ST.WS = {
  general: {   // như Maya "General": workspace chung, không giới hạn ở mesh
    id: "general", label: "General", icon: "mesh", module: "mesh", display: "edit",
    tools: ["tool.sel", "tool.move", "tool.rot", "tool.scl", "tool.free"],
    modes: ["mesh.mode.o", "mesh.mode.v", "mesh.mode.f", "mesh.mode.i"],
    shelf: ["selmask.joint", "selmask.mesh", "|", "edit.undo", "edit.redo", "|", "mesh.delete", "mesh.separate", "mesh.merge", "mesh.dup", "|", "mesh.flip", "mesh.smooth", "mesh.flipx", "mesh.weld", "mesh.clean", "|",
      "mesh.ground", "mesh.height", "|", "mesh.pivEdit", "mesh.pivCenter", "|", "sel.sym", "sel.soft", "sel.front", "|", "mesh.wire", "view.toggle4", "view.frameAll", "view.frameSel", "|", "file.fbx", "file.save", "edit.search"],
    tabs: [["channel", "Channel Box"], ["tool", "Công cụ"], ["check", "Kiểm tra"]],
    ui: { outliner: true, dock: true, shelf: true, timeline: false },
  },
  rig: {
    id: "rig", label: "Rig", icon: "rig", module: "rig", display: "hidden",
    tools: ["tool.sel", "tool.move", "tool.rot", "tool.scl"],
    modes: ["rig.step1", "rig.step2", "rig.step3", "rig.step4", "rig.step5"],
    shelf: ["edit.undo", "edit.redo", "|", "rig.mirror", "rig.guestJ", "rig.reset", "|", "skin.compute", "skin.brush", "skin.island", "skin.hammer", "skin.test", "|",
      "rig.toPose", "rig.export", "|", "view.toggle4", "view.frameAll", "view.frameSel", "|", "edit.search"],
    tabs: [["s1", "1 Mesh"], ["s2", "2 Khớp"], ["s3", "3 Xương"], ["s4", "4 Skin"], ["s5", "5 Thử"], ["channel", "Channel"]],
    size: { dockW: 360 },
    ui: { outliner: true, dock: true, shelf: true, timeline: false },
  },
  pose: {
    id: "pose", label: "Pose", icon: "pose", module: "pose", display: "hidden",
    tools: [], modes: [], shelf: [],   // thanh công cụ Pose Lab nằm ở shelf (modules/pose.js)
    tabs: [["joint", "Khớp"], ["phys", "Vật lý"], ["notes", "Ghi chú"], ["versions", "Phiên bản"]],
    size: { dockW: 340 },
    ui: { outliner: true, dock: true, shelf: true, timeline: true },
  },

};
