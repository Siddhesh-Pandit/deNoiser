# Image Denoiser - Usage Guide

A batch image denoising tool that applies multiple noise reduction filters and provides quality metrics.

## System Requirements

**Python Version:**
- Python 3.8 - 3.13 (recommended: 3.10, 3.11, or 3.12)
- Python 3.14+ will work but **without RAW format support**

**Dependencies:**
- NumPy, scikit-image, SciPy (required)
- rawpy (optional, for RAW formats - requires Python 3.8-3.13)

## Quick Start

### Option 1: GUI Mode (Recommended for Beginners)

1. **Install dependencies:**
   ```bash
   # Windows
   install_dependencies.bat
   
   # Mac/Linux
   chmod +x install_dependencies.sh
   ./install_dependencies.sh
   ```

2. **Run the GUI:**
   ```bash
   # Windows
   run_gui.bat
   
   # Mac/Linux
   chmod +x run_gui.sh
   ./run_gui.sh
   
   # Or directly
   python gui.py
   ```

3. **Use the interface:**
   - Click "Browse..." to select input and output folders
   - Choose which filters to enable (or use Quick Presets)
   - Adjust filter parameters if needed
   - Click "Start Processing"
   - After processing, click "🔍 View Comparison" button to see before/after results

### Option 2: Command Line Mode (Advanced)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure paths in `config.ini`:**
   ```ini
   [Paths]
   input_file_path = /path/to/your/noisy/images
   output_file_path = /path/to/output/folder
   ```

3. **Run the script:**
   ```bash
   python denoiserBatch.py
   ```

## How It Works

The tool processes all images in your input folder and applies three different denoising filters:

- **Gaussian Filter** - Fast smoothing, may blur details. Good for quick processing.
- **Median Filter** - Excellent for salt-and-pepper noise and digital artifacts.
- **Non-local Means ⭐** - **Best quality** - Preserves edges, textures, and fine details. Recommended for most photos.

Each filter creates a separate output file with metrics showing noise reduction percentage and PSNR (Peak Signal-to-Noise Ratio).

### 💡 Quick Tip
For best results, **enable only Non-local Means** with sharpening. This gives the highest quality output while being faster than processing all three filters.

## Key Features

### Quick Presets

The GUI includes one-click presets that instantly configure optimal settings:

- **📷 Photos** - Best for portraits, landscapes, general photos (Non-local Means only)
- **📄 Documents** - Best for scanned documents and text (Median filter only)
- **🌙 Low-Light** - Best for night photos and high ISO images (aggressive Non-local Means)
- **🔍 Compare All** - Enable all filters to see which works best for your image

### Interactive Before/After Comparison

After processing images, click the **"🔍 View Comparison"** button to open an interactive comparison window:

- **Always available** - Button appears after any successful processing
- **Draggable slider** - Smoothly reveal the processed image over the original
- **Real-time comparison** - See exactly what changed
- **Easy evaluation** - Quickly judge if the denoising worked well

This feature helps you evaluate results and decide which filter settings work best for your images. The comparison shows the first processed image with the first available filter output.

### Color Preservation Mode (Recommended)

The tool includes an intelligent color preservation mode that denoises only the luminance (brightness) channel while keeping your colors vibrant and saturated.

**How it works:**
- Converts image to LAB color space
- Denoises only the L (lightness) channel
- Preserves A (green-red) and B (blue-yellow) channels
- Converts back to RGB

**Benefits:**
- ✅ Maintains original saturation
- ✅ Preserves color vibrancy and hue
- ✅ Keeps contrast intact
- ✅ Removes only luminance noise
- ✅ Perfect for colorful photos

**When to use:**
- **Enable (default):** For photos with vibrant colors, portraits, landscapes
- **Disable:** For grayscale images or when you want traditional full-color denoising

Configure in `config.ini` under `[Output]` section or toggle in GUI.

## Configuration

### Output Settings

```ini
[Output]
# Output format: png (lossless), tiff (lossless), jpg (lossy)
format = png

# JPEG quality (1-100, only used if format=jpg)
jpeg_quality = 95

# Preserve original format instead of using format setting
preserve_original_format = false

# Preserve color: denoise only luminance, keeping saturation/hue intact
preserve_color = true
```

**Recommendations:**
- Use `png` for best quality (default)
- Use `jpg` with quality 90-95 for smaller file sizes
- Set `preserve_original_format = true` to keep original extensions
- Keep `preserve_color = true` to maintain vibrant colors (recommended)

### Filter Control

```ini
[Filters]
# Enable/disable individual filters
enable_gaussian = true
enable_median = true
enable_nonlocal = true
```

Disable filters you don't need to speed up processing.

### Gaussian Filter

```ini
[GaussianFilter]
# Sigma value (0.5-2.0, higher = more smoothing)
sigma = 0.75
```

**Tuning guide:**
- `0.5` - Light smoothing, preserves detail
- `0.75` - Balanced (default)
- `1.0-2.0` - Heavy smoothing, may blur details

### Median Filter

```ini
[MedianFilter]
# Filter size (3, 5, 7, etc. - must be odd number)
size = 3
```

**Tuning guide:**
- `3` - Good for light salt-and-pepper noise (default)
- `5` - Moderate noise
- `7+` - Heavy noise (may blur edges)

### Non-local Means Filter

```ini
[NonLocalMeans]
# h_multiplier (0.6-1.5, higher = more denoising but may blur)
h_multiplier = 0.8

# fast_mode (true/false, true is faster but slightly lower quality)
fast_mode = true

# patch_size (3, 5, 7 - size of patches for comparison)
patch_size = 5

# patch_distance (5-13 - search area for similar patches)
patch_distance = 11
```

**Tuning guide:**
- **Light noise (preserve detail):** h_multiplier=0.6-0.8, patch_size=3, patch_distance=11
- **Moderate noise (balanced):** h_multiplier=0.8-1.0, patch_size=5, patch_distance=11 (default)
- **Heavy noise (aggressive):** h_multiplier=1.2-1.5, patch_size=7, patch_distance=13
- Set `fast_mode=false` for highest quality (slower)

**Important:** Lower h_multiplier values preserve sharpness better. Start low and increase only if noise remains.

## Output Files

### Processed Images

For each input image, the tool creates:
- `filename_gaussian.png` - Gaussian filtered version
- `filename_median.png` - Median filtered version
- `filename_nonlocal.png` - Non-local means filtered version

### Metrics CSV

A timestamped CSV file (e.g., `denoising_metrics_20251127_143022.csv`) containing:

| Column | Description |
|--------|-------------|
| filename | Original image name |
| gaussian_noise_reduction | % noise removed by Gaussian filter |
| gaussian_psnr | Quality metric (higher is better) |
| median_noise_reduction | % noise removed by Median filter |
| median_psnr | Quality metric (higher is better) |
| nonlocal_noise_reduction | % noise removed by Non-local means |
| nonlocal_psnr | Quality metric (higher is better) |

**Understanding metrics:**
- **Noise reduction %**: Higher means more noise removed (but may lose detail)
- **PSNR (dB)**: Higher means better quality preservation
  - 30-35 dB: Good quality
  - 35-40 dB: Very good quality
  - 40+ dB: Excellent quality

## Supported Image Formats

**Standard Formats (always supported):**
- JPEG (.jpg, .jpeg)
- PNG (.png)
- TIFF (.tiff, .tif)
- BMP (.bmp)
- GIF (.gif)

**RAW Formats (requires rawpy + Python 3.8-3.13):**
- Nikon (.nef)
- Canon (.cr2, .cr3)
- Sony (.arw)
- Adobe (.dng)
- Fujifilm (.raf)
- Olympus (.orf)
- Panasonic (.rw2)

All formats are case-insensitive (e.g., .JPG, .Jpg, .jpg all work).

### RAW Format Notes

**If you have Python 3.8-3.13:**
- RAW support will be installed automatically
- Configure processing mode in `[RAW]` section of config.ini

**If you have Python 3.14+:**
- RAW formats are not supported (rawpy not available yet)
- All standard formats work perfectly
- Consider using Python 3.12 if you need RAW support

## Example Workflow

### 1. Light Noise (High ISO photos)
```ini
[Output]
preserve_color = true

[GaussianFilter]
sigma = 0.5

[NonLocalMeans]
h_multiplier = 0.9
patch_size = 3
```

### 2. Moderate Noise (Scanned documents)
```ini
[Output]
preserve_color = true

[GaussianFilter]
sigma = 0.75

[MedianFilter]
size = 3

[NonLocalMeans]
h_multiplier = 0.9
patch_size = 5
patch_distance = 11
```

### 3. Heavy Noise (Low-light photos)
```ini
[Output]
preserve_color = true

[GaussianFilter]
sigma = 1.0

[MedianFilter]
size = 5

[NonLocalMeans]
h_multiplier = 1.3
patch_size = 7
patch_distance = 9
fast_mode = false
```

### 4. Grayscale Images
```ini
[Output]
preserve_color = false  # Disable for grayscale

[GaussianFilter]
sigma = 0.75

[NonLocalMeans]
h_multiplier = 1.15
```

### 5. Vibrant Color Photos (Portraits, Landscapes)
```ini
[Output]
preserve_color = true  # Essential for color photos

[GaussianFilter]
sigma = 0.75

[NonLocalMeans]
h_multiplier = 0.7  # Lower to preserve detail
patch_size = 5
patch_distance = 11
```

## Tips & Best Practices

1. **Start with defaults** - The default settings work well for most images
2. **Use color preservation** - Keep it enabled for vibrant, natural-looking results
3. **Compare results** - Check all three filtered versions to see which works best
4. **Use metrics** - Higher PSNR usually means better quality
5. **Batch test** - Try different settings on a few images before processing hundreds
6. **Keep originals** - The tool never modifies your original images
7. **PNG for quality** - Use PNG output for archival or further editing
8. **Disable unused filters** - Speed up processing by disabling filters you don't need
9. **Color preservation for portraits** - Essential for maintaining skin tones
10. **Disable for grayscale** - Turn off color preservation for black & white images

## Troubleshooting

**"config.ini file not found"**
- Make sure config.ini is in the same folder as denoiserBatch.py

**"Input folder does not exist"**
- Check the path in config.ini uses forward slashes or escaped backslashes
- Use absolute paths for clarity

**"No images found"**
- Verify your input folder contains supported image formats
- Check file extensions are correct

**"rawpy is not installed" or RAW files skipped**
- Check your Python version: `python --version`
- If Python 3.14+: RAW support not available, use Python 3.8-3.13
- If Python 3.8-3.13: Install rawpy manually: `pip install rawpy`
- Tool works fine without RAW support for standard formats

**"Could not find a version that satisfies the requirement rawpy"**
- You're likely on Python 3.14+ or 3.7-
- RAW support requires Python 3.8-3.13
- Options:
  1. Use standard formats (JPEG, PNG, etc.) - works perfectly
  2. Install Python 3.12 for RAW support
  3. Wait for rawpy to support your Python version

**Processing is slow**
- Disable filters you don't need
- Set `fast_mode = true` for Non-local means
- Reduce `patch_distance` and `patch_size` for Non-local means
- For RAW files, use `processing_mode = half` or `preview`
- Process fewer images at once

**Output images look blurry**
- Reduce sigma for Gaussian filter
- Reduce h_multiplier for Non-local means
- Use smaller median filter size
- Ensure color preservation is enabled

**Not enough noise removed**
- Increase sigma for Gaussian filter
- Increase h_multiplier for Non-local means
- Use larger median filter size

**Colors look washed out or desaturated**
- Enable color preservation mode (`preserve_color = true`)
- This is the default setting - check if it was accidentally disabled
- Color preservation maintains original saturation and vibrancy

**Grayscale images not processing well**
- Disable color preservation for grayscale images
- Color preservation is designed for RGB images

## Module Structure

The tool is organized into focused modules:

- `denoiserBatch.py` - Main entry point
- `config_loader.py` - Configuration management
- `image_io.py` - Image loading/saving (includes RAW support)
- `image_filters.py` - Filter implementations
- `color_utils.py` - Color preservation utilities (LAB color space)
- `metrics.py` - Metrics calculation
- `processor.py` - Batch processing logic
- `gui.py` - Graphical user interface

## Python Version Compatibility

| Python Version | Core Features | RAW Support |
|---------------|---------------|-------------|
| 3.7 and below | ❌ Not supported | ❌ |
| 3.8 - 3.13 | ✅ Full support | ✅ Available |
| 3.14+ | ✅ Full support | ❌ Not yet available |

**Recommended:** Python 3.10, 3.11, or 3.12 for full feature support.

## License & Credits

Uses scikit-image for image processing algorithms.
RAW support powered by rawpy (LibRaw wrapper).
