# Settings Persistence Test

## How to Verify Settings Are Applied

### Test 1: Preserve Color Toggle

1. **First Run:**
   - Select an image
   - Enable "Preserve Color" (default: ON)
   - Process with Non-local Means
   - Note the output

2. **Second Run:**
   - **Uncheck "Preserve Color"**
   - Process the same image again
   - Compare outputs

**Expected Result:**
- First run: Colors should be vibrant (luminance-only denoising)
- Second run: Colors may be slightly desaturated (full RGB denoising)
- Log should show: `[color-preserving]` in first run, not in second

### Test 2: Sharpening Parameters

1. **First Run:**
   - Enable "Apply Sharpening"
   - Set Sharpen Amount: 1.0
   - Set Sharpen Radius: 1.0
   - Process image

2. **Second Run:**
   - Keep "Apply Sharpening" enabled
   - Change Sharpen Amount: 2.0
   - Change Sharpen Radius: 2.5
   - Process same image again

**Expected Result:**
- First run: Subtle sharpening
- Second run: Much stronger sharpening (more pronounced edges)
- Outputs should be visibly different

### Test 3: Filter Parameters

1. **First Run:**
   - Enable Non-local Means
   - Set h multiplier: 0.6 (preserve detail)
   - Process image

2. **Second Run:**
   - Keep Non-local Means enabled
   - Change h multiplier: 1.5 (aggressive denoising)
   - Process same image again

**Expected Result:**
- First run: More detail preserved, some noise may remain
- Second run: Smoother result, more noise removed
- Outputs should be clearly different

### Test 4: Multiple Settings at Once

1. **First Run:**
   - Preserve Color: ON
   - Apply Sharpening: OFF
   - Non-local h: 0.85
   - Process image

2. **Second Run:**
   - Preserve Color: OFF
   - Apply Sharpening: ON (Amount: 1.5, Radius: 1.5)
   - Non-local h: 1.2
   - Process same image again

**Expected Result:**
- All three changes should be visible in output
- Log should reflect all parameter changes

## Verification Checklist

After the recent fix, these settings should ALL work correctly:

### Output Settings
- ✅ Format (PNG/JPG/TIFF)
- ✅ JPEG Quality
- ✅ Preserve Color
- ✅ Apply Sharpening
- ✅ Sharpen Amount
- ✅ Sharpen Radius

### Filter Toggles
- ✅ Enable Gaussian
- ✅ Enable Median
- ✅ Enable Non-local Means

### Filter Parameters
- ✅ Gaussian Sigma
- ✅ Median Size
- ✅ Non-local h multiplier
- ✅ Non-local Fast Mode
- ✅ Non-local Patch Size
- ✅ Non-local Patch Distance

### RAW Settings
- ✅ Processing Mode (full/half/preview)

## What Was Fixed

**Before Fix:**
- `process_files()` method (used by GUI file selection) was missing `preserve_color` parameter
- Settings appeared to change in GUI but didn't affect output

**After Fix:**
- All filter calls now include `preserve_color` parameter
- All settings are read from GUI and applied correctly
- Log shows `[color-preserving]` when enabled

## Code Flow

```
GUI Spinbox/Checkbox
    ↓
tk.Variable (DoubleVar/BooleanVar/etc.)
    ↓
create_config() reads .get() from variables
    ↓
OutputConfig/FilterConfig objects
    ↓
Processor uses config.output.sharpen_amount, etc.
    ↓
Filter functions receive parameters
    ↓
Output reflects settings
```

## Common Issues

**"Settings don't seem to change output"**
- Make sure you're processing the SAME image for comparison
- Check the log for parameter values
- Look for `[color-preserving]` tag in log
- Compare file sizes (sharpening increases file size slightly)

**"Can't see difference"**
- Some changes are subtle (especially with clean images)
- Use a noisy image for testing
- Try extreme values (e.g., sharpen amount: 2.0)
- Use the "🔍 View Comparison" button

**"Log doesn't show my changes"**
- Settings are only read when you click "Start Processing"
- Changing settings after processing starts has no effect
- Must click "Start Processing" again to apply new settings

## Automated Test (For Developers)

```python
# Test that config reads GUI values correctly
def test_config_creation():
    app = DenoiserGUI(root)
    
    # Change settings
    app.sharpen_amount.set(1.8)
    app.sharpen_radius.set(2.5)
    app.preserve_color.set(False)
    
    # Create config
    config = app.create_config()
    
    # Verify
    assert config.output.sharpen_amount == 1.8
    assert config.output.sharpen_radius == 2.5
    assert config.output.preserve_color == False
    
    print("✅ Config correctly reads GUI values")
```
