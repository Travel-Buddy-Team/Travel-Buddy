@echo off
setlocal

echo Installing Travel-Buddy

set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%.venv"

echo %VENV_DIR%

if exist "%VENV_DIR%\" (
    echo Deleting old venv.
    rmdir /s /q "%VENV_DIR%"
)

echo Creating new venv.
python -m venv "%VENV_DIR%"

if errorlevel 1 (
    echo Error: Failed to create virtual environment.
    exit /b 1
)

echo Installing requirements.
"%VENV_DIR%\Scripts\python.exe" -m pip install -e "%SCRIPT_DIR%"

if errorlevel 1 (
    echo Error: Failed to install requirements.
    exit /b 1
)

echo Setup Complete
exit /b 0
