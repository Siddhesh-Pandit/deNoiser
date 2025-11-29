@echo off
REM Windows batch script to install AI dependencies

echo ============================================================
echo Image Denoiser - AI Dependencies Installer (Windows)
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
    pause
    exit /b 1
)

echo This will install PyTorch for AI denoising (~500MB download).
echo.
echo Press Ctrl+C to cancel, or
pause

echo.
echo Installing AI dependencies...
echo This may take several minutes...
echo.

python -m pip install -r requirements-ai.txt

if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo AI dependencies installed successfully!
    echo ============================================================
    echo.
    echo You can now use AI denoising in the GUI.
    echo Enable it in the "AI Denoiser" section.
    echo.
) else (
    echo.
    echo ============================================================
    echo Installation failed!
    echo ============================================================
    echo.
    echo Please try manually:
    echo   pip install -r requirements-ai.txt
    echo.
)

pause
