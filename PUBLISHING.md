# Публикация и работа с репозиторием

Это общая инструкция: как развернуть проект у себя, как вести разработку,
как изменения попадают на сайт.

Узкие инструкции (только про сборку книги) — в `book/PUBLISHING.md`.
Архитектурные решения — в `docs/decisions/`.

## Содержание

- [Требования к окружению](#требования-к-окружению)
- [Установка инструментов](#установка-инструментов)
- [Первый запуск](#первый-запуск)
- [Workflow разработки](#workflow-разработки)
- [Публикация на сайт](#публикация-на-сайт)
- [Защита веток (настраивается один раз)](#защита-веток-настраивается-один-раз)
- [FAQ](#faq)

## Требования к окружению

| Инструмент | Версия | Зачем |
|---|---|---|
| **Git** | ≥ 2.40 | Контроль версий, PR, push |
| **Python** | ≥ 3.12 | Расчётная библиотека `fracbook`, рендер графиков |
| **Quarto CLI** | 1.9.38 (зафиксировано в `.quarto-version`) | Сборка книги, OJS-интерактив |

ОС: Linux, macOS, Windows 10/11. Всё работает кросс-платформенно.

## Установка инструментов

### Git

**Windows**: [Git for Windows](https://gitforwindows.org/) — ставится
стандартным инсталлятором, по умолчанию `C:\Program Files\Git\`. После
установки `git --version` в любом терминале.

**Linux**: `sudo apt install git` (или эквивалент дистрибутива).

**macOS**: `brew install git` или `xcode-select --install`.

### Python ≥ 3.12

**Windows**: ставится через официальный installer с [python.org](https://www.python.org/downloads/)
(обязательно галка «Add Python to PATH»). Или через `winget install Python.Python.3.12`.

**Linux**: `sudo apt install python3.12 python3.12-venv python3.12-dev` (или эквивалент).

**macOS**: `brew install python@3.12`.

Проверка: `python --version` показывает 3.12.x.

### Quarto CLI 1.9.38

**Версия зафиксирована** в файле `.quarto-version` в корне репо. Несовпадение
версии с тем, что в `.quarto-version`, — источник трудноуловимых багов
рендера.

**Windows** (PowerShell):

```powershell
$ProgressPreference = 'SilentlyContinue'
$tmp = Join-Path $env:TEMP 'quarto.zip')
Invoke-WebRequest -Uri 'https://github.com/quarto-dev/quarto-cli/releases/download/v1.9.38/quarto-1.9.38-win.zip' -OutFile $tmp
Expand-Archive -Path $tmp -DestinationPath "$env:USERPROFILE\Tools\Quarto" -Force
[Environment]::SetEnvironmentVariable('Path', $env:Path + ";$env:USERPROFILE\Tools\Quarto\bin", 'User')
# перезапустить PowerShell
quarto --version  # должно быть 1.9.38
```

**Linux**:

```bash
QV=$(cat .quarto-version)
wget -qO /tmp/quarto.tar.gz "https://github.com/quarto-dev/quarto-cli/releases/download/v${QV}/quarto-${QV}-linux-amd64.tar.gz"
mkdir -p ~/.local/share/quarto-${QV}
tar -xzf /tmp/quarto.tar.gz -C ~/.local/share/quarto-${QV} --strip-components=1
ln -sf ~/.local/share/quarto-${QV}/bin/quarto ~/.local/bin/quarto
quarto --version
```

**macOS** (через `brew` отдаёт свою версию, не подходит — лучше руками как
для Linux, только macOS-архив).

Проверка после установки в **новом** терминале: `quarto --version` →
`1.9.38`.

## Первый запуск

```bash
# 1. Склонировать
git clone https://gitverse.ru/khabibullinra/fracbook.git
cd fracbook

# 2. Создать .venv в корне (обязательно в корне, не в подпапках)
python3.12 -m venv .venv

# 3. Активировать
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Windows cmd:
.\.venv\Scripts\activate.bat

# 4. Поставить пакет в editable + dev-зависимости (pytest, ruff, plotly, kaleido)
pip install -e .[dev]

# 5. Проверить
pytest -q                # все тесты зелёные
ruff check src tests     # линтер чист
quarto --version         # 1.9.38
```

Если в Positron — `interpreter` в палитре команд → выбрать `.venv`. Пакет
`fracbook` подхватится автоматически.

## Workflow разработки

```
feature/..., student/<ник>/... ──PR (review)──> dev
                                            (CI: smoke)
                                              │
                                              ▼ (PR преподавателя, релиз)
                                            master (CI: smoke + render + auto-publish pages)
                                              │
                                              ▼
                                            pages
```

### Для студента (подробно — `docs/student-workflow.md`)

1. Форк `khabibullinra/fracbook` в свой аккаунт.
2. `git clone` своего форка.
3. Ветка `student/<ник>/<короткое-описание>`.
4. Работа, коммиты.
5. `git push` в **свой форк**.
6. PR из своего форка в `khabibullinra/fracbook:dev`.
7. Ревью от преподавателя, доработки, мерж.

### Для преподавателя

1. Ревью PR в `dev` (от студентов и соавторов).
2. Когда накопилось достаточно изменений — PR из `dev` в `master`.
3. После мержа в `master` CI автоматически публикует в `pages`.

## Публикация на сайт

**Полностью автоматическая.** Ручных действий не требуется.

1. PR `dev → master` смёржен.
2. CI job `test` прогоняется на `master`: `pytest` + `ruff` + `quarto render book/`.
3. Если `test` зелёный — CI job `publish` клонирует ветку `pages`, копирует
   `book/_book/` + `tools/404.html`, коммитит `publish: YYYY-MM-DD`,
   пушит `force-with-lease`.
4. Через 1–2 минуты (CDN-кэш GitVerse Pages) сайт обновляется на
   **https://khabibullinra.gitverse.site/fracbook/**.

Если CI красный — мерж в `pages` не происходит, сайт продолжает показывать
предыдущую версию. Чинить в `master` (или откатить коммит), дождаться зелёного
CI.

### Что публикуется

- Содержимое `book/_book/` (после `quarto render book/`)
- `tools/404.html` как статический `404.html` для GitVerse Pages
- **Не** публикуется: `src/`, `notebooks/`, `models/`, `tests/`, `docs/`
  (эти папки — для разработки, не для студентов)

## Защита веток (настраивается один раз)

В UI GitVerse (один раз, при первом подключении CI-публикации):

### 1. Создать bot-токен для CI

- **Settings → Tokens → New token** (или `https://gitverse.ru/<owner>/fracbook/-/settings/tokens`)
- Имя: `fracbook-pages-bot`
- Права: `Repository: Write` (минимально достаточно для push в `pages`)
- Срок: 1 год (с ротацией)
- **Сохранить токен сразу** — после закрытия страницы не покажется

### 2. Положить токен в Secrets репо

- **Settings → Secrets → New secret** (или `https://gitverse.ru/<owner>/fracbook/-/settings/secrets`)
- Имя: `PAGES_TOKEN`
- Значение: токен из шага 1
- Доступ: только `master` (если UI позволяет), иначе — все workflow

### 3. Включить branch protection

Для `master`:
- **Settings → Branches → master → Edit**
- ✅ Require pull request before merging
- ✅ Require approvals: 1
- ✅ Require status checks to pass before merging: `test`
- ❌ Allow force push
- ❌ Allow deletion

Для `dev`:
- ✅ Require pull request before merging
- ✅ Require approvals: 1
- ✅ Require status checks to pass before merging: `test`
- ❌ Allow force push

Преподаватель — единственный, кто может мержить в `master`. Студенты
мержат только в свой форк.

## FAQ

**Локально `quarto render book/` падает, в CI — зелёный.**
Версия Quarto другая. Сверь с `.quarto-version`. Подробно — в
`book/PUBLISHING.md` → «Troubleshooting».

**`pip install -e .[dev]` падает на Windows.**
Обычно из-за того, что `.venv` создан не тем Python (например, системным
3.11). Удали `.venv`, создай заново через `python3.12 -m venv .venv`.

**Push в `master` заблокирован (branch protection).**
Это нормальная защита. Сделай PR из `dev` в `master`, попроси ревьюера
аппрувнуть.

**Студент говорит «PR не создаётся».**
Чаще всего — кнопка «Compare & pull request» на странице форка студента
ведёт в его собственный репо, а не в `khabibullinra/fracbook`. Подробно — в
`docs/student-workflow.md`.

**Хочу откатить плохой мерж в `master`.**
`git revert <commit-sha>` в `master` → push → CI пересоберёт и
переопубликует. Сайт обновится через 1–2 минуты.

**CI job `publish` упал, в `pages` пусто.**
Смотри логи в **Actions → последний запуск на master → job `publish`**.
Типичные причины: токен истёк/отозван, `pages` заблокирована на push,
сетевая ошибка. Чек-лист в `book/PUBLISHING.md` → «Troubleshooting».

**Нужно опубликовать срочно, CI не работает.**
В крайнем случае можно вручную:

```bash
# локально
quarto render book/
# скопировать book/_book/ в новую ветку pages и запушить
git checkout --orphan pages-tmp
git rm -rf .
cp -r book/_book/* .
git add -A
git commit -m "manual publish"
git push origin pages-tmp:pages --force-with-lease
git checkout master
```

Но это **временное** решение, лучше чинить CI. После ручной публикации
следующий успешный CI-мерж должен пройти без конфликтов (т.к. CI делает
`force-with-lease`).
