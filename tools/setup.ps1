# One-time setup: Python venv with OpenCV + NumPy. Run from the project root.
param([switch]$NoSchedule)
$ErrorActionPreference = "Stop"
if (-not (Test-Path ".venv")) { python -m venv .venv }
.\.venv\Scripts\python.exe -m pip install -q --upgrade pip
.\.venv\Scripts\python.exe -m pip install -q -r requirements.txt
# nhanh lam viec master tren may nay (tao tu main mot lan; khong day len GitHub)
.\.venv\Scripts\python.exe -I tools\ensure_master.py
# bo nho Claude (.claude\memory_store -> bo nho phien): chi khoi phuc khi bo nho phien dang trong, khong de len bo nho dang co
try { .\.venv\Scripts\python.exe -I tools\claude_memory.py restore --if-empty }
catch { Write-Output "Chua khoi phuc duoc bo nho Claude (khong chan setup): $_" }
# lich Windows tu day kien thuc len GitHub moi ngay 17:10 (tools\knowledge_sync.py autopush).
# Doi gio: tools\knowledge_sync_install.ps1 -Time 12:30 | go: -Remove | khong cai lich luc setup: setup.ps1 -NoSchedule
if (-not $NoSchedule) {
    try { & powershell -NoProfile -ExecutionPolicy Bypass -File "$PSScriptRoot\knowledge_sync_install.ps1" }
    catch { Write-Output "Chua cai duoc lich tu day kien thuc (khong chan setup): $_" }
}
Write-Output "Setup done."
