& "$PSScriptRoot\create_shortcut.ps1"
Copy-Item "$PSScriptRoot\Echo VR Tray Tool.lnk" -Destination "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
