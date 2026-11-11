// Horus: Phiên Claude. Cây phiên Claude + phiên con trong VS Code.
// Việc thật do tools/subsession/subsession.py làm; extension chỉ gọi nó (JavaScript thuần, không cần build).
const vscode = require("vscode");
const path = require("path");
const fs = require("fs");
const { execFile } = require("child_process");

const ST = {
  "chạy": ["sync~spin", "Đang chạy"], "chờ": ["circle-outline", "Chờ (xong lượt)"], "kẹt": ["bell-dot", "Kẹt: chờ duyệt quyền"],
  "xong": ["check", "Xong"], "chặn": ["question", "Chặn: cần bạn trả lời"], "dừng": ["debug-stop", "Đã dừng"],
  "thoát": ["error", "Thoát, chưa có báo cáo"], "gone": ["trash", "Đã xoá"], "closed": ["history", "Đã đóng"],
};
const NOTIFY = new Set(["xong", "chặn", "kẹt", "thoát"]);

let root = null, rows = [], prev = null, tree, status, timer, busy = false;

function paths() {
  return { py: path.join(root, ".venv", "Scripts", "python.exe"), script: path.join(root, "tools", "subsession", "subsession.py") };
}
function run(args) {
  const { py, script } = paths();
  return new Promise((resolve, reject) => {
    execFile(py, ["-I", script, ...args], { cwd: root, encoding: "utf8", maxBuffer: 8 * 1024 * 1024, windowsHide: true, timeout: 120000,
      env: { ...process.env, PYTHONIOENCODING: "utf-8" } },
      (err, out, errout) => (err ? reject(new Error((errout || out || err.message).trim())) : resolve(out.trim())));
  });
}
const ago = (ms) => { if (!ms) return ""; const m = Math.round((Date.now() - ms) / 60000); return m < 1 ? "vừa xong" : m < 60 ? m + " phút trước" : m < 1440 ? Math.round(m / 60) + " giờ trước" : Math.round(m / 1440) + " ngày trước"; };
const stOf = (r) => r.sub ? r.sub.status : !r.live ? "closed" : (r.state === "blocked" ? "kẹt" : (r.state === "idle" || r.state === "done") ? "chờ" : "chạy");

async function refresh(manual) {
  if (busy) return; busy = true;
  try {
    const d = JSON.parse(await run(["json"]));
    rows = d.rows;
    // thông báo khi phiên con đổi sang xong / chặn / kẹt / thoát
    const now = {};
    for (const r of rows) if (r.sub) now[r.sub.key] = r.sub.status;
    if (prev) for (const r of rows) {
      if (!r.sub) continue;
      const was = prev[r.sub.key], is = r.sub.status;
      if (was && was !== is && NOTIFY.has(is)) {
        vscode.window.showInformationMessage(`Phiên con "${r.name}": ${ST[is][1]}${r.sub.report ? ". " + r.sub.report.slice(0, 140) : ""}`, "Xem")
          .then((c) => { if (c) show(r); });
      }
    }
    prev = now;
    const running = rows.filter((r) => r.sub && ["chạy", "kẹt"].includes(r.sub.status)).length;
    const busyN = rows.filter((r) => r.live && !r.sub && r.state === "busy").length;
    status.text = `$(organization) ${running} phiên con · ${busyN} đang làm`;
    status.tooltip = "Mở Phiên Claude";
    status.show();
  } catch (e) {
    if (manual) vscode.window.showWarningMessage("Phiên Claude: không đọc được danh sách. " + e.message);
  } finally { busy = false; }
  tree.fire();
}

class Provider {
  constructor() { this._e = new vscode.EventEmitter(); this.onDidChangeTreeData = this._e.event; }
  fire() { this._e.fire(); }
  getTreeItem(n) { return n; }
  inGroup(kind, r) { return kind === "sub" ? !!r.sub : kind === "live" ? !r.sub && r.live : !r.sub && !r.live; }
  getChildren(n) {
    if (!n) {
      const g = (label, kind, open) => {
        const count = rows.filter((r) => this.inGroup(kind, r)).length;
        const i = new vscode.TreeItem(`${label} (${count})`, !count ? vscode.TreeItemCollapsibleState.None : open ? vscode.TreeItemCollapsibleState.Expanded : vscode.TreeItemCollapsibleState.Collapsed);
        i.group = kind; i.contextValue = "group"; return i;
      };
      return [g("Phiên con (do subsession giao)", "sub", true), g("Đang chạy", "live", true), g("Gần đây (đã đóng)", "closed", false)];
    }
    if (n.group) return this.level(n.group, null);
    if (n.row) return this.level(n.kind, n.row.session);
    return [];
  }
  // phiên cùng nhóm, xếp cha → con theo spawnedFrom của app (phiên cha nằm nhóm khác thì con hiện ở đầu nhóm)
  level(kind, parent) {
    const here = rows.filter((r) => this.inGroup(kind, r)), ids = new Set(here.map((r) => r.session));
    const pid = (r) => r.sub ? (r.sub.parent ? (rows.find((x) => x.sub && x.sub.key === r.sub.parent) || {}).session : null) : r.parent;
    return here.filter((r) => parent ? pid(r) === parent : (!pid(r) || !ids.has(pid(r))))
      .map((r) => this.item(r, kind, here.some((x) => pid(x) === r.session)));
  }
  item(r, kind, hasKids) {
    const s = stOf(r);
    const i = new vscode.TreeItem(r.name, hasKids ? vscode.TreeItemCollapsibleState.Expanded : vscode.TreeItemCollapsibleState.None);
    const where = r.entrypoint === "claude-desktop" ? "app" : r.entrypoint === "claude-vscode" ? "VS Code" : r.sub ? "nền" : "";
    i.description = `${ST[s][1]}${where ? " · " + where : ""} · ${ago(r.last || r.started)}`;
    i.iconPath = new vscode.ThemeIcon(ST[s][0].split("~")[0], s === "chặn" || s === "kẹt" ? new vscode.ThemeColor("notificationsWarningIcon.foreground") : undefined);
    const tip = ["**" + r.name + "**", ST[s][1] + " · id " + r.id + (where ? " · " + where : "")];
    if (r.sub && r.sub.report) tip.push(r.sub.report);
    tip.push("_Bấm để mở trong Claude Code._");
    i.tooltip = new vscode.MarkdownString(tip.join("\n\n"));
    i.contextValue = r.sub ? "sub" : r.live ? "live" : "closed"; i.row = r; i.kind = kind;
    i.command = r.sub ? { command: "horusSessions.show", title: "Xem", arguments: [i] } : { command: "horusSessions.open", title: "Mở trong Claude Code", arguments: [i] };
    return i;
  }
}

// nội dung ảo: báo cáo + việc đã giao + log của một phiên
const docs = new Map();
const docEvt = new vscode.EventEmitter();
async function show(arg) {
  const r = arg && arg.row ? arg.row : arg;
  if (!r) return;
  let txt;
  try {
    const d = JSON.parse(await run(["detail", r.id]));
    const brief = (d.brief || "").split("\n---\nLUẬT PHIÊN CON")[0];
    txt = `# ${r.name}\n\n${ST[stOf(r)][1]} · id \`${r.id}\` · ${r.cwd || ""}\n\n` +
      (d.report ? `## Báo cáo\n\n${d.report}\n\n` : "") + (brief ? `## Việc đã giao\n\n${brief}\n\n` : "") +
      (d.log ? `## Log gần nhất\n\n\`\`\`\n${d.log}\n\`\`\`\n` : "_Phiên mở trong VS Code / app: không có log nền._\n");
  } catch (e) { txt = `# ${r.name}\n\nKhông đọc được: ${e.message}`; }
  const uri = vscode.Uri.parse(`horus-session:/${encodeURIComponent(r.name)}-${r.id}.md`);
  docs.set(uri.toString(), txt); docEvt.fire(uri);
  await vscode.window.showTextDocument(await vscode.workspace.openTextDocument(uri), { preview: true });
}

// mở phiên trong Claude Code (extension Anthropic): claude-vscode.primaryEditor.open(sessionId, prompt?)
async function openInClaude(arg, prompt) {
  const r = arg && arg.row ? arg.row : arg;
  if (!r || !r.session) return;
  try { await vscode.commands.executeCommand("claude-vscode.primaryEditor.open", r.session, prompt); }
  catch (e) { vscode.window.showErrorMessage("Không mở được trong Claude Code: " + e.message); }
}

const need = (arg) => { const r = arg && arg.row; if (!r || !r.sub) { vscode.window.showInformationMessage("Chỉ làm được với phiên con do subsession giao."); return null; } return r; };

async function newTask() {
  const sel = vscode.window.activeTextEditor && !vscode.window.activeTextEditor.selection.isEmpty
    ? vscode.window.activeTextEditor.document.getText(vscode.window.activeTextEditor.selection).trim() : "";
  const name = await vscode.window.showInputBox({ title: "Giao việc cho phiên con (1/2)", prompt: "Tên ngắn, vd: doc-bao-cao", validateInput: (v) => v.trim() ? null : "Cần một tên" });
  if (!name) return;
  const brief = sel || await vscode.window.showInputBox({ title: "Giao việc cho phiên con (2/2)", prompt: "Việc cần làm: file nào được sửa, “xong” là gì. (Việc dài: chọn văn bản trong editor rồi bấm Giao việc mới.)", validateInput: (v) => v.trim() ? null : "Cần nội dung việc" });
  if (!brief) return;
  try {
    const out = await run(["start", "--name", name.trim(), "--brief", brief.trim()]);
    vscode.window.showInformationMessage(`Đã giao việc "${name}". ${out.split("\n").pop()}`);
  } catch (e) { vscode.window.showErrorMessage("Giao việc lỗi: " + e.message); }
  refresh();
}

async function simple(arg, fn, ok) {
  const r = need(arg); if (!r) return;
  try { const out = await fn(r); vscode.window.showInformationMessage(ok(r, out)); } catch (e) { vscode.window.showErrorMessage(e.message); }
  refresh();
}

function activate(ctx) {
  const ws = vscode.workspace.workspaceFolders;
  root = ws && ws.find((f) => fs.existsSync(path.join(f.uri.fsPath, "tools", "subsession", "subsession.py")))?.uri.fsPath;
  if (!root) return;
  tree = new Provider();
  status = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 50);
  status.command = "horusSessions.tree.focus";
  ctx.subscriptions.push(
    status,
    vscode.window.registerTreeDataProvider("horusSessions.tree", tree),
    vscode.workspace.registerTextDocumentContentProvider("horus-session", {
      onDidChange: docEvt.event, provideTextDocumentContent: (u) => docs.get(u.toString()) || "",
    }),
    vscode.commands.registerCommand("horusSessions.refresh", () => refresh(true)),
    vscode.commands.registerCommand("horusSessions.newTask", newTask),
    vscode.commands.registerCommand("horusSessions.show", show),
    vscode.commands.registerCommand("horusSessions.open", (arg) => openInClaude(arg)),
    vscode.commands.registerCommand("horusSessions.send", async (arg) => {
      const r0 = arg && arg.row;
      if (r0 && !r0.sub) {  // phiên thường: mở trong Claude Code, điền sẵn tin nhắn để bạn bấm Enter
        const t = await vscode.window.showInputBox({ title: `Nhắn thêm cho "${r0.name}"`, prompt: "Tin sẽ được điền sẵn trong khung chat của Claude Code" });
        if (t && t.trim()) openInClaude(arg, t.trim());
        return;
      }
      const r = need(arg); if (!r) return;
      const m = await vscode.window.showInputBox({ title: `Nhắn thêm cho "${r.name}"`, prompt: "Việc thêm hoặc câu trả lời cho phiên con" });
      if (!m || !m.trim()) return;
      simple(arg, (x) => run(["send", x.sub.key, m.trim()]), (x) => `Đã gửi cho "${x.name}".`);
    }),
    vscode.commands.registerCommand("horusSessions.stop", async (arg) => {
      const r = need(arg); if (!r) return;
      if (await vscode.window.showWarningMessage(`Dừng "${r.name}"? Hội thoại vẫn giữ.`, { modal: true }, "Dừng") !== "Dừng") return;
      simple(arg, (x) => run(["stop", x.sub.key]), (x) => `Đã dừng "${x.name}".`);
    }),
    vscode.commands.registerCommand("horusSessions.remove", async (arg) => {
      const r = need(arg); if (!r) return;
      if (await vscode.window.showWarningMessage(`Xoá "${r.name}"? Mất hội thoại.`, { modal: true }, "Xoá") !== "Xoá") return;
      simple(arg, (x) => run(["rm", x.sub.key]), (x) => `Đã xoá "${x.name}".`);
    }),
    vscode.commands.registerCommand("horusSessions.attach", (arg) => {
      const r = need(arg); if (!r) return;
      const t = vscode.window.createTerminal({ name: `claude ${r.name}`, cwd: root });
      t.show(); t.sendText(`claude attach ${r.id}`);
    }),
  );
  refresh();
  timer = setInterval(() => { if (vscode.window.state.focused) refresh(); }, 5000);
  ctx.subscriptions.push({ dispose: () => clearInterval(timer) });
}
function deactivate() { clearInterval(timer); }
module.exports = { activate, deactivate };
