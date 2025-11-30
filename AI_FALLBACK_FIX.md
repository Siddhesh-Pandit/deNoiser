# AI Fallback & Comparison Window Fix

## Problem Discovered

When AI processing fails (e.g., due to incompatible image dimensions), the system correctly falls back to classical filters, but:

1. **Poor error visibility** - Error message was buried in logs
2. **Comparison window broken** - Only looked for `_ai` files, not classical fallback files
3. **Confusing for users** - No clear indication that AI failed and classical was used

### The Specific Error
```
RuntimeError: Sizes of tensors must match except in dimension 1. 
Expected size 1634 but got size 1633 for tensor number 1 in the list.
```

This happens when image dimensions aren't compatible with the AI model (models require dimensions divisible by 8).

## Solutions Implemented

### 1. Better Error Messages

**Before:**
```
ERROR - AI denoising failed: [technical error]
INFO - Falling back to classical filters
```

**After:**
```
✗ AI denoising failed: [technical error]
⚠ Falling back to classical filters
ℹ Tip: AI models require images with dimensions divisible by 8
```

Plus the AI status label shows: `⚠ AI failed, using classical filters`

### 2. Comparison Window Fallback

**Before:**
- AI enabled → Look for `image_nonlocal_ai.png`
- Not found → Error

**After:**
- AI enabled → Look for `image_nonlocal_ai.png`
- Not found → Look for `image_nonlocal.png` (fallback)
- Not found → Error

**Priority order when AI is enabled:**
1. `nonlocal_ai` (AI succeeded)
2. `gaussian_ai` (if Gaussian enabled)
3. `median_ai` (if Median enabled)
4. `nonlocal` (AI failed, fell back to classical)
5. `gaussian` (AI failed, fell back to classical)
6. `median` (AI failed, fell back to classical)

### 3. Visual Feedback

The AI status label now shows:
- `🤖 AI: Loading model...` - Model loading
- `🤖 AI: Processing...` - AI processing
- `✓ AI denoising complete` - Success
- `⚠ AI failed, using classical filters` - Failure with fallback
- `⚠ AI not available, using classical filters` - PyTorch not installed

### 4. Auto-Open Log Window

When AI processing starts, the log window automatically opens so users can see detailed progress and any errors.

### 5. Console Logging

Running `run_gui_debug.bat` now shows all logs in the console window for debugging.

## Why AI Failed in This Case

The error "Sizes of tensors must match except in dimension 1" occurs when:
- Image dimensions aren't divisible by 8
- Image has odd dimensions that don't align with model's architecture

**Example:**
- Image: 1633 × 1634 pixels
- Model expects: Dimensions divisible by 8
- Solution: Resize image or use classical filters

## User Experience Improvements

### Before:
1. User enables AI
2. Clicks "Start Processing"
3. Sees "✓ AI denoising complete" (misleading - it actually failed)
4. File created: `image_nonlocal.png` (no `_ai`)
5. Clicks "View Comparison"
6. Error: "Could not find processed image"
7. User confused: "Where's my file? Did it work?"

### After:
1. User enables AI
2. Clicks "Start Processing"
3. Log window opens automatically
4. Sees "⚠ AI failed, using classical filters" in status label
5. Log shows: "✗ AI denoising failed: [error]"
6. Log shows: "⚠ Falling back to classical filters"
7. Log shows: "Tip: AI models require images with dimensions divisible by 8"
8. File created: `image_nonlocal.png`
9. Clicks "View Comparison"
10. **Works!** Shows classical filter result
11. User understands: "AI didn't work, but I still got a result"

## Testing

### Test 1: AI Success
1. Enable AI
2. Process image with dimensions divisible by 8
3. **Expected:** File `image_nonlocal_ai.png` created
4. **Expected:** Comparison window works

### Test 2: AI Failure (Dimension Mismatch)
1. Enable AI
2. Process image with odd dimensions (like 1633×1634)
3. **Expected:** See "⚠ AI failed, using classical filters"
4. **Expected:** File `image_nonlocal.png` created (no `_ai`)
5. **Expected:** Comparison window still works (finds classical output)

### Test 3: AI Not Installed
1. Uninstall PyTorch
2. Enable AI checkbox
3. Process image
4. **Expected:** See "⚠ AI not available, using classical filters"
5. **Expected:** File `image_nonlocal.png` created
6. **Expected:** Comparison window works

### Test 4: Double Extension Filename
1. Process file named `D85_5014.NEF.jpg` (JPEG with NEF in name)
2. **Expected:** Output `D85_5014.NEF_nonlocal.png` (keeps NEF in name)
3. **Expected:** Comparison window finds it correctly

## Files Modified

1. **processor.py**
   - Better error messages with icons (✗, ⚠, ℹ)
   - AI status callback on failure
   - Helpful tip about dimension requirements

2. **gui.py**
   - Comparison window checks both AI and classical outputs
   - Auto-open log window when AI processing starts
   - Console logging enabled for debug mode

3. **run_gui_debug.bat**
   - Improved console output
   - Shows all logs in real-time

## Known Limitations

### AI Model Dimension Requirements
- SCUNet and NAFNet require image dimensions divisible by 8
- Images with odd dimensions will fail
- **Workaround:** Resize image before processing, or use classical filters

### Future Improvements
1. **Auto-resize** - Automatically pad/resize images to compatible dimensions
2. **Dimension check** - Warn user before processing if dimensions incompatible
3. **Better error recovery** - Try to fix dimension issues automatically
4. **Model info** - Show model requirements in tooltip
