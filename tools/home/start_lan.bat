@echo off
rem Mo Studio cho MAY KHAC CUNG MANG (LAN): server nghe moi dia chi cua may nay, cong 8780.
rem Lan dau Windows hoi tuong lua: chon "Private networks" roi Allow. Khong co mat khau: ai trong mang cung mo va sua duoc.
rem Dong cua so nay de tat. Chi dung tren may nay thi bam start.bat.
cd /d "%~dp0\..\.."
".venv\Scripts\python.exe" -I tools\home\server.py --lan
