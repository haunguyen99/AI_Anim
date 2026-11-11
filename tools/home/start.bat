@echo off
rem Mo Studio (viewport) + Home (/home): server chay tren may nay (127.0.0.1:8780), dong cua so nay de tat.
cd /d "%~dp0\..\.."
rem may moi clone dang o nhanh main: tu tao nhanh lam viec master (mot lan, xem tools\ensure_master.py)
".venv\Scripts\python.exe" -I tools\ensure_master.py
start "" http://127.0.0.1:8780
rem Spine Live chay server rieng (cong 8781) trong cua so thu hai
start "Spine Live" ".venv\Scripts\python.exe" -I tools\spine_live\server.py
".venv\Scripts\python.exe" -I tools\home\server.py
