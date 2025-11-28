# Settings Logging Feature

## Overview

Every time you click "Start Processing", the app now logs ALL current settings before processing begins. This makes it easy to verify what settings are being applied and track changes across successive runs.

## Example Log Output

### First Run (Default Settings)

```
============================================================
PROCESSING SETTINGS:
============================================================
Output format: PNG
Preserve color: ON
Apply sharpening: OFF
Enabled filters: Non-local (h=0.85×σ, patch=3, distance=3, fast=ON)
RAW support: Disabled (Python 3.12)
  Install with: pip install rawpy
============================================================
[1/1] Processing: photo.jpg
  ✓ Non-local means: 52.34% noise reduction, PSNR: 34.21 dB [color-preserving]
```

### Second Run (Changed Settings)

```
============================================================
PROCESSING SETTINGS:
============================================================
Output format: PNG
Preserve color: OFF
Apply sharpening: ON
  • Sharpen amount: 1.5
  • Sharpen radius: 2.0
Enabled filters: Non-local (h=1.2×σ, patch=5, distance=5, fast=ON)
RAW support: Disabled (Python 3.12)
  Install with: pip install rawpy
============================================================
[1/1] Processing: photo.jpg
  ✓ Non-local means: 58.12% noise reduction, PSNR: 32.89 dB
  ✓ Applied sharpening (amount=1.5, radius=2.0)
```

## What Gets Logged

### Output Settings
- **Format:** PNG, JPG, or TIFF
- **JPEG Quality:** (if format is JPG)
- **Preserve Color:** ON or OFF
- **Apply Sharpening:** ON or OFF
  - Sharpen Amount (if enabled)
  - Sharpen Radius (if enabled)

### Filter Settings
Shows only enabled filters with their parameters:

**Gaussian:**
- Sigma value

**Median:**
- Filter size

**Non-local Means:**
- h multiplier
- Patch size
- Patch distance
- Fast mode (ON/OFF)

### RAW Support
- Enabled/Disabled status
- Processing mode (if enabled)
- Python version info (if disabled)

## Benefits

### 1. Verify Settings Are Applied
You can see exactly what settings are being used for each run.

### 2. Track Changes Across Runs
Compare the settings section between runs to see what changed:

```
Run 1: Sharpen amount: 1.0
Run 2: Sharpen amount: 2.0  ← Changed!
```

### 3. Troubleshooting
If results don't look right, check the log to confirm settings:
- Is "Preserve color" ON when you expected it?
- Is sharpening enabled?
- Are the filter parameters correct?

### 4. Documentation
The log serves as a record of what settings produced which results.

## Example Scenarios

### Scenario 1: Testing Sharpening Strength

**Run 1:**
```
Apply sharpening: ON
  • Sharpen amount: 0.5
  • Sharpen radius: 1.0
```

**Run 2:**
```
Apply sharpening: ON
  • Sharpen amount: 1.5  ← Increased
  • Sharpen radius: 1.0
```

**Run 3:**
```
Apply sharpening: ON
  • Sharpen amount: 2.0  ← Increased again
  • Sharpen radius: 1.0
```

You can clearly see the progression and compare outputs.

### Scenario 2: Comparing Preserve Color

**Run 1:**
```
Preserve color: ON
[Processing...]
  ✓ Non-local means: ... [color-preserving]  ← Note the tag
```

**Run 2:**
```
Preserve color: OFF  ← Changed
[Processing...]
  ✓ Non-local means: ...  ← No [color-preserving] tag
```

### Scenario 3: Filter Comparison

**Run 1:**
```
Enabled filters: Non-local (h=0.85×σ, patch=3, distance=3, fast=ON)
```

**Run 2:**
```
Enabled filters: Gaussian (σ=0.75), Median (size=3), Non-local (h=0.85×σ, patch=3, distance=3, fast=ON)
```

You can see all three filters are now enabled.

## Log Location

The settings are logged to:
1. **GUI Log Window** - Visible at the bottom of the application
2. **Console** - If running from command line
3. **Log File** - If logging to file is configured

## Reading the Log

### Settings Section
```
============================================================
PROCESSING SETTINGS:
============================================================
[All settings listed here]
============================================================
```

The settings section is clearly marked with separator lines.

### Per-Image Processing
After the settings, you'll see processing for each image:
```
[1/3] Processing: image1.jpg
  ✓ Gaussian: ...
  ✓ Median: ...
  ✓ Non-local means: ...
```

### Summary
At the end:
```
📊 Metrics saved to: denoising_metrics_20251127_143022.csv
✓ Successfully processed 3 images
```

## Tips

1. **Scroll to top** of log to see settings for current run
2. **Compare settings** between runs by looking at previous log entries
3. **Look for tags** like `[color-preserving]` to confirm settings
4. **Check filter parameters** match what you set in the GUI
5. **Save log** (copy/paste) if you want to document your workflow

## Technical Details

The settings are logged by the `_log_settings()` method in `processor.py`, which is called at the start of both:
- `process_files()` - When processing selected files
- `process_batch()` - When processing a folder

This ensures consistent logging regardless of how you select images.
