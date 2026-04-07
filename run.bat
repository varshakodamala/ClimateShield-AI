@echo off
REM Batch wrapper to run Weather Platform with proper venv activation
REM Usage: run.bat api | run.bat dashboard | run.bat pipeline

setlocal enabledelayedexpansion

REM Get the script directory
set "SCRIPT_DIR=%~dp0"

REM Activate virtual environment
set "VENV_PATH=%SCRIPT_DIR%.venv"
set "ACTIVATE_SCRIPT=%VENV_PATH%\Scripts\activate.bat"

if exist "%ACTIVATE_SCRIPT%" (
    call "%ACTIVATE_SCRIPT%"
) else (
    echo Virtual environment not found at: %VENV_PATH%
    echo Please create it with: python -m venv .venv
    exit /b 1
)

REM Change to project directory
cd /d "%SCRIPT_DIR%"

REM Run the main script with arguments
set "PYTHON_PATH=%VENV_PATH%\Scripts\python.exe"
"%PYTHON_PATH%" main.py %*
endlocal
