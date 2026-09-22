#!/usr/bin/env python3
"""
Универсальная настройка окружения (Windows / macOS / Linux) — БЕЗ Homebrew.
Всё ставится через pip: faster-whisper (распознавание) + imageio-ffmpeg (ffmpeg) +
Pillow/opencv/numpy/fonttools. Затем предзагружается модель распознавания.

Запуск:  python3 setup.py   (на Windows:  python setup.py)
"""
import os, sys, subprocess
HERE=os.path.dirname(os.path.abspath(__file__))

def pip_install():
    print("==> ставлю python-зависимости (pip)…")
    req=os.path.join(HERE,"requirements.txt")
    try:
        subprocess.run([sys.executable,"-m","pip","install","--user","-r",req],check=True)
    except subprocess.CalledProcessError:
        subprocess.run([sys.executable,"-m","pip","install","-r",req],check=True)

def check_ffmpeg():
    sys.path.insert(0, os.path.join(HERE,"pipeline"))
    from env import ffmpeg_exe
    ff=ffmpeg_exe()
    r=subprocess.run([ff,"-hide_banner","-version"],capture_output=True,text=True)
    print("==> ffmpeg:", r.stdout.splitlines()[0] if r.stdout else ff)

def predownload_model():
    name=os.environ.get("WHISPER_MODEL","large-v3-turbo")
    print(f"==> скачиваю модель распознавания '{name}' (может занять несколько минут)…")
    from faster_whisper import WhisperModel
    WhisperModel(name, device="cpu", compute_type=os.environ.get("WHISPER_COMPUTE","int8"))
    print("    модель готова (в кэше).")

def verify():
    import PIL, cv2, numpy, fontTools, faster_whisper, imageio_ffmpeg
    print("==> проверка импортов: OK")

def main():
    pip_install()
    check_ffmpeg()
    verify()
    predownload_model()
    print("\n==> ГОТОВО. Среда настроена. Можно присылать видео.")

if __name__=="__main__":
    main()
