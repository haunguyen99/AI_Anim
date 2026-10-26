@echo off
rem Mo Home: server chay tren may nay (127.0.0.1:8780), dong cua so nay de tat.
cd /d "%~dp0\..\.."
start "" http://127.0.0.1:8780
".venv\Scripts\python.exe" -I tools\home\server.py
