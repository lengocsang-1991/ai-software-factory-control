@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel% equ 0 (
    py -3 -m factory_control init
    if errorlevel 1 exit /b 1
    echo Dashboard: http://127.0.0.1:8765/
    py -3 -m factory_control serve
) else (
    python -m factory_control init
    if errorlevel 1 exit /b 1
    echo Dashboard: http://127.0.0.1:8765/
    python -m factory_control serve
)
