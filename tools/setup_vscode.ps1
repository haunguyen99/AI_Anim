# Cài VS Code + extension Claude Code cho team Animation và đặt endpoint AI.
# Hướng dẫn đầy đủ: docs/vscode_pilot.md
#
#   powershell -ExecutionPolicy Bypass -File tools/setup_vscode.ps1               # chỉ kiểm, không cài / không ghi
#   powershell -ExecutionPolicy Bypass -File tools/setup_vscode.ps1 -Install      # cài VS Code (winget, user) + extension
#   powershell -ExecutionPolicy Bypass -File tools/setup_vscode.ps1 -Endpoint lan     # endpoint IP LAN công ty
#   powershell -ExecutionPolicy Bypass -File tools/setup_vscode.ps1 -Endpoint public  # endpoint llmpro (ngoài công ty)
#
# Không bao giờ ghi key. Key do lead cấp, mỗi người tự đặt trong ~/.claude/settings.json (env.ANTHROPIC_AUTH_TOKEN).
param(
  [switch]$Install,
  [ValidateSet('keep', 'lan', 'public')][string]$Endpoint = 'keep'
)

$LAN_URL = 'http://192.168.10.29:40741'
$PUBLIC_URL = 'https://llmpro.horusjsc.com'
$EXT_ID = 'anthropic.claude-code'
$Repo = Split-Path -Parent $PSScriptRoot

function Find-Code {
  $c = Get-Command code -ErrorAction SilentlyContinue
  if ($c) { return $c.Source }
  foreach ($p in "$env:LOCALAPPDATA\Programs\Microsoft VS Code\bin\code.cmd", "C:\Program Files\Microsoft VS Code\bin\code.cmd") {
    if (Test-Path $p) { return $p }
  }
  return $null
}

# 1. VS Code
$code = Find-Code
if ($code) {
  Write-Host "[OK] VS Code: $((& $code --version)[0])"
} elseif ($Install) {
  Write-Host "[..] Cài VS Code từ winget (Microsoft.VisualStudioCode, cho user này)…"
  winget install --id Microsoft.VisualStudioCode -e --scope user --source winget --accept-source-agreements --accept-package-agreements --silent --override "/VERYSILENT /NORESTART /MERGETASKS=!runcode,addcontextmenufiles,addcontextmenufolders,addtopath"
  $code = Find-Code
  if (-not $code) { Write-Host "[LỖI] Cài VS Code không thành công."; exit 1 }
  Write-Host "[OK] Đã cài VS Code."
} else {
  Write-Host "[THIẾU] VS Code chưa có. Chạy lại với -Install."
}

# 2. Extension Claude Code (publisher Anthropic)
if ($code) {
  $exts = & $code --list-extensions 2>$null
  if ($exts -contains $EXT_ID) {
    Write-Host "[OK] Extension $EXT_ID đã có."
  } elseif ($Install) {
    & $code --install-extension $EXT_ID 2>$null | Out-Null
    Write-Host "[OK] Đã cài extension $EXT_ID."
  } else {
    Write-Host "[THIẾU] Extension $EXT_ID chưa có. Chạy lại với -Install."
  }
}

# 3. Cấu hình endpoint trong ~/.claude/settings.json (chỉ đọc key để báo có / không, không in)
$sf = Join-Path $env:USERPROFILE '.claude\settings.json'
if (-not (Test-Path $sf)) {
  Write-Host "[THIẾU] Chưa có $sf. Nhờ lead cấp key, rồi tạo file theo mẫu trong docs/vscode_pilot.md (mục 7)."
} else {
  $txt = [IO.File]::ReadAllText($sf)
  $cfg = $txt | ConvertFrom-Json
  $cur = $cfg.env.ANTHROPIC_BASE_URL
  $hasKey = [bool]$cfg.env.ANTHROPIC_AUTH_TOKEN
  Write-Host "[..] Endpoint hiện tại: $(if ($cur) { $cur } else { '(mặc định Anthropic)' }); key: $(if ($hasKey) { 'có' } else { 'CHƯA CÓ' })"
  if ($Endpoint -ne 'keep') {
    $want = if ($Endpoint -eq 'lan') { $LAN_URL } else { $PUBLIC_URL }
    $ok = $true
    if ($Endpoint -eq 'lan') {
      $tcp = New-Object Net.Sockets.TcpClient
      try { $ok = $tcp.ConnectAsync('192.168.10.29', 40741).Wait(3000) -and $tcp.Connected } catch { $ok = $false } finally { $tcp.Close() }
      if (-not $ok) { Write-Host "[LỖI] Không nối được $LAN_URL (máy không ở mạng công ty?). Giữ nguyên cấu hình." }
    }
    if ($ok -and $cur -ne $want) {
      $bak = "$sf.bak_" + (Get-Date -Format 'yyyyMMdd_HHmmss')
      Copy-Item $sf $bak
      if ($cur) {
        $new = $txt.Replace('"ANTHROPIC_BASE_URL": "' + $cur + '"', '"ANTHROPIC_BASE_URL": "' + $want + '"')
        if ($new -eq $txt) { $cfg.env.ANTHROPIC_BASE_URL = $want; $new = $cfg | ConvertTo-Json -Depth 20 }
      } else {
        if (-not $cfg.env) { $cfg | Add-Member -NotePropertyName env -NotePropertyValue ([pscustomobject]@{}) }
        $cfg.env | Add-Member -NotePropertyName ANTHROPIC_BASE_URL -NotePropertyValue $want -Force
        $new = $cfg | ConvertTo-Json -Depth 20
      }
      [IO.File]::WriteAllText($sf, $new, (New-Object Text.UTF8Encoding $false))
      Write-Host "[OK] Endpoint -> $want (bản cũ: $bak). Khởi động lại VS Code / app Claude để áp dụng."
    } elseif ($ok) {
      Write-Host "[OK] Endpoint đã là $want."
    }
  }
}

Write-Host ""
Write-Host "Mở dự án:  code `"$Repo`"   → bấm biểu tượng Claude (✱) → lần đầu: gõ / → MCP, bật các server dự án."
Write-Host "Bộ nhớ dự án (máy mới): .venv/Scripts/python.exe -I tools/claude_memory.py restore"
