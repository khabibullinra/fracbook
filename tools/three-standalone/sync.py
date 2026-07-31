"""
Синхронизация отладочного стенда tools/three-standalone.html
с OJS-блоком в book/lecture-01-intro.qmd.

Зачем: при отладке 3D-схемы не хочется пересобирать всю книгу через
quarto render. Стенд подключает Three.js напрямую с CDN, копирует
тело OJS-блока и запускает его в браузере. После правки .qmd
запустите `python tools/three-standalone/sync.py` и обновите
tools/three-standalone.html в браузере (Ctrl+R).

Зависимости: только стандартная библиотека Python 3.
"""

from __future__ import annotations

import argparse
import html
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
QMD = ROOT / "book" / "lecture-01-intro.qmd"
OUT = ROOT / "tools" / "three-standalone.html"
LABEL = "fig-fracture-scheme-three"

# Маркеры в tools/three-standalone.html, между которыми должен
# лежать код сцены. Совпадают с теми, что в плейсхолдере.
BEGIN_MARK = "=== НАЧАЛО КОДА СЦЕНЫ (скопировано из .qmd) ==="
END_MARK = "=== КОНЕЦ КОДА СЦЕНЫ ==="

# OJS-тело функции рендера ячейки обёрнуто в { ... } сразу после
# `//| echo: false`. Выдираем именно фигурные скобки, а не
# метаданные `//| …`.
OJS_RE = re.compile(
    r"```\{ojs\}\n(?P<header>(?://\|[^\n]*\n)*)(?P<body>.*?)\n```",
    re.S,
)


def extract_ojs(qmd_text: str) -> tuple[str, str]:
    """Возвращает (header, body) нужного OJS-блока. Бросает, если не найден."""
    for m in OJS_RE.finditer(qmd_text):
        header = m.group("header")
        if "label: " + LABEL in header:
            return header, m.group("body")
    raise SystemExit(
        f"OJS-блок с label={LABEL!r} не найден в {QMD}. "
        f"Проверьте, что lecture-01-intro.qmd не был переименован."
    )


def to_standalone(body: str) -> str:
    """Превращает OJS-тело в код, исполнимый в браузерном стенде.

    Различия OJS ↔ standalone:
    1. OJS-блок — это выражение, standalone-обёртка — IIFE `(() => { ... })()`.
    2. В OJS определён глобальный `invalidation` (Promise Ot). В standalone
       подменяем на бесконечно висящий Promise, чтобы cleanup-код не
       выполнился. Без подмены будет ReferenceError.
    3. В ObservableJS возвращаемое значение выражения попадает в DOM
       ячейки автоматически. В standalone-стенде этого нет, поэтому
       вставляем `__insert(wrap)` перед `return wrap;`. Без этого
       сцена строится и считает, но ничего не видно — `wrap` болтается
       в памяти без родителя.
    """
    # Подмена invalidation: пробрасываем через `with`-обёртку нельзя,
    # поэтому в самое начало вставляем `const invalidation = ...;`
    # и помощник __insert для самостоятельной вставки в DOM.
    prelude = (
        "  // Подмены OJS-глобалов для standalone-стенда:\n"
        "  // invalidation в ObservableJS — Promise, который резолвится\n"
        "  // при перерендере ячейки. Здесь мы не перерендериваем, поэтому\n"
        "  // просто Never-resolving Promise — cleanup-код не выполнится.\n"
        "  const invalidation = new Promise(() => {});\n\n"
        "  // В standalone-стенде, в отличие от ObservableJS, возвращаемое\n"
        "  // значение IIFE никто не вставит в DOM. Поэтому сами добавляем\n"
        "  // корневой контейнер в #app — иначе сцена выполняется, но\n"
        "  // невидима.\n"
        "  const __insert = (root) => {\n"
        "    const host = document.getElementById('app');\n"
        "    if (host && root) host.appendChild(root);\n"
        "  };\n"
        "  // Диагностика: обновляет маленький плашка-статус в углу стенда.\n"
        "  // Если window.__diag не определён (стенд старой версии) —\n"
        "  // ничего не делаем.\n"
        "  const __diag = (msg, ok) => {\n"
        "    if (typeof window.__diag === 'function') window.__diag(msg, ok);\n"
        "  };\n"
        "  __diag('runtime: старт', true);\n\n"
    )
    body = body.replace("\n{\n", "\n{\n" + prelude, 1)
    if "const invalidation = new Promise(() => {})" not in body:
        # запасной путь: тело без ведущего `{`, добавляем prelude в начало
        body = prelude + body

    # Перед `return wrap;` вставляем __insert(wrap). Ищем **последний**
    # такой return — в OJS-теле может быть несколько ранних выходов
    # (например, при отсутствии THREE), и вставлять __insert надо
    # ровно перед нормальным финальным return.
    needle = "  return wrap;\n"
    insert = "  // Standalone-вставка в DOM (см. комментарий к __insert выше).\n" \
             "  __insert(wrap);\n" + needle
    if needle in body:
        # rfind находит последнее вхождение; заменяем только его.
        idx = body.rfind(needle)
        body = body[:idx] + insert + body[idx + len(needle):]

    # Диагностика: в ветке с THREE === undefined сразу после записи
    # в canvasBox сообщаем статус, чтобы стенд сказал «Three.js не
    # загрузился» даже если ранний return не дошёл до __insert.
    body = body.replace(
        "canvasBox.textContent = 'Three.js не загрузился — "
        "проверьте CDN в _include/header.html.';\n    return wrap;",
        "canvasBox.textContent = 'Three.js не загрузился — "
        "проверьте CDN в _include/header.html.';\n"
        "    if (typeof __diag === 'function') __diag('Three.js не загрузился', false);\n"
        "    return wrap;",
        1,
    )

    # Диагностика: после animate() ставим метку OK. Если код упал
    # раньше — её не будет, и пользователь увидит последний успешный
    # статус (например, "runtime: старт").
    body = body.replace(
        "  animate();\n",
        "  animate();\n"
        "  if (typeof __diag === 'function') __diag('OK: animate() запущен', true);\n",
        1,
    )

    return f"(() => {{\n{body}\n}})();"


def render_html(header: str, iife: str) -> str:
    # Берём существующий стенд как шаблон, чтобы сохранить его
    # комментарии и MathJax-заглушку, и подменяем только блок кода.
    # Маркеры BEGIN/END в шаблоне могут быть как с префиксом `//`,
    # так и без — pattern ищет по подстроке с любой строки.
    template = OUT.read_text(encoding="utf-8")
    pattern = re.compile(
        r"^[^\n]*" + re.escape(BEGIN_MARK) + r".*?^[^\n]*" + re.escape(END_MARK),
        re.S | re.M,
    )
    if not pattern.search(template):
        raise SystemExit(
            f"Маркеры {BEGIN_MARK!r} / {END_MARK!r} не найдены в {OUT}. "
            "Сначала положите в стенд плейсхолдер с этими строками."
        )
    new_block = (
        f"  // {BEGIN_MARK}\n"
        f"  // Источник: book/lecture-01-intro.qmd (label: {LABEL}).\n"
        f"  // Сгенерировано tools/three-standalone/sync.py — не\n"
        f"  // редактируйте этот блок руками, иначе sync.py перезапишет.\n"
        f"  // {header.strip().splitlines()[0]}\n"
        f"{iife}\n"
        f"  // {END_MARK}"
    )
    return pattern.sub(lambda _m: new_block, template, count=1)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check", action="store_true",
                   help="только проверить, что стенд актуален (exit 1, если нет)")
    args = p.parse_args(argv)

    qmd_text = QMD.read_text(encoding="utf-8")
    header, body = extract_ojs(qmd_text)
    iife = to_standalone(body)
    expected = render_html(header, iife)

    if args.check:
        actual = OUT.read_text(encoding="utf-8")
        if actual == expected:
            print("OK: стенд актуален")
            return 0
        print("DIFF: стенд отстал от .qmd. Запустите sync.py без --check.")
        return 1

    OUT.write_text(expected, encoding="utf-8")
    print(f"Обновлено: {OUT.relative_to(ROOT)}")
    print(f"  источник: {QMD.relative_to(ROOT)}")
    print(f"  размер JS: {len(iife)} байт")
    return 0


if __name__ == "__main__":
    sys.exit(main())
