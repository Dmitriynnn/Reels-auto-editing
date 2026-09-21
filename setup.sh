#!/usr/bin/env bash
# Установка окружения для авто-монтажа reels. macOS (brew) или Linux (apt).
# Ставит ffmpeg + whisper-cpp, python-зависимости и качает модель whisper (~574 МБ).
set -e
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODEL_DIR="$HERE/assets/models"
MODEL="$MODEL_DIR/ggml-large-v3-turbo-q5_0.bin"
MODEL_URL="https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo-q5_0.bin"

echo "==> OS check"
OS="$(uname -s)"

install_mac() {
  command -v brew >/dev/null || { echo "Homebrew не найден. Установи: https://brew.sh"; exit 1; }
  echo "==> brew: ffmpeg, whisper-cpp"
  brew list ffmpeg >/dev/null 2>&1 || brew install ffmpeg
  brew list whisper-cpp >/dev/null 2>&1 || brew install whisper-cpp
}
install_linux() {
  echo "==> apt: ffmpeg (whisper-cpp собери отдельно, если нет)"
  sudo apt-get update -y && sudo apt-get install -y ffmpeg python3-pip curl
  command -v whisper-cli >/dev/null || echo "!! whisper-cli не найден: собери whisper.cpp и положи whisper-cli в PATH"
}
case "$OS" in
  Darwin) install_mac ;;
  Linux)  install_linux ;;
  *) echo "Неизвестная ОС: $OS (нужен ffmpeg + whisper-cli в PATH)";;
esac

echo "==> python зависимости"
python3 -m pip install --user -r "$HERE/requirements.txt"

echo "==> модель whisper"
mkdir -p "$MODEL_DIR"
if [ -f "$MODEL" ]; then echo "модель уже на месте"; else
  echo "качаю модель (~574 МБ)…"; curl -L --fail -o "$MODEL" "$MODEL_URL"
fi

echo "==> проверка"
command -v ffmpeg >/dev/null && echo "ffmpeg OK" || echo "ffmpeg НЕТ"
command -v whisper-cli >/dev/null && echo "whisper-cli OK" || echo "whisper-cli НЕТ"
python3 -c "import PIL,cv2,numpy,fontTools;print('python-deps OK')"
[ -f "$MODEL" ] && echo "модель OK"
echo "==> ГОТОВО. Среда настроена."
