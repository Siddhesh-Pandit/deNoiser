#!/bin/bash
# Create Debian/Ubuntu .deb package

echo "============================================================"
echo "Creating Debian Package (.deb)"
echo "============================================================"
echo ""

# Check if executable exists
if [ ! -f "dist/ImageDenoiser" ]; then
    echo "[ERROR] ImageDenoiser executable not found. Run build_installer.sh first."
    exit 1
fi

# Package info
PACKAGE_NAME="imagedenoiser"
VERSION="2.0.0"
ARCH="amd64"

# Create package structure
echo "Creating package structure..."
mkdir -p "deb/${PACKAGE_NAME}_${VERSION}_${ARCH}/DEBIAN"
mkdir -p "deb/${PACKAGE_NAME}_${VERSION}_${ARCH}/usr/bin"
mkdir -p "deb/${PACKAGE_NAME}_${VERSION}_${ARCH}/usr/share/applications"
mkdir -p "deb/${PACKAGE_NAME}_${VERSION}_${ARCH}/usr/share/doc/${PACKAGE_NAME}"
mkdir -p "deb/${PACKAGE_NAME}_${VERSION}_${ARCH}/usr/share/icons/hicolor/256x256/apps"

# Copy executable
cp dist/ImageDenoiser "deb/${PACKAGE_NAME}_${VERSION}_${ARCH}/usr/bin/"
chmod +x "deb/${PACKAGE_NAME}_${VERSION}_${ARCH}/usr/bin/ImageDenoiser"

# Create control file
cat > "deb/${PACKAGE_NAME}_${VERSION}_${ARCH}/DEBIAN/control" << EOF
Package: ${PACKAGE_NAME}
Version: ${VERSION}
Section: graphics
Priority: optional
Architecture: ${ARCH}
Maintainer: Image Denoiser Team
Description: Batch image denoising tool
 A powerful batch image denoising tool with GUI and CLI interfaces.
 Applies multiple noise reduction filters and provides quality metrics.
 .
 Features:
  - Three denoising filters (Gaussian, Median, Non-local means)
  - Color preservation mode
  - RAW format support
  - Batch processing
  - Quality metrics (PSNR, noise reduction %)
EOF

# Create desktop entry
cat > "deb/${PACKAGE_NAME}_${VERSION}_${ARCH}/usr/share/applications/${PACKAGE_NAME}.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Image Denoiser
Comment=Batch image denoising with multiple filters
Exec=/usr/bin/ImageDenoiser
Icon=imagedenoiser
Categories=Graphics;Photography;
Terminal=false
EOF

# Copy documentation
cp README.md "deb/${PACKAGE_NAME}_${VERSION}_${ARCH}/usr/share/doc/${PACKAGE_NAME}/"
cp USAGE.md "deb/${PACKAGE_NAME}_${VERSION}_${ARCH}/usr/share/doc/${PACKAGE_NAME}/"

# Copy icon (if exists)
if [ -f "icon.png" ]; then
    cp icon.png "deb/${PACKAGE_NAME}_${VERSION}_${ARCH}/usr/share/icons/hicolor/256x256/apps/${PACKAGE_NAME}.png"
fi

# Build package
echo "Building .deb package..."
dpkg-deb --build "deb/${PACKAGE_NAME}_${VERSION}_${ARCH}"

# Move to dist
mv "deb/${PACKAGE_NAME}_${VERSION}_${ARCH}.deb" dist/

echo ""
echo "============================================================"
echo "Debian package created: dist/${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"
echo ""
echo "Users can install with:"
echo "  sudo dpkg -i ${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"
echo ""
echo "Or double-click in file manager to install via Software Center"
echo "============================================================"
