Set-ItemProperty `
  -Path Registry::HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run `
  -Name "Echo VR Tray Tool" `
  -Value "powershell `"$PSScriptRoot\echovr_tray_tool.ps1`""
