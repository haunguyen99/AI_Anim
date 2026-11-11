# Cài / gỡ bộ canh HorusChat chạy ngầm khi đăng nhập Windows (thư mục Startup của người dùng, không cần quyền admin).
#   powershell -ExecutionPolicy Bypass -File tools\horuschat_daemon_install.ps1          # cài + chạy ngay
#   powershell -ExecutionPolicy Bypass -File tools\horuschat_daemon_install.ps1 -Remove  # gỡ + tắt
param([switch]$Remove)
$root = Split-Path -Parent $PSScriptRoot
$startup = [Environment]::GetFolderPath('Startup')
$lnk = Join-Path $startup 'HorusChat-watch.lnk'
if ($Remove) {
    if (Test-Path $lnk) { Remove-Item $lnk -Force }
    Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*horuschat_daemon.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
    'Đã gỡ.'; return
}
$py = Join-Path $root '.venv\Scripts\pythonw.exe'
$sh = New-Object -ComObject WScript.Shell
$s = $sh.CreateShortcut($lnk)
$s.TargetPath = $py
$s.Arguments = '-I tools\horuschat_daemon.py'
$s.WorkingDirectory = $root
$s.WindowStyle = 7
$s.Save()
Start-Process -FilePath $py -ArgumentList '-I tools\horuschat_daemon.py' -WorkingDirectory $root -WindowStyle Hidden
"Đã cài: $lnk"
