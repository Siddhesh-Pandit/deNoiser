# Release v2.0.0 - Major Refactor & GUI Addition

## 🎉 What's New

### Graphical User Interface
We've added a complete GUI application that makes image denoising accessible to everyone! No more editing config files - just click, select, and process.

**Features:**
- 📁 Browse buttons for easy folder selection
- ✅ Checkboxes to enable/disable filters
- 🎛️ Sliders and spinboxes for all parameters
- 📊 Real-time processing log
- 💬 Success/error notifications

**Launch it:**
- Windows: Double-click `run_gui.bat`
- Mac/Linux: Run `./run_gui.sh`
- Or: `python gui.py`

### Automated Installation
No more manual pip commands! We've added installation scripts for all platforms:
- `install_dependencies.bat` (Windows)
- `install_dependencies.sh` (Mac/Linux)
- `install_dependencies.py` (Cross-platform)

Just run the script and you're ready to go!

### Quality Metrics & Reporting
Now you can see exactly how well each filter performs:
- **Noise reduction percentage** - How much noise was removed
- **PSNR measurements** - Quality preservation metrics
- **CSV export** - Timestamped reports for all processed images
- **Real-time display** - See metrics as images are processed

### Complete Code Refactor
The codebase has been completely restructured for better maintainability:
- **Modular architecture** - 7 focused modules instead of one monolithic script
- **40-line main file** - Clean entry point
- **Type-safe config** - Using dataclasses
- **Better separation** - Each module has a single responsibility
- **Easier to extend** - Add new filters or features easily

### Enhanced Configuration
Everything is now configurable through `config.ini`:
- Output format (PNG, JPEG, TIFF)
- JPEG quality control
- Individual filter toggles
- All filter parameters exposed
- Sensible defaults for everything

## 🔧 Improvements

### Image Processing
- ✅ PNG output by default (lossless quality)
- ✅ Configurable JPEG quality (1-100)
- ✅ Support for TIFF format
- ✅ Case-insensitive file extensions
- ✅ Better error handling (one failure doesn't stop the batch)

### User Experience
- ✅ Progress tracking ([X/Total] format)
- ✅ Detailed logging with timestamps
- ✅ Filter parameters shown in output
- ✅ Better error messages
- ✅ Memory efficient (processes one image at a time)

### Code Quality
- ✅ Removed duplicate imports
- ✅ Removed unused dependencies (matplotlib)
- ✅ Fixed incorrect parameter usage
- ✅ Improved memory efficiency
- ✅ Better code organization

## 📚 Documentation

- **USAGE.md** - Comprehensive guide with examples and troubleshooting
- **CHANGELOG.md** - Detailed version history
- **Updated README.md** - Quick start and feature overview

## 🚀 Getting Started

1. **Install dependencies:**
   ```bash
   # Windows
   install_dependencies.bat
   
   # Mac/Linux
   ./install_dependencies.sh
   ```

2. **Run the GUI:**
   ```bash
   # Windows
   run_gui.bat
   
   # Mac/Linux
   ./run_gui.sh
   ```

3. **Or use CLI:**
   ```bash
   # Edit config.ini, then:
   python denoiserBatch.py
   ```

## 📦 What's Included

- `gui.py` - New GUI application
- `denoiserBatch.py` - Refactored CLI (40 lines!)
- `config_loader.py` - Configuration management
- `image_io.py` - Image operations
- `image_filters.py` - Filter implementations
- `metrics.py` - Metrics & CSV export
- `processor.py` - Batch processing
- `install_dependencies.*` - Installation scripts
- `run_gui.*` - GUI launchers
- `requirements.txt` - Dependencies
- `USAGE.md` - User guide
- `CHANGELOG.md` - Version history

## 🎯 Use Cases

Perfect for:
- 📸 High ISO photography cleanup
- 📄 Scanned document enhancement
- 🌙 Low-light image improvement
- 🗂️ Batch photo processing
- 📊 Filter comparison and analysis

## ⚡ Performance Tips

- Disable unused filters to speed up processing
- Use `fast_mode = true` for non-local means
- Process smaller batches for faster feedback
- PNG for quality, JPEG for speed/size

## 🐛 Bug Fixes

- Fixed duplicate imports
- Removed incorrect DPI parameter usage
- Fixed case-sensitive extension matching
- Improved memory usage
- Better error handling

## 💡 Breaking Changes

None! The tool is backward compatible. Your old `config.ini` will work with sensible defaults for new settings.

## 🙏 Feedback

Try it out and let us know what you think! Open an issue for bugs or feature requests.

---

**Full Changelog**: See [CHANGELOG.md](CHANGELOG.md) for complete details
