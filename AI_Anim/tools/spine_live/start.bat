@echo off
rem Mo Spine Live (server rieng, 127.0.0.1:8781), dong cua so nay de tat. Them --lan de may khac cung mang mo duoc.
cd /d "%~dp0\..\.."
start "" http://127.0.0.1:8781/spine
".venv\Scripts\python.exe" -I tools\spine_live\server.py %*
