"""
Самопроверка окружения. Запускается интерпретатором venv из setup.py.
Проверяет весь путь монтажа: библиотеки, ffmpeg-бинарь, декод аудио и загрузку
модели распознавания (small). Печатает SELFTEST_OK или SELFTEST_FAIL: <причина>.
Модель грузится с диска/из кэша — заодно это её предзагрузка.
"""
import os, sys, subprocess, tempfile


def main():
    try:
        import PIL, numpy, cv2, imageio_ffmpeg  # noqa: F401
    except Exception as e:
        print("SELFTEST_FAIL: не установились библиотеки (%s)" % e); return 1
    try:
        ff = imageio_ffmpeg.get_ffmpeg_exe()
        wav = os.path.join(tempfile.mkdtemp(), "t.wav")
        subprocess.run([ff, "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi",
                        "-i", "sine=frequency=220:duration=2", "-ar", "16000", "-ac", "1", wav], check=True)
    except Exception as e:
        print("SELFTEST_FAIL: ffmpeg не работает (%s)" % e); return 1
    try:
        from faster_whisper import WhisperModel
        name = os.environ.get("WHISPER_MODEL", "small")
        m = WhisperModel(name, device="cpu", compute_type="int8")
        segs, _ = m.transcribe(wav, language="ru")
        list(segs)  # прогнать генератор — реальный проход модели
    except Exception as e:
        print("SELFTEST_FAIL: распознавание речи не запустилось (%s)" % e); return 1
    print("SELFTEST_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
