# Image Denoiser

A powerful batch image denoising tool with GUI and CLI interfaces. Applies multiple noise reduction filters and provides quality metrics for comparison.

## ✨ Features

- **🖼️ GUI Application** - Easy-to-use graphical interface (no config editing needed)
- **⚡ Three Denoising Filters**:
  - Gaussian Filter - General smoothing
  - Median Filter - Salt-and-pepper noise removal
  - Non-local Means - Advanced edge-preserving denoising
- **📊 Quality Metrics** - PSNR and noise reduction percentage for each filter
- **🎛️ Fully Configurable** - Adjust all filter parameters
- **📁 Batch Processing** - Process entire folders automatically
- **💾 Multiple Formats** - PNG, JPEG, TIFF, BMP, GIF support
- **📈 CSV Reports** - Detailed metrics exported for analysis

## 🚀 Quick Start

### 1. Install Dependencies

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

### 2. Run the Application

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

## 📖 Documentation

See [USAGE.md](USAGE.md) for detailed documentation including:
- Configuration guide
- Filter tuning recommendations
- Example workflows
- Troubleshooting tips

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.

## 🖥️ GUI Preview

The GUI provides:
- Folder browser for input/output selection
- Filter enable/disable checkboxes
- Real-time parameter adjustment
- Live processing log
- Progress tracking

## 📊 Example Output

The tool generates:
- Denoised images with filter suffix (e.g., `image_gaussian.png`)
- CSV metrics file with noise reduction stats
- Processing log with quality measurements

### Sample Metrics

| Filename | Gaussian Noise Reduction | Gaussian PSNR | Median Noise Reduction | Median PSNR | Non-local Noise Reduction | Non-local PSNR |
|----------|-------------------------|---------------|------------------------|-------------|---------------------------|----------------|
| photo.jpg | 45.23% | 32.15 dB | 38.67% | 30.89 dB | 52.34% | 34.21 dB |

## 🎯 Use Cases

- High ISO photography noise reduction
- Scanned document cleanup
- Low-light image enhancement
- Batch photo processing
- Image quality comparison

## 📋 Requirements

- Python 3.7+
- NumPy
- scikit-image
- SciPy

## 🏗️ Project Structure

```
image-denoiser/
├── gui.py                    # GUI application
├── denoiserBatch.py         # CLI entry point
├── config_loader.py         # Configuration management
├── image_io.py              # Image I/O operations
├── image_filters.py         # Filter implementations
├── metrics.py               # Metrics calculation
├── processor.py             # Batch processing logic
├── config.ini               # Configuration file
├── requirements.txt         # Dependencies
└── USAGE.md                 # User guide
```

## ⚠️ Limitations

- RAW formats (.raw, .nef, .cr2) not currently supported
- Processing time varies with image size and filter settings
- Non-local means filter is computationally intensive

## 📝 Example Usage

### Before and After
Left: After denoising | Right: Before denoising
![Screenshot 2025-02-28 at 8 53 46 PM](https://github.com/user-attachments/assets/8775aef0-abff-4c8a-a0b3-eee30cd0b2c4)

## 👥 Maintainers
- Adwait Godbole
- Siddhesh Pandit
