# README.md Update Needed

## Current Issues in README.md:

1. **Typos**:
   - "? Qualityr Metrics" → should be "📊 Quality Metrics"
   - "? BSatch Processing" → should be "📦 Batch Processing"

2. **Missing Features** (added since README was written):
   - AI Denoiser (SCUNet/NAFNet)
   - GPU acceleration support
   - Selective denoising with mask editor
   - Magic wand tool
   - Gradient auto-select
   - Undo/redo in mask editor
   - Post-processing (sharpening, saturation, brightness)
   - Separate log window
   - Zoom in comparison window
   - RAW file support details

## Suggested README.md Features Section:

```markdown
## ✨ Features

### Core Features
- **🖼️ GUI Application** - Easy-to-use graphical interface (no config editing needed)
- **🎯 Quick Presets** - One-click optimization for Photos, Documents, Low-Light, or Compare All
- **🔍 Before/After Comparison** - Interactive slider with zoom to compare original vs processed
- **📊 Quality Metrics** - PSNR and noise reduction percentage for each filter
- **🎛️ Fully Configurable** - Adjust all filter parameters in real-time
- **📦 Batch Processing** - Process entire folders automatically
- **💾 Multiple Formats** - PNG, JPEG, TIFF, BMP, GIF, and RAW support
- **📈 CSV Reports** - Detailed metrics exported for analysis

### Denoising Methods
- **🤖 AI Denoiser (Optional)** - Neural network-based denoising for best quality
  - SCUNet: Fast, lightweight (3MB model)
  - NAFNet: Better quality (9MB model)
  - GPU acceleration (NVIDIA/AMD/Apple Silicon) or CPU
  - One-click installation in GUI
- **⚡ Classical Filters**:
  - Gaussian Filter - Fast smoothing
  - Median Filter - Salt-and-pepper noise removal
  - Non-local Means ⭐ - Best classical method - Preserves edges and details

### Advanced Features
- **🎨 Selective Denoising** - Paint masks to denoise only specific areas
  - Interactive mask editor with brush, eraser, magic wand
  - Auto-select gradients/edges
  - Undo/redo support
  - Works with both AI and classical methods
- **✨ Post-Processing**:
  - Sharpening to restore structure
  - Saturation boost for vivid colors
  - Brightness adjustment
  - Color preservation mode
- **📋 Processing Logs** - View in separate window, copy, or save to file
- **🔄 RAW Support** - Process camera RAW files (NEF, CR2, ARW, DNG, etc.)
```

## Installation Steps - Status: ✅ GOOD

The installation steps in README.md are still accurate:
1. Install Python ✅
2. Download project ✅
3. Install dependencies ✅
4. Run the application ✅

Optional AI installation is covered in QUICKSTART_WINDOWS.md and AI_DENOISING_GUIDE.md

## Other Documentation Status:

✅ **QUICKSTART_WINDOWS.md** - Up to date, mentions AI
✅ **AI_DENOISING_GUIDE.md** - Complete guide for AI features
✅ **AI_INSTALLATION_OPTIONS.md** - All installation methods
✅ **AMD_GPU_SETUP.md** - Explains AMD GPU limitations
✅ **SELECTIVE_DENOISING.md** - Mask editor documentation

⚠️ **README.md** - Needs feature list update and typo fixes
⚠️ **USAGE.md** - May need AI and mask editor sections

## Recommendation:

Manually edit README.md to:
1. Fix typos in features list
2. Add new features section as shown above
3. Keep installation steps as-is (they're correct)
