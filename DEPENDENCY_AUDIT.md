# Dependency Audit - Complete Coverage Check

## Summary

✅ **All dependencies are properly covered** in the installer scripts.

## Core Dependencies (Required)

These are installed by `install_dependencies.py` using `requirements-core.txt`:

| Package | Version | Used In | Purpose | Status |
|---------|---------|---------|---------|--------|
| numpy | >=1.20.0 | All modules | Array operations, image data | ✅ Covered |
| scikit-image | >=0.19.0 | image_io, image_filters, metrics | Image processing, denoising algorithms | ✅ Covered |
| scipy | >=1.7.0 | image_filters | Gaussian filter (ndimage) | ✅ Covered |
| PyWavelets | >=1.1.1 | (scikit-image dependency) | Wavelet transforms | ✅ Covered |
| Pillow | >=9.0.0 | gui.py, create_icon.py | GUI comparison window, icon creation | ✅ **FIXED** |

## Optional Dependencies

These are attempted by `install_dependencies.py` using `requirements-raw.txt`:

| Package | Version | Used In | Purpose | Status |
|---------|---------|---------|---------|--------|
| rawpy | >=0.18.0 | image_io | RAW image format support | ✅ Covered (optional) |

**Note:** rawpy installation may fail on Python 3.14+ (not yet supported). The installer handles this gracefully.

## Built-in Python Modules (No Installation Needed)

| Module | Used In | Purpose |
|--------|---------|---------|
| tkinter | gui.py, tooltip.py | GUI framework |
| os | All modules | File system operations |
| sys | Multiple modules | System information, paths |
| logging | Multiple modules | Logging and debugging |
| configparser | config_loader.py | Config file parsing |
| dataclasses | config_loader.py | Configuration data structures |
| csv | metrics.py | CSV export |
| datetime | metrics.py | Timestamps |
| threading | gui.py | Background processing |
| subprocess | install_dependencies.py | Dependency installation |

## Build-Only Dependencies (Not in Runtime Requirements)

| Package | Purpose | When Needed |
|---------|---------|-------------|
| PyInstaller | Create standalone executables | Only for building installers |

**Note:** PyInstaller is documented in BUILD_INSTRUCTIONS.md but not in requirements files since it's only needed for building, not running.

## Installation Files

### requirements.txt
- **Purpose:** Standard pip installation
- **Contains:** All core dependencies
- **Usage:** `pip install -r requirements.txt`

### requirements-core.txt
- **Purpose:** Used by install_dependencies.py for core packages
- **Contains:** numpy, scikit-image, scipy, PyWavelets, Pillow
- **Usage:** Automatic via installer scripts

### requirements-raw.txt
- **Purpose:** Used by install_dependencies.py for optional RAW support
- **Contains:** rawpy
- **Usage:** Automatic via installer scripts (fails gracefully if unavailable)

## Verification

The `install_dependencies.py` script includes a verification function that checks:

✅ numpy  
✅ scikit-image (imported as 'skimage')  
✅ scipy  
✅ PyWavelets (imported as 'pywt')  
✅ Pillow (imported as 'PIL')  
⚠️ rawpy (optional, warns if not available)

## Recent Fix

**Issue Found:** Pillow was missing from `requirements-core.txt`
- Pillow was in `requirements.txt` but not in `requirements-core.txt`
- The installer scripts use `requirements-core.txt`
- This would cause GUI comparison window to fail

**Fix Applied:**
1. ✅ Added `Pillow>=9.0.0` to `requirements-core.txt`
2. ✅ Added `'PIL': 'Pillow'` to verification in `install_dependencies.py`

## Testing Recommendations

To verify complete dependency coverage:

```bash
# 1. Fresh virtual environment
python -m venv test_env
source test_env/bin/activate  # or test_env\Scripts\activate on Windows

# 2. Run installer
python install_dependencies.py

# 3. Test all features
python gui.py  # Should open GUI with all features working
python denoiserBatch.py  # Should run CLI version

# 4. Test comparison window (requires Pillow)
python test_comparison.py  # Should open before/after window
```

## Conclusion

✅ **All dependencies are now properly covered**
- Core dependencies: Complete
- Optional dependencies: Handled gracefully
- Built-in modules: No action needed
- Build dependencies: Documented separately
- Verification: Includes all required packages
