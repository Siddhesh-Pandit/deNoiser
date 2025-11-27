@echo off
REM Windows batch script to install dependencies

echo ============================================================
echo Image Denoiser - Dependency Installer (Windows)
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.7 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo Checking Python version...
python --version
echo.

python install_dependencies.py

echo.
pause
