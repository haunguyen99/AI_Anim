# One-time setup: Python venv with OpenCV + NumPy. Run from the project root.
$ErrorActionPreference = "Stop"
if (-not (Test-Path ".venv")) { python -m venv .venv }
.\.venv\Scripts\python.exe -m pip install -q --upgrade pip
.\.venv\Scripts\python.exe -m pip install -q -r requirements.txt
# nhanh lam viec master tren may nay (tao tu main mot lan; khong day len GitHub)
.\.venv\Scripts\python.exe -I tools\ensure_master.py
Write-Output "Setup done."
