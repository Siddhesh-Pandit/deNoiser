# Image Denoiser

A powerful batch image denoising tool with AI and classical filters, featuring an intuitive GUI and comprehensive quality metrics.

> **👉 NEW USER? [START HERE](START_HERE.md) - Everything you need in one page**
>
> **🪟 Windows Users:** [5-Minute Quick Start](QUICKSTART_WINDOWS.md) | [Detailed Installation](WINDOWS_INSTALL.md)

## ✨ Features

### Core Features
- **🖼️ Modern GUI** - Intuitive interface with real-time progress and auto-opening log window
- **🤖 AI Denoising** - Neural network models (SCUNet/NAFNet) for superior quality
  - Auto-padding for any image dimensions
  - Automatic fallback to classical filters if AI fails
  - GPU acceleration (NVIDIA CUDA, Apple Silicon MPS, AMD ROCm on Linux)
- **🎯 Quick Presets** - One-click optimization for Photos, Documents, Low-Light, or Compare All
- **🔍 Interactive Comparison** - Draggable slider with zoom (25%-400%) to compare before/after
- **⏹ Cancel Anytime** - Stop processing mid-batch without corrupting files

### Denoising Methods
**Classical Filters:**
- Gaussian Filter - Fast smoothing
- Median Filter - Salt-and-pepper noise removal
- Non-local Means ⭐ - Best classical quality, preserves edges and details

**AI Models:**
- SCUNet - Fast, 3MB, recommended
- NAFNet - Better quality, 9MB (download may fail, use SCUNet)

### Advanced Features
- **🎨 Selective Denoising** - Paint mask to denoise only specific areas
- **⚙️ Output Settings** - Post-processing with sharpening, saturation boost, brightness adjustment
- **📊 Quality Metrics** - PSNR and noise reduction percentage for each filter
- **🎛️ Fully Configurable** - Adjust all filter parameters in real-time
- **📦 Batch Processing** - Process entire folders with progress tracking
- **💾 Multiple Formats** - PNG, JPEG, TIFF, BMP, GIF, RAW (NEF, CR2, ARW, DNG, etc.)
- **📈 CSV Reports** - Detailed metrics comparing all filters

## 🚀 Quick Start

**Installation takes 5 minutes. No releases yet - run from source:**

#### 1. Install Python

Download and install [Python 3.12](https://www.python.org/downloads/) (or 3.8-3.14)

**Windows:** Make sure to check "Add Python to PATH" during installation

#### 2. Download Project

Click the green "Code" button → Download ZIP → Extract

#### 3. Install Dependencies

**Windows:**
```bash
install_dependencies.bat
```

**Mac/Linux:**
```bash
chmod +x install_dependencies.sh
./install_dependencies.sh
```

**Or manually:**
```bash
pip install -r requirements.txt
```

#### 4. Run the Application

**GUI Mode (Recommended):**
```bash
# Windows
run_gui.bat

# Mac/Linux
chmod +x run_gui.sh
./run_gui.sh

# Or directly
python gui.py
```

**Command Line Mode:**
```bash
# Edit config.ini first, then:
python denoiserBatch.py
```

#### 5. Optional: Install AI Denoising

**In-GUI (Easiest):**
1. Check "Enable AI Denoiser 🤖"
2. Click "Yes" to install (~500MB)
3. Wait 3-5 minutes
4. Restart app

**Or manually:**
```bash
pip install -r requirements-ai.txt
```

---

### Building Standalone Executables (Optional)

Want to create a standalone .exe that doesn't require Python?

See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) for creating executables:
- Windows: `.exe` executable
- macOS: `.app` bundle and `.dmg` installer
- Linux: AppImage and `.deb` package

## 📖 Documentation

### User Guides
- **[USAGE.md](USAGE.md)** - Complete user guide with filter tuning and workflows
- **[QUICKSTART_WINDOWS.md](QUICKSTART_WINDOWS.md)** - 5-minute Windows installation
- **[WINDOWS_INSTALL.md](WINDOWS_INSTALL.md)** - Detailed Windows setup and troubleshooting
- **[AI_DENOISING_GUIDE.md](AI_DENOISING_GUIDE.md)** - AI models, GPU setup, troubleshooting
- **[SELECTIVE_DENOISING.md](SELECTIVE_DENOISING.md)** - Mask editor guide
- **[OUTPUT_SETTINGS_GUIDE.md](OUTPUT_SETTINGS_GUIDE.md)** - Post-processing options

### Installation & Setup
- **[AI_INSTALLATION_OPTIONS.md](AI_INSTALLATION_OPTIONS.md)** - All methods to install AI dependencies
- **[AMD_GPU_SETUP.md](AMD_GPU_SETUP.md)** - AMD GPU acceleration setup (Linux ROCm)
- **[BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)** - Create standalone executables

### Technical Documentation
- **[AI_PADDING_FIX.md](AI_PADDING_FIX.md)** - How auto-padding handles any image dimensions
- **[AI_FALLBACK_FIX.md](AI_FALLBACK_FIX.md)** - Automatic fallback when AI fails
- **[AI_PROGRESS_FEEDBACK.md](AI_PROGRESS_FEEDBACK.md)** - Real-time AI status implementation
- **[CANCEL_BUTTON_FEATURE.md](CANCEL_BUTTON_FEATURE.md)** - Cancellable processing architecture
- **[FEATURE_COMPARISON_WINDOW.md](FEATURE_COMPARISON_WINDOW.md)** - Before/after comparison with zoom
- **[BUGFIX_AI_COMPARISON.md](BUGFIX_AI_COMPARISON.md)** - Comparison window AI file detection fix

### Project Information
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and changes
- **[EVOLUTION_BLOG.md](EVOLUTION_BLOG.md)** - Journey from simple script to full-featured app
- **[LICENSE_INFO.md](LICENSE_INFO.md)** - License details and commercial use

## 🖥️ GUI Preview

The GUI provides:
- Folder/file browser for input selection
- Filter enable/disable with real-time parameter adjustment
- Quick presets for common scenarios
- Live processing log with auto-popup for AI
- Progress tracking with cancel button
- Before/after comparison with interactive slider and zoom
- Mask editor for selective denoising

## 📊 Example Output

The tool generates:
- Denoised images with filter suffix (e.g., `image_nonlocal_ai.png`)
- CSV metrics file with noise reduction stats
- Processing log with quality measurements

### Sample Metrics

| Filename | Gaussian NR | Gaussian PSNR | AI NR | AI PSNR | Non-local NR | Non-local PSNR |
|----------|-------------|---------------|-------|---------|--------------|----------------|
| photo.jpg | 45.23% | 32.15 dB | 58.91% | 36.42 dB | 52.34% | 34.21 dB |

## 🎯 Use Cases

- High ISO photography noise reduction
- Scanned document cleanup
- Low-light image enhancement
- Batch photo processing
- Image quality comparison
- Selective area denoising (faces, subjects)

## 📋 Requirements

**Core Requirements:**
- Python 3.8 - 3.14 (recommended: 3.10, 3.11, 3.12, or 3.13)
- NumPy
- scikit-image
- SciPy

**Optional (for RAW support):**
- rawpy (requires Python 3.8 - 3.13 only)
- Note: Python 3.14+ works for all formats except RAW

**Optional (for AI Denoising):**
- PyTorch (~500MB)
- Install via GUI or `pip install -r requirements-ai.txt`

## 🏗️ Project Structure

```
image-denoiser/
├── gui.py                      # GUI application
├── denoiserBatch.py           # CLI entry point
├── config_loader.py           # Configuration management
├── image_io.py                # Image I/O operations
├── image_filters.py           # Classical filter implementations
├── ai_denoiser.py             # AI denoising (SCUNet/NAFNet)
├── ai_models.py               # AI model architectures
├── color_utils.py             # Color preservation utilities
├── metrics.py                 # Metrics calculation
├── processor.py               # Batch processing logic
├── mask_editor.py             # Selective denoising mask editor
├── tooltip.py                 # GUI tooltip utilities
├── config.ini                 # Configuration file
├── requirements.txt           # Core dependencies
├── requirements-ai.txt        # AI dependencies
├── icon.ico / icon.png        # Application icon
├── run_gui.bat / .sh          # Quick launchers
├── install_dependencies.bat/.sh  # Installers
└── Documentation files (.md)
```

## 📷 RAW Format Support

The tool supports RAW image formats from major camera manufacturers:
- Nikon (.nef)
- Canon (.cr2, .cr3)
- Sony (.arw)
- Adobe (.dng)
- Fujifilm (.raf)
- Olympus (.orf)
- Panasonic (.rw2)

### Python Version Requirements for RAW

**RAW support requires:**
- Python 3.8 - 3.13 (rawpy library limitation)
- Recommended: Python 3.10, 3.11, or 3.12

**Not supported:**
- Python 3.14+ (rawpy not yet available)
- Python 3.7 and below (deprecated)

### Installation

**Automatic (during setup):**
```bash
python install_dependencies.py
# Will attempt to install rawpy automatically
```

**Manual installation:**
```bash
pip install rawpy
```

**If you're on Python 3.14+:**
- RAW support won't be available
- Tool works perfectly with JPEG, PNG, TIFF, BMP, GIF
- Consider using Python 3.12 if you need RAW support

### Processing Modes

- `full` - Full resolution (best quality, slowest)
- `half` - Half resolution (balanced, recommended)
- `preview` - Embedded JPEG (fastest, lower quality)

Configure in `config.ini` under `[RAW]` section or select in GUI.

## 🤖 AI Denoising

### Models

**SCUNet (Recommended):**
- Size: 3MB
- Speed: Fast
- Quality: Excellent
- Download: Reliable

**NAFNet:**
- Size: 9MB
- Speed: Slower
- Quality: Slightly better
- Download: May fail (use SCUNet if issues)

### GPU Support

**NVIDIA (CUDA):**
- Windows/Linux: Full support
- Fastest performance
- Install: `pip install torch --index-url https://download.pytorch.org/whl/cu118`

**Apple Silicon (MPS):**
- Mac M1/M2/M3: Automatic support
- Good performance
- Install: `pip install torch`

**AMD (ROCm):**
- Linux only: Supported
- Moderate performance
- Install: `pip install torch --index-url https://download.pytorch.org/whl/rocm5.7`

**CPU:**
- All platforms: Automatic fallback
- Slower but works everywhere
- No special installation needed

### Features

- **Auto-padding:** Handles any image dimensions (models require divisible by 8)
- **Automatic fallback:** Uses classical filters if AI fails
- **Progress display:** Real-time status with model loading, processing stages
- **Cancellable:** Stop AI processing mid-batch
- **Post-processing:** Apply sharpening, saturation, brightness after AI

## ⚠️ Limitations

- **RAW processing** requires `rawpy` library (optional, Python 3.8-3.13 only)
- **Python 3.14+** users cannot use RAW support (rawpy not yet available)
- **NAFNet download** may fail (use SCUNet instead)
- **AMD GPU** acceleration only on Linux with ROCm
- RAW files take significantly longer to process than standard formats
- Processing time varies with image size and filter settings
- Non-local means and AI filters are computationally intensive

## 📝 Example Usage

### Before and After
Left: After denoising | Right: Before denoising
![Screenshot 2025-02-28 at 8 53 46 PM](https://github.com/user-attachments/assets/8775aef0-abff-4c8a-a0b3-eee30cd0b2c4)

## 👥 Maintainers
- Adwait Godbole
- Siddhesh Pandit

## 📄 License

This project is licensed under the **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)** license.

**You are free to:**
- ✅ Use for personal projects
- ✅ Use for educational purposes
- ✅ Use for research
- ✅ Modify and adapt the code
- ✅ Share with others

**You may NOT:**
- ❌ Use for commercial purposes
- ❌ Sell the software or derivatives
- ❌ Use in commercial products or services

**Requirements:**
- Give appropriate credit to the authors
- Indicate if changes were made
- Provide a link to the license

For commercial use inquiries, please contact the maintainers.

See [LICENSE](LICENSE) file for full details.
