#!/bin/bash
# Create macOS DMG installer

echo "============================================================"
echo "Creating macOS DMG Installer"
echo "============================================================"
echo ""

# Check if create-dmg is installed
if ! command -v create-dmg &> /dev/null; then
    echo "create-dmg not found. Installing via Homebrew..."
    if ! command -v brew &> /dev/null; then
        echo "[ERROR] Homebrew not installed. Install from https://brew.sh"
        exit 1
    fi
    brew install create-dmg
fi

# Check if app bundle exists
if [ ! -d "dist/ImageDenoiser.app" ]; then
    echo "[ERROR] ImageDenoiser.app not found. Run build_installer.sh first."
    exit 1
fi

# Create DMG
create-dmg \
    --volname "Image Denoiser" \
    --volicon "icon.icns" \
    --window-pos 200 120 \
    --window-size 800 400 \
    --icon-size 100 \
    --icon "ImageDenoiser.app" 200 190 \
    --hide-extension "ImageDenoiser.app" \
    --app-drop-link 600 185 \
    "dist/ImageDenoiser-Installer.dmg" \
    "dist/ImageDenoiser.app"

echo ""
echo "============================================================"
echo "DMG created: dist/ImageDenoiser-Installer.dmg"
echo ""
echo "Users can:"
echo "  1. Open the DMG"
echo "  2. Drag ImageDenoiser to Applications"
echo "  3. Launch from Applications folder"
echo "============================================================"
