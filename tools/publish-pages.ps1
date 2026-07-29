# Тонкий шим: делегирует в кросс-платформенный Python-скрипт.
# Реальная логика — в tools\publish_pages.py.
# Использование: powershell -File tools\publish-pages.ps1 [аргументы]
#                или .\tools\publish-pages.ps1 [аргументы] из PowerShell.

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Сначала пробуем Windows Python Launcher, затем python.exe.
$py = $null
try {
    $ver = & py -3 --version 2>$null
    if ($LASTEXITCODE -eq 0) { $py = 'py -3' }
} catch {}

if (-not $py) {
    $pyCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pyCmd) { $py = 'python' }
}

if (-not $py) {
    Write-Error "python не найден в PATH"
    exit 1
}

& $py "$scriptDir\publish_pages.py" @args
exit $LASTEXITCODE
