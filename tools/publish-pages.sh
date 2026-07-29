#!/usr/bin/env bash
# Тонкий шим: делегирует в кросс-платформенный Python-скрипт.
# Реальная логика — в tools/publish_pages.py.
set -euo pipefail

if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "Error: python3/python не найден в PATH" >&2
  exit 1
fi

exec "$PY" "$(dirname "$0")/publish_pages.py" "$@"
