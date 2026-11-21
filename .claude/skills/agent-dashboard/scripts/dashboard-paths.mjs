// Xác định repo cần xem và nơi lưu trang, dùng chung cho bản tĩnh và bản Live.
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

export function resolveRoot(argv = process.argv) {
  const flag = argv.indexOf('--root');
  if (flag >= 0) {
    const given = argv[flag + 1];
    if (!given || !fs.existsSync(given) || !fs.statSync(given).isDirectory()) {
      console.error(`Thư mục --root không tồn tại: ${given ?? '(trống)'}`);
      process.exit(1);
    }
    return fs.realpathSync.native(path.resolve(given));
  }
  try {
    const top = execFileSync('git', ['rev-parse', '--show-toplevel'], {
      encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'], windowsHide: true,
    }).trim();
    if (top) return fs.realpathSync.native(path.resolve(top));
  } catch {
    // Không phải repo git thì xem thư mục hiện tại.
  }
  return fs.realpathSync.native(process.cwd());
}

// Trang lưu ngoài repo để không thêm file rác hay phải sửa .gitignore của repo được xem.
export function outputFile(root) {
  const slug = root.replace(/[^a-zA-Z0-9]/g, '-');
  return path.join(os.homedir(), '.claude', 'agent-dashboard', slug, 'agents.html');
}
