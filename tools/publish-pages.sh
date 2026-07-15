#!/usr/bin/env bash
# Публикует book/_book/ в ветку pages через git worktree.
# Запускать только на машине преподавателя (Linux/macOS).
# Студенты с этим скриптом не работают.

set -euo pipefail

usage() {
  cat <<EOF
Usage: $0 [--dry-run] [--no-render]

  --dry-run    Показать, что будет сделано, без изменений на диске и в remote.
  --no-render  Пропустить рендер, использовать текущий book/_book/.
  -h, --help   Показать эту справку.
EOF
}

DRY_RUN=0
NO_RENDER=0
for arg in "$@"; do
  case "$arg" in
    --dry-run)   DRY_RUN=1 ;;
    --no-render) NO_RENDER=1 ;;
    -h|--help)   usage; exit 0 ;;
    *)           echo "Unknown argument: $arg" >&2; usage >&2; exit 2 ;;
  esac
done

cd "$(git rev-parse --show-toplevel)"

# Чистота рабочего дерева в master
if [ -n "$(git status --porcelain)" ]; then
  echo "Error: рабочее дерево в master содержит незакоммиченные изменения или неотслеживаемые файлы." >&2
  echo "Сделайте commit/stash или удалите лишнее перед публикацией:" >&2
  git status --short >&2
  exit 1
fi

# Проверка Quarto
if ! command -v quarto >/dev/null 2>&1; then
  echo "Error: 'quarto' не найден в PATH." >&2
  exit 1
fi
QV=$(quarto --version | head -1)
if ! printf '1.9\n%s\n' "$QV" | sort -V -C; then
  echo "Error: требуется Quarto >= 1.9, найден $QV." >&2
  exit 1
fi

log() { printf '== %s\n' "$*"; }
run() { if [ "$DRY_RUN" -eq 1 ]; then echo "(dry-run) $*"; else eval "$@"; fi; }

# Рендер
if [ "$NO_RENDER" -eq 0 ]; then
  log "Рендер book/ (Quarto $QV)"
  run "quarto render book/"
else
  log "Пропуск рендера (--no-render)"
fi

# Worktree для ветки pages
PAGES_DIR=".worktrees/pages"
if [ ! -d "$PAGES_DIR" ]; then
  log "Создаю worktree $PAGES_DIR на ветке pages"
  run "git worktree add -b pages '$PAGES_DIR'"
else
  log "Переиспользую worktree $PAGES_DIR"
  if [ "$DRY_RUN" -eq 0 ]; then
    git -C "$PAGES_DIR" pull --ff-only origin pages 2>/dev/null || true
  fi
fi

# Зеркалирование артефакта сборки
log "Зеркалирую book/_book/ -> $PAGES_DIR/"
run "rsync -a --delete --exclude='.git' book/_book/ '$PAGES_DIR/'"

if [ -f tools/404.html ]; then
  run "cp tools/404.html '$PAGES_DIR/404.html'"
fi

if [ "$DRY_RUN" -eq 1 ]; then
  log "(dry-run завершён)"
  exit 0
fi

# Коммит и пуш
cd "$PAGES_DIR"
git add -A
if git diff --cached --quiet; then
  log "Нет изменений для публикации"
  exit 0
fi
git commit -m "publish: $(date -I)"
log "Пуш в origin/pages (force-with-lease)"
git push --force-with-lease origin pages

log "Готово. Сайт: https://khabibullinra.gitverse.site/fracbook/"
