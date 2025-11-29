@echo off
REM Windows batch script to run GUI
REM Using pythonw.exe to run without console window

REM Try pythonw first (no console window)
where pythonw >nul 2>&1
if %errorlevel% equ 0 (
    start "" pythonw gui.py
) else (
    REM Fallback to python if pythonw not found
    python gui.py
)
