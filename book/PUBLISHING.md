# Сборка книги Quarto

Узкая инструкция: как собрать `book/` локально и что делать, если что-то
сломалось. Публикация на сайт — через CI (см. `PUBLISHING.md` в корне).

## Содержание

- [Локальный рендер](#локальный-рендер)
- [Структура `book/`](#структура-book)
- [Добавление главы](#добавление-главы)
- [Troubleshooting](#troubleshooting)

## Локальный рендер

```bash
# Из корня репо, с активированным .venv:
quarto preview book/    # рендерит + открывает в браузере + авто-перезагрузка
quarto render book/     # рендерит без браузера (для CI / smoke-теста)
```

`quarto preview` следит за `.qmd`, `.py`, конфигами и перерисовывает
страницу при изменении. В Positron — **Quarto: Preview** в палитре команд.

Артефакт — `book/_book/`. Папка в `.gitignore`, в `master` не коммитится.

## Структура `book/`

```
book/
├── _quarto.yml              # конфигурация книги (тема, toc, include-in-header)
├── _include/header.html     # inline-<script> для Plotly.js (CDN)
├── index.qmd                # титульная страница
├── lecture-NN-*.qmd         # лекции (8 штук, порядок в _quarto.yml)
├── tutorial-NN-*.qmd        # лабораторные работы (9 штук, в appendices)
├── images/                  # иллюстрации (SVG предпочтительно)
├── references.bib           # BibTeX для цитирований
└── PUBLISHING.md            # этот файл
```

Главы нумеруются `lecture-NN-` (лекции) и `tutorial-NN-` (лабораторные).
Порядок и нумерация — в `book/_quarto.yml` (`chapters:` и `appendices:`).

## Добавление главы

1. Создать файл `book/lecture-NN-<короткий-slug>.qmd` (или `tutorial-...`).
2. В frontmatter — заголовок:
   ```yaml
   ---
   title: "Лекция N. <название>"
   ---
   ```
3. Добавить в `book/_quarto.yml` в секцию `chapters:` (для лекции) или
   `appendices:` (для лабораторной). Порядок определяет нумерацию.
4. Локально: `quarto preview book/` → проверить навигацию и рендер.
5. PR в `dev`. После ревью и мержа — попадёт в `master`, CI опубликует.

## Troubleshooting

### `quarto` не найден

В новом терминале после установки: см. `PUBLISHING.md` в корне →
«Установка инструментов». На Windows: перезапустить PowerShell после
добавления в PATH.

Версия другая — `quarto --version` показывает не `1.9.38`. Поставь
правильную версию (см. ADR-0001 и `PUBLISHING.md`).

### Ошибка `Error resolving header-includes: unable to open file <script ...>`

`include-in-header` в `_quarto.yml` ожидает **путь к файлу**, не inline-строку.
Содержимое inline-тега положи в `book/_include/header.html`, а в YAML
укажи путь к нему:

```yaml
format:
  html:
    include-in-header: _include/header.html
```

Содержимое `book/_include/header.html`:

```html
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
```

Если в офлайне — скачай Plotly в `book/_include/plotly.min.js` и поменяй
`src` на относительный путь. Quarto сам скопирует оба файла в `_book/`.

### `Error: filter main.lua: ... Unable to resolve crossref @fig-...`

Crossref `@fig-some-label` не находит чанк с `label: fig-some-label`.
Проверь:

- Лейбл есть в frontmatter чанка: `#| label: fig-some-label`
- Ссылка пишется как `[@fig-some-label]` (с префиксом `fig-` и `@`)
- Лейбл уникален в рамках книги

OJS-блоки тоже поддерживают `label` + `fig-cap` (Quarto ≥ 1.4). Если
crossref на OJS-чанк не работает — переименуй ссылку в тексте на «на
рисунке ниже».

### Python-чанк не запускается / падает

Проверь, что `.venv` активирован (или выбран как interpreter в Positron).
Внутри чанка — только вызовы `fracbook` (см. `book/CONTRIBUTING.md`).
Если падает с `ModuleNotFoundError: No module named 'fracbook'` — выполни
`pip install -e .[dev]` заново.

### OJS-блок возвращает пустой график

`Plotly is not defined` — CDN не загрузился. Проверь:

1. `book/_include/header.html` существует и содержит `<script src="...">`.
2. В `_quarto.yml` стоит `include-in-header: _include/header.html`.
3. В DevTools браузера (F12) на опубликованной странице — Network → нет ли
   ошибки на `cdn.plot.ly`.

### PDF-рендер падает / пустая страница

PDF в этой методичке **опционально** (см. `AGENTS.md`). HTML — основной
формат. Если нужен PDF:

- `kaleido` уже в `dev`-зависимостях (`pyproject.toml`).
- `quarto render book/ --to pdf` соберёт PDF. Plotly-графики уйдут как
  статичные PNG.
- Если падает — смотри в `book/_book/*.log`. Типичная причина —
  нехватка памяти для больших 3D-графиков; уменьши `n` (количество
  точек на окружности) в чанке.

### Локально зелёный, CI красный

Версия Quarto другая. Сверь `quarto --version` с `.quarto-version`. Или
Python-окружение (CI использует чистый `pip install -e .[dev]`, без
дополнительных системных пакетов).

### Долго рендерится

Большие 3D-графики (Plotly, OJS-схемы с `n > 100`) — медленно. Если
`quarto preview` тормозит — уменьши `n` (например, с 40 до 20), это не
влияет на визуальное качество для типичных углов обзора.
