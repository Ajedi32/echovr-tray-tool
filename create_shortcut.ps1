param (
   [string]$Arguments = "",
   [string]$Destination = $PSScriptRoot
)

$python = poetry run powershell -Command "Get-Command pythonw | Select -ExpandProperty Path"

# See https://docs.microsoft.com/en-us/powershell/scripting/samples/creating-.net-and-com-objects--new-object-?view=powershell-6#creating-com-objects-with-new-object
$WshShell = New-Object -comObject WScript.Shell

# See https://support.microsoft.com/en-us/help/244677/how-to-create-a-desktop-shortcut-with-the-windows-script-host
$Shortcut = $WshShell.CreateShortcut("$Destination\Echo VR Tray Tool.lnk")
$Shortcut.TargetPath = $python
$Shortcut.WindowStyle = 4 # 3=Maximized, 7=Minimized, 4=Normal
$Shortcut.Arguments = "-m echovr_tray_tool $Arguments"
$Shortcut.WorkingDirectory = $PSScriptRoot
$Shortcut.Save()
