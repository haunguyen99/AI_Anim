"""Mỗi máy làm việc trên nhánh master riêng (chỉ ở máy, không bao giờ đẩy lên GitHub); GitHub main chỉ có mã nguồn.
Máy vừa clone đang ở main: tạo master từ main rồi chuyển sang (một lần). Máy đã có master hoặc đang ở nhánh khác: không làm gì.
Gọi từ tools/setup.ps1 (cài lần đầu) và tools/home/start.bat (mỗi lần mở Home), nên máy cài từ trước cũng tự có master.
Lấy mã mới của team sau đó: `git pull origin main`. Đẩy mã nguồn: /push (tools/push_source.py dựng từ origin/main, đứng nhánh nào cũng được).
Không bao giờ chặn việc mở Home: lỗi gì cũng thoát 0.
"""
import os, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True, encoding="utf8")


def main():
    try:
        if git("rev-parse", "--is-inside-work-tree").stdout.strip() != "true":
            return 0
        if git("branch", "--show-current").stdout.strip() != "main":
            return 0
        if git("show-ref", "--verify", "--quiet", "refs/heads/master").returncode == 0:
            return 0
        r = git("switch", "-c", "master")
        if r.returncode == 0:
            print("Da tao nhanh master tu main va chuyen sang (nhanh lam viec tren may nay, khong day len GitHub).")
            print("Lay ma moi cua team: git pull origin main  |  Day ma nguon: /push")
        else:
            print("Chua tao duoc nhanh master: " + (r.stderr or r.stdout).strip())
    except Exception as e:   # không có git, v.v.
        print("Bo qua buoc tao nhanh master: %s" % e)
    return 0


if __name__ == "__main__":
    sys.exit(main())
