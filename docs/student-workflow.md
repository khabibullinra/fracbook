# Как работать с проектом: инструкция для студента

Пошаговое руководство: от регистрации на GitVerse до первого merged PR.
Предполагается, что у вас Windows 10/11 и Positron (или обычный терминал
с Git). Если что-то не совпадает с вашей системой — пишите в чат курса,
поможем.

## Содержание

1. [Что такое форк и зачем он нужен](#1-что-такое-форк-и-зачем-он-нужен)
2. [Регистрация на GitVerse](#2-регистрация-на-gitverse)
3. [Форк репозитория](#3-форк-репозитория)
4. [Установка Git, Python, Quarto](#4-установка-git-python-quarto)
5. [Клонирование своего форка](#5-клонирование-своего-форка)
6. [Создание виртуального окружения](#6-создание-виртуального-окружения)
7. [Создание рабочей ветки](#7-создание-рабочей-ветки)
8. [Работа: редактирование, коммит, проверка](#8-работа-редактирование-коммит-проверка)
9. [Отправка изменений в свой форк](#9-отправка-изменений-в-свой-форк)
10. [Создание Pull Request](#10-создание-pull-request)
11. [После создания PR: ревью и доработки](#11-после-создания-pr-ревью-и-доработки)
12. [Синхронизация форка с основным репо](#12-синхронизация-форка-с-основным-репо)
13. [FAQ](#13-faq)

## 1. Что такое форк и зачем он нужен

**Форк** — это ваша личная копия репозитория преподавателя на GitVerse.
Вы работаете в своей копии, а когда готовы поделиться — отправляете
**Pull Request** (запрос на вливание) в оригинальный репозиторий.

**Зачем так, а не напрямую**: преподаватель хочет быть уверен, что в
основной репозиторий попадут только проверенные изменения. Если каждый
студент пишет прямо в `master` — любой неудачный коммит ломает сайт
методички. Через форк ваши эксперименты безопасны.

```
оригинальный репо (преподаватель)  ←── PR ←──  ваш форк (студент)
         khabibullinra/fracbook              <ваш-ник>/fracbook
                  │                                   │
                  ▼                                   ▼
              master/dev                          ваши ветки
                                                  student/<ник>/...
```

## 2. Регистрация на GitVerse

1. Откройте [gitverse.ru](https://gitverse.ru).
2. Sign up → email или GitHub-аккаунт.
3. Подтвердите email.
4. Запомните свой ник (видно в правом верхнем углу) — он понадобится для
   адреса форка.

## 3. Форк репозитория

1. Откройте [gitverse.ru/khabibullinra/fracbook](https://gitverse.ru/khabibullinra/fracbook).
2. В правом верхнем углу страницы — кнопка **«Форк»** (вилка-стрелка).
3. Подтвердите, что форкаете в свой аккаунт.
4. Готово. Теперь у вас есть `https://gitverse.ru/<ваш-ник>/fracbook`.

## 4. Установка Git, Python, Quarto

Подробно с командами — в `PUBLISHING.md` в корне репо → «Установка
инструментов». Коротко:

- **Git for Windows** — [gitforwindows.org](https://gitforwindows.org/), далее → Next → Next → Finish.
- **Python 3.12** — [python.org/downloads](https://www.python.org/downloads/), при установке галка **Add Python to PATH**.
- **Quarto 1.10.18** — ставится через `winget install --id Posit.Quarto -e` (Windows) или скачивается с [quarto.org/docs/download](https://quarto.org/docs/download/) (Linux, macOS). Подробно — в `PUBLISHING.md`.

Проверка в **новом** PowerShell:

```powershell
git --version       # git version 2.4x.x
python --version    # Python 3.12.x
quarto --version    # 1.10.18
```

В Positron Git и Python уже есть. Quarto — встроен, но версия может быть
другая; **поставьте 1.10.18 в систему** по инструкции (отличается от
Positron-версии, специально).

## 5. Клонирование своего форка

```powershell
# В PowerShell, в папке, где будете держать проект (например, C:\projects):
cd C:\projects
git clone https://gitverse.ru/<ваш-ник>/fracbook.git
cd fracbook
```

**Важно**: клонируете **свой форк**, не оригинальный репо. Иначе не сможете
пушить.

Проверка:

```powershell
git remote -v
# Должно быть:
# origin  https://gitverse.ru/<ваш-ник>/fracbook.git (fetch)
# origin  https://gitverse.ru/<ваш-ник>/fracbook.git (push)
```

## 6. Создание виртуального окружения

В корне склонированного проекта (там, где лежит `pyproject.toml`):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Если PowerShell ругается на Execution Policy:
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
# затем снова:
.\.venv\Scripts\Activate.ps1
```

После активации в начале строки появится `(.venv)`. Установите зависимости:

```powershell
pip install -e .[dev]
```

Это поставит пакет `fracbook` в editable-режиме (изменения в `src/fracbook/`
сразу видны без переустановки) и dev-инструменты (pytest, ruff, plotly,
kaleido).

## 7. Создание рабочей ветки

**Каждая задача — отдельная ветка.** Не коммитьте в `master` (там лежит
эталонный код).

```powershell
# Убедиться, что вы на master и он свежий
git checkout master
git pull

# Создать свою ветку
git checkout -b student/<ваш-ник>/<короткое-описание>
```

Примеры хороших имён веток:

- `student/ivanov/lab-1-pkn-sensitivity`
- `student/petrova/fix-typo-lecture-2`
- `student/sidorov/add-notebook-steady-state`

Плохих:

- `my-changes` (непонятно, чьи)
- `fix` (что фиксим?)
- `master` (запрещено)

## 8. Работа: редактирование, коммит, проверка

Редактируйте файлы в Positron / VS Code / любом редакторе. Перед коммитом
**обязательно** прогоните:

```powershell
# 1. Тесты пакета fracbook
pytest -q

# 2. Линтер
ruff check src tests

# 3. (Опционально, рекомендуется) Рендер книги — поймает синтаксис .qmd
quarto render book/
```

Если что-то красное — починить до коммита.

**Коммит — осмысленными кусками.** Не один коммит на всё, не по одной
строке. Один коммит = одна логическая правка.

```powershell
git add <что-изменили>
git status            # проверьте, что попало в индекс
git commit -m "краткое описание на русском"
```

Хорошие сообщения:

- `add: разбор лабораторной 1 в lecture-04`
- `fix: опечатка в формуле 2.3`
- `refactor: вынести геометрию трещины в fracbook.viz`

## 9. Отправка изменений в свой форк

```powershell
git push -u origin student/<ваш-ник>/<короткое-описание>
```

`-u` привязывает локальную ветку к удалённой. Дальше просто `git push`.

## 10. Создание Pull Request

1. Откройте в браузере **свой форк**: `https://gitverse.ru/<ваш-ник>/fracbook`.
2. GitVerse сам покажет баннер «Your recently pushed branches» → нажмите
   **«Compare & pull request»** напротив вашей ветки.
3. Если баннера нет: переключитесь на свою ветку (выпадающий список
   слева) → **«Contribute»** → **«Open pull request»**.
4. Заполните форму:
   - **Title**: краткое описание (как в коммите).
   - **Description**: что сделали, зачем, на что обратить внимание
     ревьюеру. Если есть связанный issue — укажите `#123`.
   - **Base repository**: `khabibullinra/fracbook` (оригинальный репо).
   - **Base branch**: `dev` (НЕ `master` — в master мы не мержим).
   - **Head repository**: `<ваш-ник>/fracbook` (ваш форк).
   - **Head branch**: `student/<ваш-ник>/<короткое-описание>`.
5. Нажмите **«Create pull request»**.
6. Дождитесь, пока CI пройдёт (зелёная галка) или упадёт (красный
   крестик). Если красный — читайте логи, чините, пушите исправления
   в ту же ветку (PR обновится автоматически).

## 11. После создания PR: ревью и доработки

Преподаватель или ревьюер посмотрит ваш код и оставит комментарии прямо
в PR (в строках файла). Возможные сценарии:

### Вас попросили что-то поправить

1. Внесите правки в той же ветке локально.
2. Закоммитьте и запушьте:
   ```powershell
   git add .
   git commit -m "правки по ревью"
   git push
   ```
3. PR обновится автоматически. Ничего больше делать не нужно.

### Преподаватель одобрил (✓ Approve)

Скорее всего, он же и нажмёт **«Merge pull request»**. Если не нажал —
напишите ему в чат курса: «PR #NN одобрен, можно мержить?».

После мержа ваша ветка `student/<ник>/...` останется в вашем форке
(это нормально, можно удалить или оставить для истории).

## 12. Синхронизация форка с основным репо

Со временем основной репо уходит вперёд (другие PR смержены, новые
главы). Чтобы ваш форк не отставал:

### Через UI (проще)

1. Откройте свой форк на GitVerse.
2. Если есть баннер «This branch is N commits behind khabibullinra:master»
   → **«Sync fork»** → **«Update branch»**.
3. Готово.

### Через командную строку (надёжнее)

Добавьте оригинальный репо как remote (один раз):

```powershell
git remote add upstream https://gitverse.ru/khabibullinra/fracbook.git
git remote -v
# origin    https://gitverse.ru/<ваш-ник>/fracbook.git (fetch)
# origin    https://gitverse.ru/<ваш-ник>/fracbook.git (push)
# upstream  https://gitverse.ru/khabibullinra/fracbook.git (fetch)
# upstream  https://gitverse.ru/khabibullinra/fracbook.git (push)
```

Подтяните изменения:

```powershell
# Обновить master в вашем форке
git checkout master
git fetch upstream
git merge upstream/master
git push origin master

# Обновить вашу рабочую ветку (если ещё не смёржена)
git checkout student/<ваш-ник>/...
git merge master
# Если конфликты — починить, git add, git commit
git push
```

## 13. FAQ

**`git push` просит пароль, но я не хочу вводить его каждый раз.**
Настройте SSH-ключ. Пошагово — в документации GitVerse:
`Settings → SSH keys → Add key`. Сгенерируйте ключ через
`ssh-keygen -t ed25519` и скопируйте публичный в форму.

Или используйте Personal Access Token (PAT) вместо пароля. PAT живёт
дольше и отзывается явно.

**`git push` отклонён: `non-fast-forward`.**
Кто-то (или вы сами) запушил в вашу ветку раньше. Сначала
`git pull --rebase`, потом `git push`.

**Positron показывает старый `fracbook`.**
Positron использует свой Python-интерпретатор. Выберите `.venv` в
палитре команд: **"Python: Select Interpreter"** → путь к
`C:\projects\fracbook\.venv\Scripts\python.exe`.

**`pip install -e .[dev]` падает с "Microsoft Visual C++ 14.0 or greater is required".**
Один из пакетов (скорее всего, `numpy` или `matplotlib`) требует
компилятора. Поставьте **Build Tools for Visual Studio**:
[visualstudio.microsoft.com/visual-cpp-build-tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/),
при установке отметьте «Desktop development with C++».

**`quarto render book/` падает, а `quarto preview book/` работает.**
Странно, но бывает. Покажите преподавателю вывод — обычно это
несовместимая версия Quarto.

**Мой PR «конфликтует» с основным репо.**
Ветка отстала. Сделайте sync (раздел 12), потом
`git rebase master` (или `merge master`) в вашей ветке, почините
конфликты, `git push -f`. PR обновится.

**У меня нет Positron. Я в обычном VS Code / терминале.**
Всё то же самое, кроме выбора интерпретатора. В VS Code: **Ctrl+Shift+P**
→ "Python: Select Interpreter" → ваш `.venv`. Quarto рендерите из
терминала (`quarto preview book/`).

**Можно ли без форка, если я уже Developer в основном репо?**
Нельзя. После ADR-0003 студенты работают **только** через форк. Если у
вас остались старые права Developer — просьба их не использовать,
работайте через форк. После следующего аудита прав роль Developer у
студенческих аккаунтов будет отозвана.

**Что-то сломалось, и я не знаю, что делать.**
Пишите в чат курса. Лучше спросить и сделать правильно, чем молча
закоммитить ерунду.
