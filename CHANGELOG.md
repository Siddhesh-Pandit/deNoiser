# Changelog

## [Unreleased]

### 🤖 AI Denoising Revolution

#### Neural Network Models
- **SCUNet model** - Fast, 3MB, recommended for most use cases
- **NAFNet model** - Better quality, 9MB (with fallback URL handling)
- **Auto-padding** - Handles any image dimensions (pads to divisible by 8, crops back)
- **Automatic fallback** - Uses classical filters if AI fails
- **GPU acceleration** - NVIDIA CUDA, Apple Silicon MPS, AMD ROCm (Linux)
- **One-click installation** - In-GUI PyTorch installation with progress window
- **Real-time progress** - Shows model loading, processing stages, completion
- **Smart error handling** - Helpful messages for dimension issues, missing dependencies

#### AI User Experience
- **Auto-opening log window** - Opens automatically when AI processing starts
- **AI status label** - Real-time feedback (🤖 Loading model, Processing, ✓ Complete, ⚠ Failed)
- **Progress callbacks** - Visual feedback during model download and inference
- **Fallback messaging** - Clear indication when AI falls back to classical filters

### 🎨 Advanced Features

#### Selective Denoising
- **Mask editor** - Paint areas to denoise, leave rest untouched
- **Brush tools** - Adjustable size, opacity, hardness
- **Quick actions** - Invert, clear, fill all
- **Mask preview** - See exactly what will be processed
- **Mask caching** - Remembers masks per image
- **Works with all filters** - AI and classical filters respect masks

#### Output Settings & Post-Processing
- **Sharpening** - Restore structure after denoising (amount, radius controls)
- **Saturation boost** - Enhance color vibrancy
- **Brightness adjustment** - Lighten or darken output
- **Mask-aware** - Post-processing only affects masked areas
- **Color preservation** - Denoise luminance only (classical filters)
- **Format flexibility** - PNG, JPEG, TIFF with quality control

#### Interactive Comparison
- **"🔍 View Comparison" button** - Always visible after processing
- **Draggable slider** - Smooth before/after reveal
- **Zoom controls** - 25%-400% zoom with mouse wheel support
- **Scrollable canvas** - Navigate large zoomed images
- **Works with AI** - Automatically finds AI or classical output
- **Fallback detection** - Shows classical output if AI failed

### 🚀 User Experience Improvements

#### Processing Control
- **⏹ Cancel button** - Stop processing mid-batch without corrupting files
- **Cancellation points** - Checks between images for clean exit
- **Partial results** - Saves completed images before cancellation
- **Thread-safe** - Proper flag handling across threads

#### Visual Feedback
- **Progress tracking** - Real-time file count and percentage
- **Status messages** - Clear indication of current operation
- **Error visibility** - Prominent display of issues with helpful tips
- **Console logging** - `run_gui_debug.bat` for detailed debugging

#### Quick Presets
- **📷 Photos** - Optimized for portraits, landscapes
- **📄 Documents** - Best for scanned text
- **🌙 Low-Light** - Aggressive noise removal for night photos
- **🔍 Compare All** - Enable all filters to see which works best

### 🔧 Technical Improvements

#### Comparison Window Enhancements
- **AI file detection** - Looks for `_ai` suffix files
- **Fallback logic** - Checks classical outputs if AI files missing
- **Multiple filter support** - Handles gaussian_ai, median_ai, nonlocal_ai
- **Detailed error messages** - Shows exactly which files were checked
- **Debug logging** - Tracks file lookup process

#### AI Processing Pipeline
- **Dimension validation** - Auto-pads images to model requirements
- **Tensor handling** - Proper conversion between NumPy and PyTorch
- **Memory management** - Efficient GPU/CPU memory usage
- **Error recovery** - Graceful degradation on failures

#### Metrics & Reporting
- **AI metrics columns** - CSV includes AI filter results
- **Comparison data** - Side-by-side classical vs AI performance
- **Extended fieldnames** - gaussian_ai, median_ai, nonlocal_ai columns

### 📚 Documentation Expansion

#### User Guides
- **AI_DENOISING_GUIDE.md** - Complete AI setup and usage
- **SELECTIVE_DENOISING.md** - Mask editor tutorial
- **OUTPUT_SETTINGS_GUIDE.md** - Post-processing options
- **QUICKSTART_WINDOWS.md** - 5-minute installation
- **WINDOWS_INSTALL.md** - Detailed Windows setup

#### Technical Documentation
- **AI_PADDING_FIX.md** - Auto-padding implementation
- **AI_FALLBACK_FIX.md** - Fallback architecture
- **AI_PROGRESS_FEEDBACK.md** - Real-time status system
- **CANCEL_BUTTON_FEATURE.md** - Cancellation implementation
- **FEATURE_COMPARISON_WINDOW.md** - Comparison window details
- **BUGFIX_AI_COMPARISON.md** - File detection fixes

#### Installation & Setup
- **AI_INSTALLATION_OPTIONS.md** - All installation methods
- **AMD_GPU_SETUP.md** - ROCm setup for Linux
- **BUILD_INSTRUCTIONS.md** - Create standalone executables

#### Project Information
- **EVOLUTION_BLOG.md** - Journey from script to full app
- **LICENSE_INFO.md** - License details and commercial use

### 🐛 Bug Fixes

#### AI Processing
- Fixed tensor dimension mismatch with auto-padding
- Fixed AI fallback not working in folder processing mode
- Fixed comparison window not finding AI output files
- Fixed NAFNet download with fallback URL handling

#### Comparison Window
- Fixed file detection for double-extension filenames (e.g., `image.NEF.jpg`)
- Fixed comparison window only checking for `nonlocal_ai` files
- Added fallback to classical outputs when AI files missing
- Improved error messages showing checked file paths

#### Output Settings
- Fixed output settings not applying to AI mode
- Fixed mask-aware post-processing (sharpening, saturation, brightness)
- Fixed preserve color setting (now only affects classical filters)

### ⚡ Performance

- **GPU acceleration** - 10-100x faster with CUDA/MPS/ROCm
- **Efficient padding** - Minimal overhead (<1% extra pixels typically)
- **Smart caching** - Model loaded once, reused for all images
- **Cancellable operations** - No wasted processing time

### 🔒 Stability

- **Graceful degradation** - AI fails → Classical filters
- **Error resilience** - Try primary URL → Try fallback → Use CPU
- **Thread safety** - Proper synchronization for GUI updates
- **Clean cancellation** - No corrupted files or bad state

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
