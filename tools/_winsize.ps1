param($Title, $W=1100, $H=800)
Add-Type @"
using System; using System.Runtime.InteropServices;
public class WS { [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr h,int x,int y,int w,int ht,bool r); [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h,int c); }
"@
$p = Get-Process Frolvy* | Where-Object { $_.MainWindowTitle -like "*$Title*" } | Select -First 1
[WS]::ShowWindow($p.MainWindowHandle, 9) | Out-Null
[WS]::MoveWindow($p.MainWindowHandle, 50, 50, $W, $H, $true)
