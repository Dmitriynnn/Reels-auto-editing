# Reels-auto-editing

Автоматический монтаж вертикальных разговорных reels 1080×1920 в фиксированном
стиле: вырезание пауз, авто-ускорение под темп Instagram, хук, секции «совет N/3»,
субтитры по слову с акцентами, вставки-стикеры и карточки-сравнения, «дышащая»
камера, свуши, финальный призыв. Всё оформление — над лицом (автодетекция), с учётом
интерфейса Instagram, без наложений. **Работает на Windows и macOS/Linux** — установка
целиком через pip (Homebrew не нужен).

## Как это работает
Claude (в приложении Claude Code) читает эту репу, ставит окружение и монтирует
любое присланное видео. Механику делают скрипты в `pipeline/`, творческие тексты
Claude берёт из транскрипта и кладёт в `edit_plan.json`.

## Быстрый старт (для человека)
Открой **`docs/GUIDE.pdf`** — пошаговая инструкция для не-технических пользователей.
Или скопируй первый промпт из **`SETUP_PROMPT.md`** в новый чат Claude Code и пришли видео.

## Быстрый старт (вручную)
```
python3 setup.py                                # venv + зависимости + модель small + самопроверка (печатает READY)
python3 pipeline/make_reel.py video.mov pipeline/edit_plan.example.json out.mp4
```
`setup.py` создаёт изолированный venv (`~/.reels-auto-venv`), ставит всё нужное (ffmpeg из imageio-ffmpeg,
opencv, Pillow, faster-whisper), качает лёгкую модель распознавания **small (~250 МБ)** и проверяет себя.
Путь venv-python пишется в `.reels_runner`; скрипты пайплайна сами уходят в это окружение, даже если их
вызвать системным `python3`. Скорость по умолчанию — `"auto"`, паузы вырезаются автоматически.
Распознавание речи автоматическое — вставлять текст руками не нужно.

## Состав
```
setup.py                     кросс-платформенная установка (Win/Mac/Linux, всё через pip)
setup.sh / setup.ps1         тонкие обёртки над setup.py (mac-linux / windows)
requirements.txt             python-зависимости (faster-whisper, imageio-ffmpeg, Pillow, opencv, …)
SETUP_PROMPT.md              первый промпт для чистого Claude
skill/REELS_STYLE_SKILL.md   инструкция монтажа (мозг)
skill/STYLE_GUIDE.md         визуальная спецификация стиля
pipeline/                    транскрипт, база, детекция лица, оформление, камера, звук, сборка
pipeline/edit_plan.example.json  пример творческого плана
assets/fonts/                OFL-шрифты (Oswald, Montserrat, Caveat, Playfair) + лицензии
assets/models/               модель детекции лица (yunet). Модель whisper качает setup.sh
docs/GUIDE.pdf               PDF-инструкция для пользователя
```

## Требования
Windows, macOS или Linux; Python 3.9+; интернет и ~1–1.5 ГБ свободного места; при первом
запуске разрешить выполнение команд. Homebrew/компиляция не нужны — ffmpeg приходит из
`imageio-ffmpeg`, распознавание — `faster-whisper` (модель small). Первая настройка 5–10 минут.

## Лицензии
- Код — MIT (`LICENSE`).
- Шрифты — OFL (`assets/fonts/OFL-*.txt`).
- Модель лица yunet — Apache-2.0 (OpenCV Zoo).
- Модель whisper — MIT (ggerganov/whisper.cpp), качается при установке.
- Оригинальные коммерческие шрифты (Stadium/Gramatika/Anticva/Baystar) НЕ включены.
