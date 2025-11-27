@echo off
REM Windows batch script to build installer

echo ============================================================
echo Image Denoiser - Windows Installer Builder
echo ============================================================
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if %errorlevel% neq 0 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
    echo.
)

echo Building Windows executable...
echo This may take several minutes...
echo.

python build_installer.py

echo.
echo ============================================================
echo Build complete!
echo.
echo The executable is located at: dist\ImageDenoiser.exe
echo.
echo You can distribute this single file to users.
echo No Python installation required!
echo ============================================================
echo.
pause
