# fracbook

Методическое пособите (книга) по курсу "Основы гидравлического разрыва пласта" (ГРП).
Инженерные расчёты производительности добывающих скважин с трещинами ГРП:
аналитические модели, гидродинамические симуляторы.

## Стек

- **Quarto** — основной инструмент публикации (`.qmd` файлы с prose + кодом).
- **Python** — примеры расчётов и ядро `fracbook`.
- **fracbook** — локальный пакет расчётов в `src/fracbook/`, устанавливается
  в editable-режиме (`pip install -e .[dev]`). Внешняя `fracpy` может
  использоваться как зависимость через `pyproject.toml`, когда появится.

## Выходные форматы

- `html` — базовый вариант (просмотр/веб). Сейчас публикуется на GitVerse Pages.
- `pdf` — вариант для печати; собирается локально преподавателем,
  в Pages **не** публикуется (по решению команды).

## Язык и оформление

- Текст методички — русский.
- Имена файлов, идентификаторы, сообщения коммитов — на усмотрение автора,
  но содержимое документации всегда по-русски.
- Лицензия — MIT (см. `LICENSE`).

## Карта репозитория

| Путь | Назначение |
|---|---|
| `src/fracbook/` | Пакет расчётов (ядро методички). |
| `tests/` | `pytest` для `src/fracbook/`. |
| `book/` | Quarto-книга (`.qmd`, конфиги, изображения). Стиль — в `book/CONTRIBUTING.md`, публикация — в `book/PUBLISHING.md`. |
| `notebooks/` | Quarto-проект с экспериментальными ноутбуками (`drafts/`, `reviewed/`, `scratch/`). |
| `models/` | Модели гидродинамических симуляторов (`models/<simulator>/<NN-slug>/`). Новую модель заводить копированием `models/<simulator>/_template/`. |
| `docs/` | Документация репо: роли (`CONTRIBUTING.md`), архитектурные решения (`decisions/`). |
| `tools/` | Скрипты поддержки. Публикация — `publish_pages.py` (кросс-платформенный драйвер) + шимы `publish-pages.sh`/`.cmd`/`.ps1`; статический 404 — `tools/404.html`. |
| `.gitverse/workflows/` | CI (smoke-test: `pytest` + `ruff`). |

## Конвенции для агентов

Что делать:
- Перед коммитом в `master`, если менялся `src/fracbook/` или `book/`
  (или `notebooks/` для ноутбуков), прогнать `pytest -q`, `ruff check src tests`
  и `quarto render book/` (или `notebooks/` если менялся). Это та же
  тройка, что в CI — иначе красный билд.
- Новый код — в `src/fracbook/`, новые эксперименты — в `notebooks/drafts/`.
  Ноутбук не должен содержать новой математики, только вызовы `fracbook`.
- Стиль кода и оформление книги — в `book/CONTRIBUTING.md` и ruff-конфиге
  в `pyproject.toml`.

Что **не** делать (конвенция, не репозиторное ограничение):
- Не редактировать и не коммитить `book/_book/`, `book/_freeze/`,
  `notebooks/_site/` — это выход сборки.
- **Не пушить в ветку `pages`** — это делает только преподаватель
  через `tools/publish_pages.py` (или шимы `tools/publish-pages.{sh,cmd,ps1}`).
  Агент не инициирует push в `pages`, даже если пользователь явно попросил
  собрать книгу локально.
- Не коммитить `.venv/`, `_freeze/`, `.ipynb_checkpoints/`, бинарь
  симуляторов (`.geos`, `.unrst`, `.INIT`, `.EGRID`, `.MSG`, `.PRT`,
  `.log`).
- Не редактировать файлы в корне репо без необходимости — структура
  зафиксирована в этой карте.

## Публикация

Подробно — в `book/PUBLISHING.md`. Кратко — пайплайн кросс-платформенный
(драйвер на Python, шимы под основные оболочки):

1. Сборка html (любая ОС):
   ```bash
   quarto render book/
   ```
   Артефакт — `book/_book/`, в `master` не коммитится.

2. Публикация в Pages (только преподаватель, любая ОС):

   | ОС / shell | Команда |
   |---|---|
   | Linux, macOS, Git Bash | `./tools/publish-pages.sh` |
   | Windows (cmd) | `tools\publish-pages.cmd` |
   | Windows (PowerShell) | `tools\publish-pages.ps1` |
   | Любая, напрямую | `python tools/publish_pages.py` |

   Шимы — тонкие обёртки, вся логика в `publish_pages.py`: проверка
   чистого дерева → `pytest` + `ruff` → `quarto render` → копирование
   в worktree `.worktrees/pages` → `commit` + `push --force-with-lease`.

3. Сверка версии Quarto: файл `.quarto-version` в корне. Quarto CLI
   (Linux, macOS) подхватывает его автоматически; **Positron-Quarto
   на Windows игнорирует `.quarto-version`** — там версию сверяют
   глазами с этим файлом и обновляют Positron при расхождении.

После публикации сайт обновляется на
**https://khabibullinra.gitverse.site/fracbook/** через ~1–2 минуты
(CDN-кэш GitVerse Pages).

## Рабочий процесс CI

`.gitverse/workflows/ci.yaml` запускает smoke-test на каждый push и PR
в `master` на чистом `gv02-runnerXX` (Ubuntu):

1. `pip install -e .[dev]` — тянет Quarto-зависимости (`notebook`,
   `matplotlib`, `nbformat`, `nbclient` — все транзитивно через `notebook>=7`).
2. `ruff check src tests`
3. `pytest -q`
4. `quarto render book/` — ловит синтаксические ошибки `.qmd`, битые
   crossref и неработающие Python-чанки.
5. `actions/upload-artifact` — кладёт собранный `book/_book/` как
   артефакт `book-html` (хранится 7 дней, можно скачать прямо из PR
   и посмотреть глазами).

Деплоя в Pages из CI **нет** — это сознательное упрощение: в `pages`
пушит только преподаватель через `tools/publish_pages.py`.