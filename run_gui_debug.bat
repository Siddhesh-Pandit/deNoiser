@echo off
REM Windows batch script to run GUI with console for debugging

echo Starting Image Denoiser GUI...
echo.
python gui.py

REM Window will close automatically when GUI exits
REM If you see errors, the window will stay open briefly
if %errorlevel% neq 0 (
    echo.
    echo An error occurred. Press any key to close...
    pause >nul
)
