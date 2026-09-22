#!/usr/bin/env bash
# macOS / Linux: тонкая обёртка над кросс-платформенным setup.py.
# Всё ставится через pip (ffmpeg — из пакета imageio-ffmpeg, распознавание — faster-whisper).
set -e
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$(command -v python3 || command -v python)"
[ -z "$PY" ] && { echo "Не найден Python 3. Установи Python 3.9+ и повтори."; exit 1; }
"$PY" "$HERE/setup.py"
