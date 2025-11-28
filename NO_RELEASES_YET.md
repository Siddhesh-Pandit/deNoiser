# No Pre-Built Releases Yet

## Current Status

This project doesn't have pre-built executables (.exe, .app, .AppImage) available yet.

## How to Use It Now

**Everyone must install from source** - but it's easy! Takes ~5 minutes.

### Quick Steps:

1. **Install Python 3.12** from [python.org](https://www.python.org/downloads/)
2. **Download this project** (green "Code" button → Download ZIP)
3. **Extract and run installer**:
   - Windows: Double-click `install_dependencies.bat`
   - Mac/Linux: Run `./install_dependencies.sh`
4. **Run the app**:
   - Windows: Double-click `run_gui.bat`
   - Mac/Linux: Run `./run_gui.sh`

**Full instructions:** See [START_HERE.md](START_HERE.md)

---

## Future: Pre-Built Releases

Once releases are created, you'll be able to:

### Windows
- Download `ImageDenoiser.exe`
- Double-click to run
- No Python or setup needed

### macOS
- Download `ImageDenoiser.dmg`
- Drag to Applications
- Launch like any app

### Linux
- Download `ImageDenoiser.AppImage`
- Make executable and run
- Or install `.deb` package

---

## Want to Build Your Own Executable?

You can create your own standalone executable right now!

See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) for:
- Building Windows .exe
- Building macOS .app and .dmg
- Building Linux AppImage and .deb

This lets you:
- Create a portable version
- Share with others who don't have Python
- Run without dependencies

---

## Why No Releases Yet?

Releases require:
1. Testing on multiple platforms
2. Code signing (for security)
3. Creating installers for each OS
4. Setting up CI/CD pipeline

The project is fully functional - just needs packaging for distribution.

---

## Questions?

**"Do I need to know Python?"**
- No! Just install it and follow the steps

**"Is it hard to install?"**
- No! Takes 5 minutes with automated scripts

**"Will there be releases soon?"**
- Check the [Releases page](../../releases) for updates

**"Can I help create releases?"**
- Yes! See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) and contribute
