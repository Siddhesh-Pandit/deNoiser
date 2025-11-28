# Installation Documentation Summary

Complete overview of all installation resources for Image Denoiser.

## Documentation Files

### For Windows Users

| File | Purpose | Time | Audience |
|------|---------|------|----------|
| **QUICKSTART_WINDOWS.md** | Fast 5-minute guide | 2-5 min | Everyone |
| **WINDOWS_INSTALL.md** | Complete step-by-step guide | 10-15 min | Beginners |
| **README.md** | Project overview with quick links | 5 min | Everyone |

### For All Platforms

| File | Purpose | Audience |
|------|---------|----------|
| **README.md** | Main project documentation | Everyone |
| **USAGE.md** | Complete user guide | Users |
| **BUILD_INSTRUCTIONS.md** | Building executables | Developers |
| **DEPENDENCY_AUDIT.md** | Dependency verification | Developers |

## Installation Methods

### Method 1: Standalone Executable (Easiest)

**Platforms:** Windows, macOS, Linux

**Steps:**
1. Download from Releases
2. Run the executable
3. Done!

**Pros:**
- No Python needed
- No dependencies
- Works immediately

**Cons:**
- Larger file size
- May trigger antivirus

**Documentation:**
- Windows: QUICKSTART_WINDOWS.md
- All platforms: README.md

---

### Method 2: Run from Source (Developers)

**Platforms:** Windows, macOS, Linux

**Steps:**
1. Install Python 3.8-3.13
2. Download/clone repository
3. Run installer script
4. Launch application

**Pros:**
- Can modify code
- Smaller download
- Latest features

**Cons:**
- Requires Python
- More setup steps

**Documentation:**
- Windows: WINDOWS_INSTALL.md (detailed) or QUICKSTART_WINDOWS.md (fast)
- All platforms: README.md, USAGE.md

---

## Installation Scripts

### Automated Installers

| Script | Platform | What It Does |
|--------|----------|--------------|
| `install_dependencies.bat` | Windows | One-click dependency installation |
| `install_dependencies.sh` | Mac/Linux | One-click dependency installation |
| `install_dependencies.py` | All | Cross-platform Python installer |

### Launcher Scripts

| Script | Platform | What It Does |
|--------|----------|--------------|
| `run_gui.bat` | Windows | Launch GUI application |
| `run_gui.sh` | Mac/Linux | Launch GUI application |

### Requirements Files

| File | Purpose |
|------|---------|
| `requirements.txt` | All dependencies (for pip) |
| `requirements-core.txt` | Core dependencies (used by installer) |
| `requirements-raw.txt` | Optional RAW support (used by installer) |

---

## Quick Reference by User Type

### 🎯 Casual User (Just Want to Use It)

**Best Path:** Standalone Executable

**Steps:**
1. Download .exe/.app/.AppImage
2. Run it
3. Done!

**Read:** QUICKSTART_WINDOWS.md (Windows) or README.md (other platforms)

---

### 👨‍💻 Developer (Want to Modify Code)

**Best Path:** Run from Source

**Steps:**
1. Install Python 3.12
2. Clone repository
3. Run `install_dependencies.bat` (Windows) or `install_dependencies.sh` (Mac/Linux)
4. Run `run_gui.bat` or `python gui.py`

**Read:** WINDOWS_INSTALL.md (Windows) or README.md (other platforms)

---

### 🏗️ Builder (Want to Create Executables)

**Best Path:** Build from Source

**Steps:**
1. Follow developer setup
2. Install PyInstaller
3. Run build scripts

**Read:** BUILD_INSTRUCTIONS.md

---

## Troubleshooting Resources

### By Issue Type

| Issue | Documentation |
|-------|---------------|
| Python not found | WINDOWS_INSTALL.md → Troubleshooting |
| Dependencies won't install | WINDOWS_INSTALL.md → Troubleshooting |
| Antivirus warnings | WINDOWS_INSTALL.md → Antivirus Warnings |
| RAW support issues | USAGE.md → RAW Format Notes |
| Build issues | BUILD_INSTRUCTIONS.md → Troubleshooting |
| Missing dependencies | DEPENDENCY_AUDIT.md |

### By Platform

| Platform | Primary Resource |
|----------|-----------------|
| Windows | WINDOWS_INSTALL.md |
| macOS | README.md + USAGE.md |
| Linux | README.md + USAGE.md |

---

## Installation Verification

After installation, verify everything works:

### Quick Test
```bash
# Run GUI
python gui.py  # or run_gui.bat on Windows

# Should open without errors
```

### Full Test
```bash
# Run dependency verification
python install_dependencies.py

# Should show all packages installed
```

### Feature Test
1. Open GUI
2. Select test images
3. Use "📷 Photos" preset
4. Click "Start Processing"
5. Click "🔍 View Comparison"

All features should work without errors.

---

## Getting Help

### Documentation Order

1. **Quick Start:** QUICKSTART_WINDOWS.md (Windows) or README.md
2. **Detailed Setup:** WINDOWS_INSTALL.md (Windows) or USAGE.md
3. **Troubleshooting:** Check relevant guide's troubleshooting section
4. **Advanced:** BUILD_INSTRUCTIONS.md, DEPENDENCY_AUDIT.md

### Support Channels

- 📖 Documentation: See files above
- 🐛 Bug Reports: GitHub Issues
- 💡 Feature Requests: GitHub Issues
- ❓ Questions: GitHub Discussions

---

## Summary

**Windows Users:**
- **Fastest:** QUICKSTART_WINDOWS.md (5 minutes)
- **Most Complete:** WINDOWS_INSTALL.md (detailed)
- **Overview:** README.md

**Other Platforms:**
- **Start Here:** README.md
- **Full Guide:** USAGE.md
- **Building:** BUILD_INSTRUCTIONS.md

**All Users:**
- Installation scripts handle dependencies automatically
- Standalone executables require no setup
- Documentation covers all common issues
