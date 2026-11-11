# Cài / gỡ lịch Windows tự đẩy kiến thức lên GitHub (tools/knowledge_sync.py autopush). Không cần quyền admin.
#   powershell -ExecutionPolicy Bypass -File tools\knowledge_sync_install.ps1                 # cài, mặc định 17:10 mỗi ngày
#   powershell -ExecutionPolicy Bypass -File tools\knowledge_sync_install.ps1 -Time 12:30     # đổi giờ
#   powershell -ExecutionPolicy Bypass -File tools\knowledge_sync_install.ps1 -Remove         # gỡ
# Máy tắt đúng giờ thì chạy bù khi bật lại (StartWhenAvailable). Nhật ký: work\store\_sys\watch\knowledge_autopush.log
param([string]$Time = '17:10', [switch]$Remove)
$name = 'AIAnim_KnowledgePush'
if ($Remove) {
    Unregister-ScheduledTask -TaskName $name -Confirm:$false -ErrorAction SilentlyContinue
    'Đã gỡ lịch.'; return
}
$root = Split-Path -Parent $PSScriptRoot
$py = Join-Path $root '.venv\Scripts\pythonw.exe'
$action = New-ScheduledTaskAction -Execute $py -Argument '-I tools\knowledge_sync.py autopush' -WorkingDirectory $root
$trigger = New-ScheduledTaskTrigger -Daily -At $Time
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RunOnlyIfNetworkAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 15)
Register-ScheduledTask -TaskName $name -Action $action -Trigger $trigger -Settings $settings -Description 'AI Animation: tự gộp và đẩy kiến thức lên GitHub main' -Force | Out-Null
"Đã cài lịch '$name': mỗi ngày lúc $Time."
