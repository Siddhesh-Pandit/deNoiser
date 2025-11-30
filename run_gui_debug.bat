@echo off
echo Starting Image Denoiser with debug logging...
echo.
echo All processing logs will appear in this window.
echo Keep this window open while using the GUI.
echo.
python -u gui.py 2>&1
echo.
echo GUI closed.
pause
