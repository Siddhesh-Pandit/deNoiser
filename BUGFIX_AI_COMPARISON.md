# Bug Fix: AI Comparison Window Not Working

## The Problem

When using AI denoising with all classical filters disabled + output settings enabled:
- **Expected:** File `image_nonlocal_ai.png` created, comparison window works
- **Actual:** No `_ai.png` file created, comparison window fails

## Root Cause

There were TWO bugs:

### Bug 1: Missing AI-only logic in folder processing
**Location:** `processor.py` - `_process_single_image()` method

**Issue:** When processing a folder (Browse Folder button), the code only ran AI if Non-local Means filter was enabled:
```python
# OLD CODE (BROKEN)
if self.config.filters.enable_nonlocal:
    # Process with AI...
```

But when processing files (Browse Files button), it correctly handled AI-only mode:
```python
# CORRECT CODE
if self.config.filters.enable_nonlocal or (self.config.ai_denoiser.enable_ai and not any([
    self.config.filters.enable_gaussian,
    self.config.filters.enable_median
])):
    # Process with AI...
```

**Result:** AI-only mode worked for file selection but NOT for folder selection.

### Bug 2: Comparison window didn't check for all AI file variants
**Location:** `gui.py` - `show_comparison_window()` method

**Issue:** The comparison window only looked for `nonlocal_ai` files, but when AI is enabled with Gaussian or Median filters, it creates `gaussian_ai` or `median_ai` files instead.

**Old logic:**
```python
if self.enable_ai.get():
    filter_suffixes.append('nonlocal_ai')  # Only checks this!
```

**New logic:**
```python
if self.enable_ai.get():
    # Check for AI variants of each enabled filter
    if self.enable_nonlocal.get():
        filter_suffixes.append('nonlocal_ai')
    if self.enable_gaussian.get():
        filter_suffixes.append('gaussian_ai')
    if self.enable_median.get():
        filter_suffixes.append('median_ai')
    # If no classical filters, AI still runs
    if not any([...]):
        filter_suffixes.append('nonlocal_ai')
```

## The Fix

### Fix 1: Unified AI-only logic
Updated `_process_single_image()` to match `process_files()` logic:
- Now checks if AI is enabled AND no classical filters are enabled
- Runs AI denoising even when all classical filters are disabled
- Works for both folder and file selection

### Fix 2: Comprehensive file suffix checking
Updated comparison window to check for all possible AI file variants:
- `nonlocal_ai` (AI + Non-local Means OR AI-only)
- `gaussian_ai` (AI + Gaussian)
- `median_ai` (AI + Median)

## How AI Mode Works

### When AI is Enabled:
AI **REPLACES** the classical filter for each enabled filter:

| Classical Filters Enabled | Files Created |
|---------------------------|---------------|
| None | `image_nonlocal_ai.png` |
| Gaussian only | `image_gaussian_ai.png` |
| Median only | `image_median_ai.png` |
| Non-local only | `image_nonlocal_ai.png` |
| Gaussian + Median | `image_gaussian_ai.png` + `image_median_ai.png` |
| All three | `image_gaussian_ai.png` + `image_median_ai.png` + `image_nonlocal_ai.png` |

### Output Settings with AI:
All output settings (sharpening, saturation, brightness) are applied AFTER AI denoising:
```
AI Denoising → Mask → Sharpening → Saturation → Brightness → Save
```

The filename doesn't change based on output settings - they're baked into the saved file.

## Testing

To verify the fix works:

### Test 1: AI-only mode (folder)
1. Select a folder with images
2. Enable AI denoising
3. Disable all classical filters (Gaussian, Median, Non-local)
4. Enable output settings (sharpening, saturation, etc.)
5. Process
6. **Expected:** `image_nonlocal_ai.png` created
7. Click "View Comparison"
8. **Expected:** Comparison window opens

### Test 2: AI-only mode (files)
Same as Test 1 but use "Browse Files" instead of "Browse Folder"

### Test 3: AI + Gaussian
1. Enable AI + Gaussian only
2. Process
3. **Expected:** `image_gaussian_ai.png` created
4. **Expected:** Comparison window shows this file

### Test 4: AI + Multiple filters
1. Enable AI + Gaussian + Median
2. Process
3. **Expected:** Both `image_gaussian_ai.png` and `image_median_ai.png` created
4. **Expected:** Comparison window shows gaussian_ai (first priority)

## Files Modified

1. **processor.py**
   - Fixed `_process_single_image()` to handle AI-only mode
   - Now matches `process_files()` logic

2. **gui.py**
   - Fixed `show_comparison_window()` to check all AI file variants
   - Properly handles AI + classical filter combinations

3. **FEATURE_COMPARISON_WINDOW.md**
   - Updated documentation to reflect actual behavior
   - Added troubleshooting for AI mode
