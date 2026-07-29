#!/usr/bin/env python3
"""Кросс-платформенный скрипт публикации book/_book/ в ветку pages.

Использование:
    python tools/publish_pages.py [--dry-run] [--no-render] [--no-tests] [-h]

Требования:
- git в PATH
- quarto >= 1.9 в PATH
- python3 (или python) в PATH; тесты прогоняются в том же интерпретаторе

Запускать только на машине преподавателя. Студентам этот скрипт
использовать не нужно.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

# Зафиксированная версия Quarto. Должна совпадать с .quarto-version
# в корне репозитория. Positron (Windows) игнорирует .quarto-version и
# использует свой встроенный Quarto, поэтому на Windows-стороне
# преподавателя версию всё равно надо сверять вручную.
MIN_QUARTO_VERSION = (1, 9, 0)

REPO_ROOT = Path(__file__).resolve().parent.parent
PAGES_WORKTREE = REPO_ROOT / ".worktrees" / "pages"
PAGES_BRANCH = "pages"
PAGES_REMOTE = "origin"
BOOK_DIR = REPO_ROOT / "book"
BOOK_OUTPUT = BOOK_DIR / "_book"
QUARTO_VERSION_FILE = REPO_ROOT / ".quarto-version"
NOT_FOUND_HTML = REPO_ROOT / "tools" / "404.html"


# ---------- утилиты ----------


def log(msg: str) -> None:
    print(f"== {msg}", flush=True)


def run(
    cmd: Sequence[str],
    *,
    cwd: Path | None = None,
    check: bool = True,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Запустить команду, прокидывая stdout/stderr в наш stdout.

    stderr намеренно НЕ перехватывается: ошибки должны быть видны
    пользователю вживую (особенно при quarto render).
    """
    printable = " ".join(cmd)
    log(f"$ {printable}" + (f"  (cwd={cwd})" if cwd else ""))
    return subprocess.run(
        list(cmd),
        cwd=str(cwd) if cwd else None,
        check=check,
        env=env,
        text=True,
    )


@dataclass
class Ctx:
    dry_run: bool
    no_render: bool
    no_tests: bool

    def run(self, cmd: Sequence[str], **kw) -> subprocess.CompletedProcess[str] | None:
        if self.dry_run and kw.pop("mutating", False):
            log(f"(dry-run) {' '.join(cmd)}")
            return None
        return run(cmd, **kw)


# ---------- проверки окружения ----------


def fail(msg: str, code: int = 1) -> None:
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(code)


def require_in_path(tool: str) -> str:
    path = shutil.which(tool)
    if not path:
        fail(f"'{tool}' не найден в PATH")
    return path


def parse_quarto_version(stdout: str) -> tuple[int, int, int]:
    """Парсит вывод `quarto --version` — там одна строка вида '1.9.38'."""
    first = stdout.strip().splitlines()[0].strip()
    parts = first.split(".")
    try:
        major = int(parts[0])
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2]) if len(parts) > 2 else 0
    except (ValueError, IndexError) as exc:
        fail(f"не удалось распарсить версию Quarto: {first!r} ({exc})")
    return (major, minor, patch)


def check_quarto(ctx: Ctx) -> tuple[int, int, int]:
    require_in_path("quarto")
    if ctx.dry_run:
        # в dry-run quarto может отсутствовать; не падаем
        log("(dry-run) пропуск проверки версии Quarto")
        return MIN_QUARTO_VERSION
    proc = subprocess.run(
        ["quarto", "--version"], capture_output=True, text=True, check=False,
    )
    if proc.returncode != 0:
        fail("'quarto --version' завершился с ошибкой")
    version = parse_quarto_version(proc.stdout)
    if version < MIN_QUARTO_VERSION:
        actual = ".".join(str(x) for x in version)
        expected = ".".join(str(x) for x in MIN_QUARTO_VERSION)
        fail(f"требуется Quarto >= {expected}, найден {actual}")
    log(f"Quarto {'.'.join(str(x) for x in version)} — ок")
    return version


def check_expected_quarto_file(version: tuple[int, int, int]) -> None:
    """Если в репо есть .quarto-version — сверяем с реальной версией."""
    if not QUARTO_VERSION_FILE.exists():
        return
    expected_text = QUARTO_VERSION_FILE.read_text(encoding="utf-8").strip()
    expected = parse_quarto_version(expected_text)
    if expected != version:
        actual = ".".join(str(x) for x in version)
        expected_str = ".".join(str(x) for x in expected)
        print(
            f"Warning: .quarto-version требует {expected_str}, "
            f"запущен {actual}. Возможен рассинхрон.",
            file=sys.stderr,
        )


def check_master_clean(ctx: Ctx) -> None:
    proc = ctx.run(["git", "status", "--porcelain"], mutating=False)
    if ctx.dry_run:
        return
    assert proc is not None
    if proc.stdout.strip():
        log("Рабочее дерево содержит незакоммиченные изменения:")
        print(proc.stdout, end="", file=sys.stderr)
        fail("сделайте commit/stash или уберите лишнее перед публикацией")


# ---------- шаги пайплайна ----------


def run_tests(ctx: Ctx) -> None:
    """Локальная страховка перед публикацией — те же шаги, что в CI."""
    if ctx.no_tests:
        log("Пропуск тестов (--no-tests)")
        return
    log("pytest -q")
    ctx.run([sys.executable, "-m", "pytest", "-q"], mutating=False)
    log("ruff check src tests")
    ctx.run([sys.executable, "-m", "ruff", "check", "src", "tests"], mutating=False)


def render_book(ctx: Ctx) -> None:
    if ctx.no_render:
        log("Пропуск рендера (--no-render); используется book/_book/")
        return
    log(f"Рендер {BOOK_DIR}/")
    ctx.run(["quarto", "render", str(BOOK_DIR)], mutating=False)
    if not BOOK_OUTPUT.exists():
        fail(f"после quarto render нет каталога {BOOK_OUTPUT}")


def ensure_worktree(ctx: Ctx) -> Path:
    if PAGES_WORKTREE.exists():
        log(f"Переиспользую worktree {PAGES_WORKTREE}")
        # Подтянуть свежий origin/pages, если есть. Может не быть — это ок.
        ctx.run(
            ["git", "-C", str(PAGES_WORKTREE), "pull", "--ff-only",
             PAGES_REMOTE, PAGES_BRANCH],
            mutating=True,
            check=False,
        )
        return PAGES_WORKTREE

    log(f"Создаю worktree {PAGES_WORKTREE} на ветке {PAGES_BRANCH}")
    # Сначала пробуем привязаться к существующей ветке pages, иначе создаём.
    if ctx.dry_run:
        log(f"(dry-run) git worktree add {PAGES_WORKTREE} {PAGES_BRANCH}")
        return PAGES_WORKTREE

    has_branch = subprocess.run(
        ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{PAGES_BRANCH}"],
        check=False,
    ).returncode == 0
    if has_branch:
        ctx.run(
            ["git", "worktree", "add", str(PAGES_WORKTREE), PAGES_BRANCH],
            mutating=True,
        )
    else:
        ctx.run(
            ["git", "worktree", "add", "-b", PAGES_BRANCH, str(PAGES_WORKTREE)],
            mutating=True,
        )
    return PAGES_WORKTREE


def mirror_to_worktree(ctx: Ctx, worktree: Path) -> None:
    """Очистить worktree (кроме .git) и скопировать туда book/_book/ + 404.html.

    Стратегия очистки:
    - оставить .git/ — это сам worktree;
    - удалить всё остальное (включая скрытые файлы вроде .nojekyll);
    - скопировать book/_book/ поверх;
    - положить tools/404.html как 404.html (если есть).

    Тот же эффект, что у `rsync -a --delete`, но без зависимости от rsync.
    Ручные файлы в ветке pages (robots.txt, custom CNAME и т.п.) при таком
    подходе не выживут — это и сейчас так. Если такие файлы понадобятся,
    их надо будет добавлять в этот скрипт явно.
    """
    log(f"Зеркалирую {BOOK_OUTPUT}/ -> {worktree}/")
    if ctx.dry_run:
        log(f"(dry-run) очистка {worktree} кроме .git/")
        log(f"(dry-run) копирование {BOOK_OUTPUT} -> {worktree}")
        if NOT_FOUND_HTML.exists():
            log(f"(dry-run) копирование {NOT_FOUND_HTML} -> {worktree}/404.html")
        return

    for entry in worktree.iterdir():
        if entry.name == ".git":
            continue
        if entry.is_dir():
            shutil.rmtree(entry)
        else:
            entry.unlink()

    shutil.copytree(BOOK_OUTPUT, worktree, dirs_exist_ok=True)

    if NOT_FOUND_HTML.exists():
        shutil.copy2(NOT_FOUND_HTML, worktree / "404.html")
    else:
        log(f"Warning: {NOT_FOUND_HTML} не найден, 404.html не будет добавлен")


def commit_and_push(ctx: Ctx, worktree: Path) -> None:
    if ctx.dry_run:
        log("(dry-run) git add -A && git commit && git push --force-with-lease")
        return

    ctx.run(["git", "add", "-A"], cwd=worktree, mutating=True)
    # Пустой коммит — нет изменений, выходим без пуша
    diff = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=str(worktree),
        check=False,
    )
    if diff.returncode == 0:
        log("Нет изменений для публикации")
        return

    # Дата в ISO — кросс-платформенно через datetime
    from datetime import date

    msg = f"publish: {date.today().isoformat()}"
    ctx.run(["git", "commit", "-m", msg], cwd=worktree, mutating=True)
    log("Пуш в origin/pages (force-with-lease)")
    ctx.run(
        ["git", "push", "--force-with-lease", PAGES_REMOTE, PAGES_BRANCH],
        cwd=worktree,
        mutating=True,
    )
    log("Готово. Сайт: https://khabibullinra.gitverse.site/fracbook/")


def prune_stale_worktrees(ctx: Ctx) -> None:
    """Подчистить записи о удалённых worktrees (сами worktrees не трогаем)."""
    ctx.run(["git", "worktree", "prune"], mutating=True, check=False)


# ---------- main ----------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Публикация book/_book/ в ветку pages.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="показать шаги без реальных изменений",
    )
    parser.add_argument(
        "--no-render",
        action="store_true",
        help="использовать уже собранный book/_book/",
    )
    parser.add_argument(
        "--no-tests",
        action="store_true",
        help="пропустить pytest и ruff перед публикацией",
    )
    parser.add_argument(
        "--prune",
        action="store_true",
        help="в конце подчистить устаревшие записи о worktrees",
    )
    args = parser.parse_args(argv)

    ctx = Ctx(
        dry_run=args.dry_run,
        no_render=args.no_render,
        no_tests=args.no_tests,
    )

    # cd в корень репо — все пути относительные
    import os

    os.chdir(REPO_ROOT)

    require_in_path("git")
    version = check_quarto(ctx)
    if not ctx.dry_run:
        check_expected_quarto_file(version)
    check_master_clean(ctx)
    run_tests(ctx)
    render_book(ctx)

    worktree = ensure_worktree(ctx)
    mirror_to_worktree(ctx, worktree)
    commit_and_push(ctx, worktree)

    if args.prune:
        prune_stale_worktrees(ctx)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
