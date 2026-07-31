# Отладочный стенд 3D-схемы (Three.js)

Зачем: при правке 3D-схемы в `book/lecture-01-intro.qmd` (OJS-блок
`fig-fracture-scheme-three`) не хочется пересобирать всю книгу через
`quarto render` только чтобы увидеть, как крутится подпись. Этот
стенд копирует тело OJS-блока в обычный HTML и запускает его
напрямую: браузер + F5 = обновление.

## Быстрый старт

1. После правки `.qmd` обновите стенд:

   ```bash
   python tools/three-standalone/sync.py
   ```

2. Откройте `tools/three-standalone.html` в браузере (двойной клик
   в проводнике, или `Ctrl+Shift+P` → "Live Preview: Show Preview"
   в Positron).

3. Крутите сцену мышью, двигайте бегунки — изменения в `.qmd`
   отразятся после следующего `sync.py` и `Ctrl+R`.

## Диагностика при первой загрузке

В правом нижнем углу стенда — маленький плашка-статус:

| Что пишет | Что значит |
|---|---|
| `init…` | стенд ещё не отработал, JS не загрузился |
| `runtime: старт` | код сцены стартовал, но анимация ещё не запустилась |
| `Three.js не загрузился` | CDN Three.js не отдал (интернет, блокировка). Проверьте F12 → Network |
| `OK: animate() запущен` | всё работает, можно крутить |

Если плашка осталась `init…` — откройте DevTools (`F12`) → Console,
там будет ошибка инициализации.

## Что внутри

| Файл | Зачем |
|---|---|
| `tools/three-standalone.html` | Сам стенд. Один HTML, без билд-шага. |
| `tools/three-standalone/sync.py` | Копирует OJS-блок из .qmd в стенд. |
| `tools/three-standalone/README.md` | Этот файл. |

## Верификация перед коммитом

`sync.py --check` — выходит с RC=0, если `tools/three-standalone.html`
соответствует текущему `.qmd`. Можно повесить в pre-commit или в
CI, чтобы стенд не отставал.

Также сам стенд парсится без ошибок:

```bash
node --check <(python -c "import re,pathlib; \
  p=pathlib.Path('tools/three-standalone.html').read_text(encoding='utf-8'); \
  print(re.search(r'<script id=\"scene-source\"[^>]*>(.*?)</script>', p, re.S).group(1))")
```

## Что НЕ совпадает с production

- В OJS определён глобальный `invalidation` (Promise на перерендер).
  `sync.py` подменяет его на Never-resolving Promise, поэтому код
  cleanup-а (`renderer.dispose`, удаление DOM-узлов) **никогда не
  выполнится**. Это и нужно для отладки: при правке не сработает
  «освобождение ресурсов между итерациями», и можно спокойно
  крутить сцену.
- MathJax подменён на заглушку: `tex2chtml` возвращает plain-текст
  c `$x_f$`. LaTeX-плашки на сцене в стенде выглядят беднее, чем
  в production Quarto-сборке. Это сознательное упрощение — для
  отладки **геометрии** и **вращения подписей** настоящий MathJax
  не нужен.
- В standalone, в отличие от ObservableJS, возвращаемое значение
  IIFE никто не вставит в DOM. `sync.py` подставляет `__insert(wrap)`
  перед `return wrap;`, чтобы корневой контейнер попал в `#app`.
- В стенде только текущая сцена. Другие OJS-блоки (если появятся)
  подключаются отдельными стендами или общим шаблоном.

## Когда этого мало

- Если вы правите Quarto-специфичные вещи (crossref, mathjax внутри
  PDF, тему cosmo) — без `quarto render book/` всё равно не
  обойтись. Стенд покрывает только JS/3D-часть.
- Если меняются внешние зависимости (`book/_include/header.html` —
  другой CDN Three.js, добавлен Plotly) — нужно поправить CDN-строку
  в `tools/three-standalone.html`.
