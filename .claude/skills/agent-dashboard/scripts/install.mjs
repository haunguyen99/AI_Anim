#!/usr/bin/env node
// Liên kết skill này vào ~/.claude/skills để dùng ở mọi repo. Sửa ở repo nguồn là mọi repo được cập nhật.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const source = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const skills = path.join(os.homedir(), '.claude', 'skills');
const target = path.join(skills, 'agent-dashboard');

fs.mkdirSync(skills, { recursive: true });
const current = fs.lstatSync(target, { throwIfNoEntry: false });
if (current && !current.isSymbolicLink()) {
  console.error(`Bỏ qua: ${target} đã tồn tại và không phải liên kết.`);
  process.exit(1);
}
// Liên kết hỏng (repo đã bị di chuyển hoặc xóa) không có đường dẫn thật.
const linkedTo = () => {
  try {
    return fs.realpathSync.native(target);
  } catch (error) {
    if (error.code === 'ENOENT') return null;
    throw error;
  }
};
if (current && linkedTo() === fs.realpathSync.native(source)) {
  console.log(`Đã cài sẵn: ${target}`);
  process.exit(0);
}
// unlink chỉ gỡ liên kết, không đụng tới nội dung thư mục mà nó trỏ tới.
if (current) fs.unlinkSync(target);
// Junction trên Windows không cần quyền quản trị.
fs.symlinkSync(source, target, process.platform === 'win32' ? 'junction' : 'dir');
console.log(`Đã cài: ${target}`);
