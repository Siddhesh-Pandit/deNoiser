# Windows Installation Guide

Complete step-by-step guide for installing Image Denoiser on Windows.

> **Note:** No pre-built executables available yet. Follow the steps below to run from source.
> Want to build your own .exe? See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)

## Installation from Source

### Prerequisites

**Step 1: Install Python**

1. Download Python from [python.org](https://www.python.org/downloads/)
   - **Recommended:** Python 3.12 (best compatibility)
   - **Supported:** Python 3.8 - 3.13
   - **Note:** Python 3.14+ won't support RAW images yet

2. Run the installer
   - ⚠️ **IMPORTANT:** Check "Add Python to PATH"
   - Click "Install Now"

3. Verify installation:
   ```cmd
   python --version
   ```
   Should show: `Python 3.12.x` (or your version)

**Step 2: Download the Project**

**Option A: Download ZIP**
1. Click the green "Code" button on GitHub
2. Select "Download ZIP"
3. Extract to a folder (e.g., `C:\ImageDenoiser`)

**Option B: Clone with Git**
```cmd
git clone https://github.com/yourusername/image-denoiser.git
cd image-denoiser
```

### Installation

**Method 1: Automatic (Recommended)**

1. Open the project folder in File Explorer
2. Double-click `install_dependencies.bat`
3. Wait for installation to complete
4. Press any key to close

The script will:
- Check Python installation
- Install all required packages
- Attempt to install RAW support (optional)
- Verify everything works

**Method 2: Manual**

Open Command Prompt in the project folder and run:

```cmd
pip install -r requirements.txt
```

For RAW support (optional):
```cmd
pip install rawpy
```

### Running the Application

**GUI Mode (Recommended):**

Double-click `run_gui.bat` in File Explorer

Or from Command Prompt:
```cmd
run_gui.bat
```

Or directly:
```cmd
python gui.py
```

**Command Line Mode:**

1. Edit `config.ini` with your settings
2. Run:
   ```cmd
   python denoiserBatch.py
   ```

---

## Troubleshooting

### "Python is not recognized"

**Problem:** Python not in PATH

**Solution:**
1. Reinstall Python
2. Make sure to check "Add Python to PATH" during installation
3. Or add manually:
   - Search "Environment Variables" in Windows
   - Edit "Path" variable
   - Add Python installation folder (e.g., `C:\Python312`)

### "pip is not recognized"

**Problem:** pip not installed or not in PATH

**Solution:**
```cmd
python -m ensurepip --upgrade
```

### "No module named 'numpy'" (or other package)

**Problem:** Dependencies not installed

**Solution:**
```cmd
python install_dependencies.py
```

Or manually:
```cmd
pip install numpy scikit-image scipy PyWavelets Pillow
```

### "Could not find a version that satisfies the requirement rawpy"

**Problem:** rawpy not available for your Python version

**Solution:**
- If Python 3.14+: RAW support not available yet (use standard formats)
- If Python 3.8-3.13: Try manual install: `pip install rawpy`
- Or skip RAW support (tool works fine without it)

### Antivirus Blocks Installation

**Problem:** Antivirus blocking pip or Python

**Solution:**
1. Temporarily disable antivirus
2. Run installation
3. Re-enable antivirus
4. Add Python folder to antivirus exceptions

### "Access Denied" Error

**Problem:** Insufficient permissions

**Solution:**
Run Command Prompt as Administrator:
1. Search "cmd" in Start Menu
2. Right-click "Command Prompt"
3. Select "Run as administrator"
4. Navigate to project folder
5. Run installation again

### GUI Window Doesn't Open

**Problem:** tkinter not installed

**Solution:**
tkinter should come with Python. If missing:
1. Reinstall Python
2. During installation, select "tcl/tk and IDLE"

---

## System Requirements

**Minimum:**
- Windows 7 or later
- 2 GB RAM
- 500 MB free disk space
- Python 3.8+ (if running from source)

**Recommended:**
- Windows 10/11
- 4 GB RAM
- 1 GB free disk space
- Python 3.12

---

## Quick Reference

### File Locations

**Project Files:**
```
C:\ImageDenoiser\          (or wherever you extracted)
├── gui.py                 Main GUI application
├── run_gui.bat           Quick launcher
├── install_dependencies.bat  Installer
└── config.ini            Configuration file
```

**Python Installation:**
```
C:\Users\YourName\AppData\Local\Programs\Python\Python312\
```

### Common Commands

```cmd
# Check Python version
python --version

# Check pip version
pip --version

# Install dependencies
install_dependencies.bat

# Run GUI
run_gui.bat

# Run CLI
python denoiserBatch.py

# Update packages
pip install --upgrade -r requirements.txt
```

---

## Next Steps

After installation:

1. **Read the User Guide:** See [USAGE.md](USAGE.md) for detailed instructions
2. **Try the GUI:** Run `run_gui.bat` and process some test images
3. **Explore Presets:** Use Quick Presets for common scenarios
4. **View Comparisons:** Use the "🔍 View Comparison" button after processing

---

## Getting Help

**Documentation:**
- [USAGE.md](USAGE.md) - Complete user guide
- [README.md](README.md) - Project overview
- [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) - Building executables

**Common Issues:**
- Check the Troubleshooting section above
- Review the log output in the GUI
- Ensure all dependencies are installed

**Still Need Help?**
- Open an issue on GitHub
- Include your Python version: `python --version`
- Include error messages from the log
