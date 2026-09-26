"""
Гарантирует, что тяжёлый код (faster-whisper, opencv, Pillow) выполняется в venv,
созданном setup.py. Если скрипт запущен системным python без зависимостей —
перезапускает сам себя интерпретатором venv (путь берётся из файла .reels_runner
в корне репозитория). Так «один промпт → видео → рилс» переживает вызов не тем
python: пайплайн сам уходит в правильное окружение.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNNER_FILE = os.path.join(ROOT, ".reels_runner")


def venv_python(venv):
    if os.name == "nt":
        return os.path.join(venv, "Scripts", "python.exe")
    return os.path.join(venv, "bin", "python")


def runner_path():
    try:
        with open(RUNNER_FILE, encoding="utf-8") as fh:
            p = fh.read().strip()
        return p or None
    except Exception:
        return None


def ensure_venv():
    """Если faster_whisper недоступен, а venv-раннер есть — перезапуститься в нём."""
    try:
        import faster_whisper  # noqa: F401
        return
    except Exception:
        pass
    runner = runner_path()
    if runner and os.path.exists(runner):
        if os.path.abspath(runner) != os.path.abspath(sys.executable):
            os.execv(runner, [runner] + sys.argv)
    # раннера нет — пусть настоящая ошибка импорта всплывёт выше по стеку
