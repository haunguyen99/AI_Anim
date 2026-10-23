# Make the Cascadeur window visible WITHOUT taking keyboard focus: restore it if minimised, move it onto the
# secondary monitor (user's choice 2026-10-21: "Màn hình 2"), keep it always-on-top there.
# Cascadeur only writes RenderToFile images while its viewport is drawn (not minimised / not covered).
# Focus stays with the user's window: on 2026-10-21 a key typed elsewhere ("F" = Add/Remove key) reached Cascadeur
# after the old version activated it and deleted the key being posed.
# Usage: powershell -ExecutionPolicy Bypass -File tools/cascadeur/front.ps1            (show on monitor 2, on top, no focus)
#        powershell -ExecutionPolicy Bypass -File tools/cascadeur/front.ps1 -Release   (drop always-on-top)
param([switch]$Release)
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class Win {
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);
  [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr h);
  [DllImport("user32.dll")] public static extern bool IsZoomed(IntPtr h);
  [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr after, int x, int y, int cx, int cy, uint flags);
}
"@
Add-Type -AssemblyName System.Windows.Forms
$p = Get-Process cascadeur -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
if (-not $p) { Write-Output "cascadeur window not found"; exit 1 }
$h = $p.MainWindowHandle
$NOACT = 0x0010
if ($Release) {
  [void][Win]::SetWindowPos($h, [IntPtr](-2), 0, 0, 0, 0, 0x0001 -bor 0x0002 -bor $NOACT)   # HWND_NOTOPMOST
  Write-Output "released"; exit 0
}
if ([Win]::IsIconic($h) -or [Win]::IsZoomed($h)) { [void][Win]::ShowWindow($h, 4) }        # SW_SHOWNOACTIVATE (restore, no focus)
$scr = [System.Windows.Forms.Screen]::AllScreens | Where-Object { -not $_.Primary } | Select-Object -First 1
if (-not $scr) { $scr = [System.Windows.Forms.Screen]::PrimaryScreen }
$wa = $scr.WorkingArea
# same client size as a maximised window (Windows hangs the 8 px frame off-screen); the render scale follows the viewport size
$B = 8
$ok = [Win]::SetWindowPos($h, [IntPtr](-1), $wa.X - $B, $wa.Y - $B, $wa.Width + 2 * $B, $wa.Height + 2 * $B, $NOACT)   # HWND_TOPMOST, no focus
Write-Output ("on top of {0} (no focus): {1}" -f $scr.DeviceName, $ok)
