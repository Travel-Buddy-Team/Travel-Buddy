@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%.venv"

if not exist "%VENV_DIR%\" (
    echo Error: No .venv folder! Make sure to run setup-windows.bat!
    exit /b 1
)

if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo Error: Python executable not found in virtual environment!
    exit /b 1
)

"%VENV_DIR%\Scripts\python.exe" "%SCRIPT_DIR%src\TravelBuddy\main.py"

exit /b %ERRORLEVEL%