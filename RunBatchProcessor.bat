@echo off
:: Check if Python 3.11 is available
py -3.11 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python 3.11 is not installed. Please install it from https://www.python.org/
    pause
    exit /b
)

:: Run the script with Python 3.11
py -3.11 BatchProcessor.py
pause
