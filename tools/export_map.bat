@echo off
chcp 65001 >nul
rem Copies JourneyMap explored-map tiles (day view) into jm_export, replacing "~" in folder names with "-",
rem so Claude can read them. It only copies; nothing in the journeymap folder is changed or deleted.
powershell -NoProfile -ExecutionPolicy Bypass -Command "$s=Join-Path '%~dp0' 'journeymap\data\mp'; $d=Join-Path '%~dp0' 'jm_export'; $n=0; Get-ChildItem -LiteralPath $s -Directory | ForEach-Object { $w=$_; Get-ChildItem -LiteralPath $w.FullName -Directory | Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'day') } | ForEach-Object { $t=Join-Path $d (($w.Name -replace '~','-')+'\'+$_.Name+'\day'); New-Item -ItemType Directory -Force -Path $t | Out-Null; Copy-Item -Path (Join-Path $_.FullName 'day\*.png') -Destination $t -Force; $n++ } }; Write-Host ('Copied ' + $n + ' map folders to ' + $d)"
echo.
echo 完成：已把 JourneyMap 地圖複製到 jm_export 資料夾。回到 Claude 說「好了」即可。
echo.
pause
