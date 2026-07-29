# Публикание методички

Краткая инструкция для преподавателя — как собрать книгу и опубликовать её на GitVerse Pages.

## Требования

- **Quarto** строго той версии, что в `.quarto-version` (на момент написания — 1.9.38). На Linux преподавателя — ставится отдельно (см. ниже). На Windows у преподавателя — встроен в Positron.
  - **Positron игнорирует `.quarto-version`** и использует свой встроенный Quarto. Поэтому на Windows-стороне версию всё равно надо сверять глазами.
- **Python ≥ 3.12**, **только через `.venv` в корне проекта.** Никаких системных установок `fracbook`.
- Доступ к GitVerse по SSH (ключ уже настроен на машине преподавателя).

### Установка Quarto на Linux

Один раз — версия подставляется из `.quarto-version`:

```bash
QV=$(cat .quarto-version)
wget -qO /tmp/quarto.tar.gz \
  "https://github.com/quarto-dev/quarto-cli/releases/download/v${QV}/quarto-${QV}-linux-amd64.tar.gz"
mkdir -p ~/.local/share/quarto-${QV}
tar -xzf /tmp/quarto.tar.gz -C ~/.local/share/quarto-${QV} --strip-components=1
ln -sf ~/.local/share/quarto-${QV}/bin/quarto ~/.local/bin/quarto
quarto --version  # должно совпасть с .quarto-version
```

`~/.local/bin` уже в `PATH` (добавляется `~/.profile` при логине).

### Настройка `.venv` (все участники)

Один раз после клона:

```bash
python3 -m venv .venv
```

Активация:

| ОС / shell | Команда |
|---|---|
| Linux, macOS, Git Bash | `source .venv/bin/activate` |
| Windows (cmd) | `.venv\Scripts\activate.bat` |
| Windows (PowerShell) | `.venv\Scripts\Activate.ps1` |

Установка пакета и dev-зависимостей:

```bash
pip install -e .[dev]
```

Проверка:

```bash
python -c "import fracbook; print(fracbook.__version__)"
pytest -q
```

## Локальный просмотр (без публикации)

Из корня проекта, **с активированным `.venv`**:

```bash
quarto preview book/
```

Откроется в браузере по адресу `http://localhost:XXXX`, авто-перерендер при изменении `.qmd`/`.py`/конфигов.

В Positron (Windows у преподавателя) тот же эффект даёт команда **Quarto: Preview** в палитре команд.

> **Почему нет pre-render хука в `_quarto.yml`?** Quarto вызывает pre-render хуки через `cmd /c` на Windows и через `sh -c` на Linux — единого кросс-платформенного механизма нет. Студент с битым `fracbook` всё равно не сможет закоммитить: CI гоняет `pytest` + `quarto render` как отдельные шаги, и красный CI блокирует PR. Локальная страховка — та же тройка `pytest -q && ruff check src tests && quarto render book/`, что и в CI.

## Сборка html

```bash
quarto render book/
```

Артефакт — в `book/_book/`. Эта папка в `.gitignore`, в `master` не попадает.

## Публикация на GitVerse Pages

Только преподаватель. Скрипт `tools/publish_pages.py` (кросс-платформенный, на Python). Запускается через тонкую обёртку:

| ОС / shell | Команда |
|---|---|
| Linux, macOS, Git Bash | `./tools/publish-pages.sh` |
| Windows (cmd) | `tools\publish-pages.cmd` |
| Windows (PowerShell) | `tools\publish-pages.ps1` |
| Любая, напрямую | `python tools/publish_pages.py` |

Что делает:
1. Проверяет, что рабочее дерево `master` чистое.
2. Проверяет, что `quarto` есть в `PATH` и версия ≥ 1.9. Сверяет с `.quarto-version`, если тот есть.
3. Прогоняет `pytest -q` и `ruff check src tests` (если не передан `--no-tests`).
4. `quarto render book/`.
5. Подготавливает worktree `.worktrees/pages` (создаёт при первом запуске, иначе — переиспользует и подтягивает свежий `origin/pages`).
6. Очищает worktree (кроме `.git`) и копирует туда `book/_book/` + `tools/404.html`.
7. Коммитит в `pages` с сообщением `publish: YYYY-MM-DD` и пушит `--force-with-lease`.

После выполнения сайт обновится на **https://khabibullinra.gitverse.site/fracbook/** через ~1–2 минуты (CDN-кэш GitVerse Pages).

### Опции скрипта

```bash
./tools/publish-pages.sh --dry-run     # показать шаги, ничего не менять
./tools/publish-pages.sh --no-render   # использовать уже собранный book/_book/
./tools/publish-pages.sh --no-tests    # пропустить pytest/ruff
./tools/publish-pages.sh --prune       # в конце подчистить устаревшие worktree-записи
./tools/publish-pages.sh -h            # справка
```

## CI

`.gitverse/workflows/ci.yaml` на каждый push/PR в `master` гоняет:
1. `pip install -e .[dev]`
2. `ruff check src tests`
3. `pytest -q`
4. `quarto render book/` — smoke-test `.qmd` (ловятся синтаксические ошибки, битые crossref, неработающие Python-чанки)
5. Загружает собранный `book/_book/` как артефакт `book-html` (на 7 дней) — можно посмотреть глазами прямо в PR.

Публикация в Pages из CI **не** делается. Это сознательное упрощение: в Pages пушит только преподаватель, через `tools/publish_pages.py`.

## Troubleshooting

**Сайт показывает старую версию.**
CDN-кэш GitVerse Pages. Подождите 1–2 минуты или откройте в режиме инкогнито.

**`push --force-with-lease` отклонён.**
Кто-то (или вы в другой сессии) обновил `origin/pages`. Скрипт защищает от случайной перезаписи чужих изменений. Сделайте `git fetch origin pages` → `git -C .worktrees/pages merge --ff-only origin/pages` → повторите публикацию.

**`quarto` не найден.**
Активируйте `.venv` (если используете CLI) или установите Quarto по инструкции выше. В Positron `quarto` доступен автоматически.

**Версия Quarto в `PATH` не совпадает с `.quarto-version`.**
Преподаватель увидит предупреждение в начале `publish_pages.py`. На Linux — обновите ссылку `~/.local/bin/quarto` на нужную версию. На Windows (Positron) — Positron-Quarto игнорирует файл, синхронизируйте версию через обновление Positron.

**404 на сайте без явной причины.**
Содержимое ветки `pages` на сервере и локально разошлось. Сверьте `git -C .worktrees/pages log --oneline | head` с `git log origin/pages --oneline | head`. При расхождении — принудительно пересинхронизируйте.

**Push в `pages` случайно сделал студент.**
Откатите: `git -C .worktrees/pages reset --hard <предыдущий-коммит>` → `git push --force-with-lease origin pages`.

**`pytest -q` падает на pre-render хуке.**
Сначала чините тесты в `src/fracbook/`. Pre-render хука в проекте сейчас нет (см. выше), так что это сообщение — на случай, если вы добавите её сами.
