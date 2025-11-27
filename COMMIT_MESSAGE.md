# Add RAW format support and improve error handling

## Major Features

### RAW Image Format Support
- Added support for RAW formats (.nef, .cr2, .cr3, .arw, .dng, .raf, .orf, .rw2)
- Three processing modes: full, half, preview
- Automatic detection and graceful fallback when rawpy unavailable
- Python version compatibility checks (requires 3.8-3.13)
- Auto-skip RAW files on unsupported Python versions (3.14+)

### Flexible Input Selection (GUI)
- Added ability to select individual files or multiple files
- New "Folder" and "Files" buttons for input selection
- Support for single image, multiple images, or entire folder
- File type filters in selection dialog

### Enhanced Error Handling
- Filter-specific error messages with helpful hints
- Graceful degradation - failed filters don't stop processing
- "N/A" metrics for failed filters in CSV output
- Per-filter try-catch blocks
- Summary showing X/Y filters succeeded

## Bug Fixes

### Critical Fixes
- Fixed `nonlocal` reserved keyword issue in config_loader.py, processor.py, gui.py
- Added missing PyWavelets dependency
- Fixed image normalization for uint16 and float images
- Fixed non-local means filter data type handling
- Improved image format conversion for denoising algorithms

### Installation Improvements
- Split requirements into core and optional (requirements-core.txt, requirements-raw.txt)
- Made rawpy optional with automatic fallback
- Added Python version detection in installer
- Python 3.14+ detection with helpful messages
- Enhanced install_dependencies.py with better error handling

### Platform Support
- Added Python availability checks to install_dependencies.bat
- Added Python availability checks to install_dependencies.sh
- Platform-specific installation instructions

## Improvements

### Code Quality
- Better image data type handling across all filters
- Improved normalize_image() function with multiple dtype support
- Enhanced non-local means filter with format conversion
- Better error messages with context-specific hints

### User Experience
- RAW support status displayed in GUI
- Clear messaging when RAW files are skipped
- Progress tracking for filter success/failure
- Improved validation for file/folder selection
- Better logging throughout processing pipeline

### Documentation
- Updated README.md with Python version requirements
- Updated USAGE.md with RAW format details
- Added Python compatibility table
- Enhanced troubleshooting section
- Clear RAW support limitations documented

## Technical Details

### New Files
- `requirements-core.txt` - Core dependencies only
- `requirements-raw.txt` - Optional RAW support
- `COMMIT_MESSAGE.md` - This file

### Modified Files
- `gui.py` - Input selection, RAW status, error handling
- `processor.py` - Filter error handling, file processing method
- `config_loader.py` - RAW config, fixed reserved keyword
- `image_io.py` - RAW loading, auto-skip functionality
- `image_filters.py` - Enhanced non-local means filter
- `metrics.py` - Better image normalization
- `requirements.txt` - Added PyWavelets, commented rawpy
- `install_dependencies.py` - Python version checks, optional rawpy
- `install_dependencies.bat` - Python availability check
- `install_dependencies.sh` - Python availability check
- `README.md` - RAW support documentation
- `USAGE.md` - System requirements, troubleshooting

### Dependencies Added
- PyWavelets>=1.1.1 (required)
- rawpy>=0.18.0 (optional, Python 3.8-3.13 only)

## Breaking Changes
None - fully backward compatible

## Python Version Support
- **3.8-3.13**: Full support including RAW
- **3.14+**: Full support except RAW (rawpy not available yet)
- **3.7 and below**: Not supported

## Testing Notes
- Tested on Python 3.14 (core features work, RAW skipped)
- Tested with various image formats (JPEG, PNG)
- Tested filter failure scenarios
- Tested file and folder selection modes
