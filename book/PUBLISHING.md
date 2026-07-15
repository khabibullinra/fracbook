# Публикация методички

Краткая инструкция для преподавателя — как собрать книгу и опубликовать её на GitVerse Pages.

## Требования

- **Quarto ≥ 1.9.** На Linux преподавателя — ставится отдельно (см. ниже). На Windows у студентов — встроен в Positron.
- **Python ≥ 3.12**, **только через `.venv` в корне проекта.** Никаких системных установок `fracbook`.
- Доступ к gitverse по SSH (ключ уже настроен на машине преподавателя).

### Установка Quarto на Linux

Один раз:

```bash
wget -qO /tmp/quarto.tar.gz \
  https://github.com/quarto-dev/quarto-cli/releases/download/v1.9.38/quarto-1.9.38-linux-amd64.tar.gz
mkdir -p ~/.local/share/quarto-1.9.38
tar -xzf /tmp/quarto.tar.gz -C ~/.local/share/quarto-1.9.38 --strip-components=1
ln -sf ~/.local/share/quarto-1.9.38/bin/quarto ~/.local/bin/quarto
quarto --version  # → 1.9.38
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

В Positron (Windows у студентов) тот же эффект даёт команда **Quarto: Preview** в палитре команд.

## Сборка html

```bash
quarto render book/
```

Артефакт — в `book/_book/`. Эта папка в `.gitignore`, в `master` не попадает.

## Публикация на GitVerse Pages

Только преподаватель. Скрипт `tools/publish-pages.sh`:

```bash
./tools/publish-pages.sh
```

Что делает:
1. Проверяет, что рабочее дерево `master` чистое.
2. Проверяет, что в `PATH` есть Quarto ≥ 1.9.
3. `quarto render book/`.
4. Подготавливает worktree `.worktrees/pages` (создаёт при первом запуске, иначе — переиспользует и подтягивает свежий `origin/pages`).
5. Зеркалирует `book/_book/` → `.worktrees/pages/` (с удалением лишних файлов).
6. Копирует `tools/404.html` в worktree (Quarto его не генерирует).
7. Коммитит в `pages` с сообщением `publish: YYYY-MM-DD` и пушит `--force-with-lease`.

После выполнения сайт обновится на **https://khabibullinra.gitverse.site/fracbook/** через ~1–2 минуты (CDN-кэш GitVerse Pages).

### Опции скрипта

```bash
./tools/publish-pages.sh --dry-run    # показать шаги, ничего не менять
./tools/publish-pages.sh --no-render  # использовать уже собранный book/_book/
./tools/publish-pages.sh -h           # справка
```

## Troubleshooting

**Сайт показывает старую версию.**
CDN-кэш GitVerse Pages. Подождите 1–2 минуты или откройте в режиме инкогнито.

**`push --force-with-lease` отклонён.**
Кто-то (или вы в другой сессии) обновил `origin/pages`. Скрипт защищает от случайной перезаписи чужих изменений. Сделайте `git fetch origin pages` → `git -C .worktrees/pages merge --ff-only origin/pages` → повторите публикацию.

**`quarto` не найден.**
Активируйте `.venv` (если используете CLI) или установите Quarto по инструкции выше. В Positron `quarto` доступен автоматически.

**404 на сайте без явной причины.**
Содержимое ветки `pages` на сервере и локально разошлось. Сверьте `git -C .worktrees/pages log --oneline | head` с `git log origin/pages --oneline | head`. При расхождении — принудительно пересинхронизируйте.

**Push в `pages` случайно сделал студент.**
Откатите: `git -C .worktrees/pages reset --hard <предыдущий-коммит>` → `git push --force-with-lease origin pages`.
