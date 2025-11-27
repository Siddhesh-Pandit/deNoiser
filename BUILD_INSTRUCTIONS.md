# Building Windows Installer

This guide explains how to create a standalone Windows executable for Image Denoiser.

## Prerequisites

1. **Python 3.8-3.13** installed on Windows
2. **All dependencies** installed:
   ```bash
   pip install -r requirements-core.txt
   pip install pyinstaller
   ```

## Quick Build

### Option 1: Using the Build Script (Recommended)

Simply run:
```bash
build_installer.bat
```

This will:
- Check if PyInstaller is installed (installs if needed)
- Build the executable
- Create `dist/ImageDenoiser.exe`

### Option 2: Manual Build

```bash
# Install PyInstaller
pip install pyinstaller

# Build using spec file
pyinstaller ImageDenoiser.spec

# Or build directly
pyinstaller --onefile --windowed --name=ImageDenoiser gui.py
```

## Output

After building, you'll find:
- **dist/ImageDenoiser.exe** - Standalone executable (~100-150 MB)
- **build/** - Temporary build files (can be deleted)

## Distribution

The `ImageDenoiser.exe` file is completely standalone:
- ✅ No Python installation required
- ✅ All dependencies included
- ✅ Single file distribution
- ✅ Works on any Windows 10/11 system

Simply share the `.exe` file with users!

## Customization

### Add an Icon

1. Create or download an `.ico` file
2. Save it as `icon.ico` in the project root
3. Rebuild the installer

### Reduce File Size

Edit `ImageDenoiser.spec` and add to `excludes`:
```python
excludes=['matplotlib', 'IPython', 'notebook'],
```

### Include Additional Files

Edit `ImageDenoiser.spec` and add to `datas`:
```python
datas=[
    ('config.ini', '.'),
    ('README.md', '.'),
    ('USAGE.md', '.'),
    ('examples/', 'examples'),  # Add example folder
],
```

## Troubleshooting

### "PyInstaller not found"
```bash
pip install pyinstaller
```

### "Module not found" errors
Make sure all dependencies are installed:
```bash
pip install -r requirements-core.txt
```

### Large file size
This is normal - the executable includes Python and all libraries. Typical size: 100-150 MB.

### Antivirus warnings
Some antivirus software may flag PyInstaller executables as suspicious. This is a false positive. You can:
- Submit the file to your antivirus vendor for whitelisting
- Sign the executable with a code signing certificate (for professional distribution)

## Advanced: Code Signing (Optional)

For professional distribution, consider code signing:

1. Obtain a code signing certificate
2. Use `signtool.exe` (Windows SDK):
   ```bash
   signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com dist/ImageDenoiser.exe
   ```

This removes Windows SmartScreen warnings and builds user trust.

## Creating an Installer Package (Optional)

For a more professional installer with Start Menu shortcuts:

### Using Inno Setup

1. Download [Inno Setup](https://jrsoftware.org/isinfo.php)
2. Create `installer.iss`:
   ```ini
   [Setup]
   AppName=Image Denoiser
   AppVersion=2.0
   DefaultDirName={pf}\ImageDenoiser
   DefaultGroupName=Image Denoiser
   OutputDir=installer
   OutputBaseFilename=ImageDenoiser-Setup
   
   [Files]
   Source: "dist\ImageDenoiser.exe"; DestDir: "{app}"
   Source: "README.md"; DestDir: "{app}"
   Source: "USAGE.md"; DestDir: "{app}"
   
   [Icons]
   Name: "{group}\Image Denoiser"; Filename: "{app}\ImageDenoiser.exe"
   Name: "{commondesktop}\Image Denoiser"; Filename: "{app}\ImageDenoiser.exe"
   ```
3. Compile with Inno Setup

This creates a professional installer with uninstaller, Start Menu shortcuts, and desktop icon.

## Notes

- Build on the oldest Windows version you want to support
- Test the executable on a clean Windows system without Python
- The first run may be slower as Windows scans the executable
- Consider creating both 32-bit and 64-bit versions for maximum compatibility

---

# Building macOS Installer

## Prerequisites

1. **macOS** system
2. **Python 3.8-3.13** installed
3. **Homebrew** (for create-dmg): https://brew.sh

## Quick Build

### Step 1: Build the Application

```bash
chmod +x build_installer.sh
./build_installer.sh
```

This creates `dist/ImageDenoiser.app`

### Step 2: Create DMG Installer (Optional)

```bash
chmod +x create_dmg.sh
./create_dmg.sh
```

This creates `dist/ImageDenoiser-Installer.dmg`

## Output

- **ImageDenoiser.app** - macOS application bundle
- **ImageDenoiser-Installer.dmg** - Drag-to-install DMG

## Distribution

Users can:
1. Open the DMG
2. Drag ImageDenoiser to Applications folder
3. Launch from Applications

## Code Signing (Recommended)

For distribution outside the App Store:

```bash
# Sign the app
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" dist/ImageDenoiser.app

# Notarize with Apple
xcrun notarytool submit dist/ImageDenoiser-Installer.dmg --apple-id your@email.com --password app-specific-password --team-id TEAMID
```

This removes Gatekeeper warnings.

---

# Building Linux Installer

## Prerequisites

1. **Linux** system (Ubuntu, Debian, Fedora, etc.)
2. **Python 3.8-3.13** installed

## Quick Build

### Option 1: AppImage (Universal)

```bash
chmod +x build_installer.sh
./build_installer.sh

chmod +x create_appimage.sh
./create_appimage.sh
```

Creates: `dist/ImageDenoiser-x86_64.AppImage`

**Benefits:**
- Works on all Linux distributions
- No installation required
- Single file distribution

### Option 2: Debian Package (.deb)

```bash
chmod +x build_installer.sh
./build_installer.sh

chmod +x create_deb.sh
./create_deb.sh
```

Creates: `dist/imagedenoiser_2.0.0_amd64.deb`

**Benefits:**
- Integrates with system package manager
- Automatic updates via apt
- Desktop menu integration

## Distribution

### AppImage
Users simply:
```bash
chmod +x ImageDenoiser-x86_64.AppImage
./ImageDenoiser-x86_64.AppImage
```

### Debian Package
Users install with:
```bash
sudo dpkg -i imagedenoiser_2.0.0_amd64.deb
```

Or double-click in file manager.

## Creating RPM Package (Fedora/RHEL)

For RPM-based distributions:

```bash
# Install rpmbuild
sudo dnf install rpm-build

# Create RPM structure
mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

# Create spec file (see online guides)
# Build RPM
rpmbuild -ba imagedenoiser.spec
```

---

# Cross-Platform Build Summary

| Platform | Command | Output | Size |
|----------|---------|--------|------|
| Windows | `build_installer.bat` | ImageDenoiser.exe | ~150 MB |
| macOS | `./build_installer.sh` + `./create_dmg.sh` | ImageDenoiser-Installer.dmg | ~180 MB |
| Linux (AppImage) | `./build_installer.sh` + `./create_appimage.sh` | ImageDenoiser-x86_64.AppImage | ~170 MB |
| Linux (Debian) | `./build_installer.sh` + `./create_deb.sh` | imagedenoiser_2.0.0_amd64.deb | ~150 MB |

## Tips for All Platforms

1. **Test on clean systems** without Python installed
2. **Include README** and documentation
3. **Add application icon** for professional appearance
4. **Sign executables** to avoid security warnings
5. **Create checksums** (SHA256) for downloads
6. **Provide installation instructions** for each platform
