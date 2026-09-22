# Windows (PowerShell): обёртка над кросс-платформенным setup.py.
# Всё ставится через pip (ffmpeg — imageio-ffmpeg, распознавание — faster-whisper). Homebrew не нужен.
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$py = (Get-Command python -ErrorAction SilentlyContinue)
if (-not $py) { $py = (Get-Command python3 -ErrorAction SilentlyContinue) }
if (-not $py) { Write-Error "Не найден Python 3. Установи Python 3.9+ (python.org) и повтори."; exit 1 }
& $py.Path (Join-Path $here "setup.py")
