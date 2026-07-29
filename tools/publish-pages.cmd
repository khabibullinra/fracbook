@echo off
REM Тонкий шим: делегирует в кросс-платформенный Python-скрипт.
REM Реальная логика — в tools\publish_pages.py.

setlocal

REM Пробуем Windows Python Launcher (ставится с любым официальным
REM инсталлятором Python), затем fallback на python.exe.
set "PY=py -3"
py -3 --version >nul 2>&1
if errorlevel 1 set "PY=python"

"%PY%" "%~dp0publish_pages.py" %*
exit /b %ERRORLEVEL%
