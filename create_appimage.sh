#!/bin/bash
# Create Linux AppImage

echo "============================================================"
echo "Creating Linux AppImage"
echo "============================================================"
echo ""

# Check if executable exists
if [ ! -f "dist/ImageDenoiser" ]; then
    echo "[ERROR] ImageDenoiser executable not found. Run build_installer.sh first."
    exit 1
fi

# Create AppDir structure
echo "Creating AppDir structure..."
mkdir -p AppDir/usr/bin
mkdir -p AppDir/usr/share/applications
mkdir -p AppDir/usr/share/icons/hicolor/256x256/apps

# Copy executable
cp dist/ImageDenoiser AppDir/usr/bin/

# Create desktop entry
cat > AppDir/usr/share/applications/imagedenoiser.desktop << EOF
[Desktop Entry]
Type=Application
Name=Image Denoiser
Comment=Batch image denoising with multiple filters
Exec=ImageDenoiser
Icon=imagedenoiser
Categories=Graphics;Photography;
Terminal=false
EOF

# Copy icon (if exists)
if [ -f "icon.png" ]; then
    cp icon.png AppDir/usr/share/icons/hicolor/256x256/apps/imagedenoiser.png
fi

# Create AppRun script
cat > AppDir/AppRun << 'EOF'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
exec "${HERE}/usr/bin/ImageDenoiser" "$@"
EOF

chmod +x AppDir/AppRun

# Download appimagetool if not present
if [ ! -f "appimagetool-x86_64.AppImage" ]; then
    echo "Downloading appimagetool..."
    wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x appimagetool-x86_64.AppImage
fi

# Create AppImage
echo "Creating AppImage..."
./appimagetool-x86_64.AppImage AppDir dist/ImageDenoiser-x86_64.AppImage

echo ""
echo "============================================================"
echo "AppImage created: dist/ImageDenoiser-x86_64.AppImage"
echo ""
echo "Users can:"
echo "  1. Download the AppImage"
echo "  2. Make it executable: chmod +x ImageDenoiser-x86_64.AppImage"
echo "  3. Run it: ./ImageDenoiser-x86_64.AppImage"
echo ""
echo "No installation required!"
echo "============================================================"
