#!/usr/bin/env python3
"""
Установщик окружения для авто-монтажа рилсов. Windows / macOS / Linux.

Делает всё сам и проверяет себя:
  1) создаёт изолированный venv (обходит блокировку системного pip / PEP 668);
  2) ставит лёгкие зависимости (Pillow, opencv, numpy, faster-whisper, imageio-ffmpeg —
     ffmpeg-бинарь приходит с пакетом, системный не нужен);
  3) качает МАЛЕНЬКУЮ модель распознавания (small, ~250 МБ) и делает самопроверку
     всего пути монтажа;
  4) пишет путь venv-python в .reels_runner — дальше весь пайплайн идёт через него.

Итог: строка READY (и RUNNER=<путь>) при успехе, либо SETUP_FAILED: <одна причина>.
Запуск:  python3 setup.py   (Windows:  python setup.py)
"""
import os, sys, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
VENV = os.path.expanduser(os.path.join("~", ".reels-auto-venv"))
REQ = os.path.join(HERE, "requirements.txt")
RUNNER_FILE = os.path.join(HERE, ".reels_runner")


def venv_python(venv):
    return os.path.join(venv, "Scripts", "python.exe") if os.name == "nt" else os.path.join(venv, "bin", "python")


def run(cmd, timeout=1800):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def fail(reason):
    print("SETUP_FAILED: " + reason)
    sys.exit(1)


def main():
    print("==> создаю изолированное окружение (venv)…")
    if not os.path.exists(venv_python(VENV)):
        r = run([sys.executable, "-m", "venv", VENV])
        if r.returncode != 0 or not os.path.exists(venv_python(VENV)):
            fail("не удалось создать venv. Установи Python 3.9+ с python.org (галочка Add to PATH) и повтори. %s" % (r.stderr or "").strip()[:200])
    vpy = venv_python(VENV)

    print("==> ставлю зависимости (это несколько минут)…")
    run([vpy, "-m", "pip", "install", "--upgrade", "pip"], timeout=600)
    r = run([vpy, "-m", "pip", "install", "-r", REQ], timeout=2400)
    if r.returncode != 0:
        # одна повторная попытка с большим таймаутом соединения
        r = run([vpy, "-m", "pip", "install", "--default-timeout=180", "-r", REQ], timeout=2400)
    if r.returncode != 0:
        tail = (r.stderr or r.stdout or "").strip().splitlines()[-1:] or [""]
        fail("не установились зависимости (проверь интернет и место на диске). %s" % tail[0][:200])

    # раннер — чтобы весь пайплайн шёл через venv даже при вызове системным python
    try:
        with open(RUNNER_FILE, "w", encoding="utf-8") as fh:
            fh.write(vpy)
    except Exception as e:
        fail("не удалось записать .reels_runner (%s)" % e)

    print("==> качаю модель распознавания (small, ~250 МБ) и проверяю себя…")
    os.environ.setdefault("WHISPER_MODEL", "small")
    r = run([vpy, os.path.join(HERE, "pipeline", "selftest.py")], timeout=2400)
    out = (r.stdout or "") + (r.stderr or "")
    if "SELFTEST_OK" not in out:
        line = "SELFTEST_FAIL" in out and out[out.index("SELFTEST_FAIL"):].splitlines()[0] or (out.strip().splitlines()[-1:] or [""])[0]
        fail("самопроверка не прошла: %s" % line[:200])

    print("RUNNER=%s" % vpy)
    print("READY. Среда готова, можно присылать видео.")


if __name__ == "__main__":
    try:
        main()
    except subprocess.TimeoutExpired:
        fail("установка/загрузка модели заняла слишком долго (медленный интернет). Повтори при стабильной сети.")
    except KeyboardInterrupt:
        fail("прервано")
