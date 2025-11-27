#!/bin/bash
# Unix/Linux/Mac shell script to build installer

echo "============================================================"
echo "Image Denoiser - Unix/Linux/Mac Installer Builder"
echo "============================================================"
echo ""

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     PLATFORM=Linux;;
    Darwin*)    PLATFORM=Mac;;
    *)          PLATFORM="Unknown"
esac

echo "Detected platform: $PLATFORM"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    exit 1
fi

# Check if PyInstaller is installed
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "PyInstaller not found. Installing..."
    python3 -m pip install pyinstaller
    echo ""
fi

echo "Building executable for $PLATFORM..."
echo "This may take several minutes..."
echo ""

# Build using PyInstaller
python3 -m PyInstaller \
    --onefile \
    --windowed \
    --name=ImageDenoiser \
    --add-data="config.ini:." \
    --add-data="README.md:." \
    --add-data="USAGE.md:." \
    --hidden-import=skimage.restoration \
    --hidden-import=skimage.metrics \
    --hidden-import=scipy.ndimage \
    --hidden-import=pywt \
    --hidden-import=rawpy \
    --collect-all=skimage \
    --collect-all=scipy \
    --collect-all=pywt \
    --noconfirm \
    gui.py

echo ""
echo "============================================================"
echo "Build complete!"
echo ""

if [ "$PLATFORM" = "Mac" ]; then
    echo "Application bundle: dist/ImageDenoiser.app"
    echo ""
    echo "To create a DMG installer:"
    echo "  1. Install create-dmg: brew install create-dmg"
    echo "  2. Run: ./create_dmg.sh"
else
    echo "Executable: dist/ImageDenoiser"
    echo ""
    echo "To make it executable:"
    echo "  chmod +x dist/ImageDenoiser"
fi

echo ""
echo "You can distribute this to users without Python!"
echo "============================================================"
