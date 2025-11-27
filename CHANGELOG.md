# Changelog

## [2.0.0] - Major Refactor & GUI Addition

### 🎉 New Features

#### Graphical User Interface
- **Added GUI application** (`gui.py`) with tkinter for easy, visual operation
- Browse buttons for folder selection
- Real-time processing log display
- Interactive filter parameter adjustment
- No need to manually edit config files
- Launch scripts: `run_gui.bat` (Windows) and `run_gui.sh` (Mac/Linux)

#### Automated Dependency Installation
- **Installation scripts** for all platforms:
  - `install_dependencies.py` - Cross-platform Python installer
  - `install_dependencies.bat` - Windows batch script
  - `install_dependencies.sh` - Unix/Linux/Mac shell script
- Automatic verification of installed packages
- `requirements.txt` for standard pip installation

#### Quality Metrics & Reporting
- **Noise reduction metrics** calculated for each filter
- **PSNR (Peak Signal-to-Noise Ratio)** quality measurements
- **CSV export** with timestamped metrics for all processed images
- Real-time metric display during processing

### 🔧 Improvements

#### Code Architecture
- **Modularized codebase** split into focused modules:
  - `config_loader.py` - Configuration management with dataclasses
  - `image_io.py` - Image loading/saving operations
  - `image_filters.py` - Filter implementations
  - `metrics.py` - Metrics calculation and CSV export
  - `processor.py` - Batch processing logic
  - `denoiserBatch.py` - Main entry point (now only 40 lines)
- Improved code readability and maintainability
- Better separation of concerns
- Easier to test and extend

#### Configuration System
- **Comprehensive config.ini** with all parameters exposed
- Output format control (PNG, JPEG, TIFF)
- JPEG quality settings
- Individual filter enable/disable toggles
- All filter parameters configurable:
  - Gaussian: sigma adjustment
  - Median: filter size control
  - Non-local means: h_multiplier, patch_size, patch_distance, fast_mode
- Fallback defaults for all settings

#### Image Processing
- **Better output quality** - PNG default (lossless)
- Configurable JPEG quality (1-100)
- Option to preserve original file formats
- Support for more formats (added TIFF)
- **Case-insensitive** file extension matching
- Improved error handling per image (one failure doesn't stop batch)

#### User Experience
- **Progress tracking** - Shows [X/Total] for each image
- Detailed logging with timestamps
- Filter parameters displayed in log output
- Better error messages
- Processing continues even if individual images fail

### 📚 Documentation

- **USAGE.md** - Comprehensive usage guide with:
  - Quick start for both GUI and CLI modes
  - Detailed configuration explanations
  - Tuning guides for each filter
  - Example workflows for different noise levels
  - Troubleshooting section
  - Tips and best practices
- **CHANGELOG.md** - This file documenting all changes

### 🐛 Bug Fixes

- Removed duplicate imports (`denoise_nl_means`, `estimate_sigma`)
- Removed unused imports (`data`, `img_as_float`, `peak_signal_noise_ratio`, `random_noise`, `matplotlib`)
- Fixed incorrect `dpi` parameter usage in image saving
- Fixed redundant `img is not None` check
- Improved file extension comparison (now properly case-insensitive)
- Better memory efficiency (no longer stores all images in memory)

### 🗑️ Removed

- Matplotlib dependency (no longer needed)
- Unused helper function `append_extension` (replaced with cleaner implementation)
- Hardcoded parameters (now all configurable)
- Inconsistent DPI values across filters

### ⚡ Performance

- Memory optimization - processes images one at a time instead of loading all
- Configurable fast_mode for non-local means filter
- Option to disable unused filters to speed up processing

### 📦 Project Structure

```
image-denoiser/
├── gui.py                      # GUI application
├── denoiserBatch.py           # CLI entry point
├── config_loader.py           # Configuration management
├── image_io.py                # Image I/O operations
├── image_filters.py           # Filter implementations
├── metrics.py                 # Metrics calculation
├── processor.py               # Batch processing logic
├── config.ini                 # Configuration file
├── requirements.txt           # Python dependencies
├── install_dependencies.py    # Dependency installer
├── install_dependencies.bat   # Windows installer
├── install_dependencies.sh    # Unix/Linux/Mac installer
├── run_gui.bat               # Windows GUI launcher
├── run_gui.sh                # Unix/Linux/Mac GUI launcher
├── USAGE.md                  # User guide
├── CHANGELOG.md              # This file
└── README.md                 # Project overview
```

---

## [1.0.0] - Initial Release

### Features
- Basic batch image denoising
- Three filters: Gaussian, Median, Non-local means
- Hardcoded parameters
- JPEG output only
- Basic console logging
