@echo off
setlocal
cd /d "%~dp0"
set "STUDIO_PY=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
set "PYTHONIOENCODING=utf-8"

if exist "%STUDIO_PY%" (
    "%STUDIO_PY%" -B _build\studio.py --open
    goto done
)
where py >nul 2>nul
if not errorlevel 1 (
    py -3 -B _build\studio.py --open
    goto done
)
where python >nul 2>nul
if not errorlevel 1 (
    python -B _build\studio.py --open
    goto done
)
echo Python 3 is required to start the local studio.
pause
exit /b 1

:done
if errorlevel 1 pause
