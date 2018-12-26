Set-Location $PSScriptRoot

$python = poetry run powershell -Command "Get-Command pythonw | Select -ExpandProperty Path"

Start-Process -NoNewWindow -FilePath $python -WorkingDirectory $PSScriptRoot -ArgumentList "-m echovr_tray_tool"
