# Color Boost Fix - Sharpening with Color Preservation

## The Problem

When using **"Preserve Color"** + **"Apply Sharpening"** together, blues (and other colors) were getting boosted/oversaturated.

### Why This Happened

1. **Denoising** was correctly applied to luminance only (preserving colors)
2. **Sharpening** was incorrectly applied to all RGB channels
3. This caused color channels to be sharpened, boosting saturation

### Example

```
Original Image → Denoise (luminance only) → Sharpen (RGB) → Color boost! ❌
```

The sharpening was enhancing color differences, making blues more intense.

## The Fix

Sharpening now respects the **"Preserve Color"** setting:

- When **Preserve Color is ON**: Sharpening applied to luminance only
- When **Preserve Color is OFF**: Sharpening applied to full RGB

### Code Changes

**1. Updated `apply_unsharp_mask()` in `image_filters.py`:**
- Added `preserve_color` parameter
- When enabled, uses `_denoise_luminance_only()` helper
- Sharpens only the L channel in LAB color space
- Preserves A and B channels (color information)

**2. Updated processor to pass `preserve_color`:**
```python
filtered_img = apply_unsharp_mask(
    filtered_img, 
    radius=self.config.output.sharpen_radius,
    amount=self.config.output.sharpen_amount,
    preserve_color=self.config.output.preserve_color  # ← Added
)
```

**3. Added logging:**
```
✓ Applied sharpening (amount=1.5, radius=1.5) [color-preserving]
```

## Result

Now the complete pipeline is color-preserving:

```
Original Image → Denoise (luminance only) → Sharpen (luminance only) → Natural colors! ✅
```

## Testing

### Before Fix
- Preserve Color: ON
- Apply Sharpening: ON
- Result: Blues boosted, colors oversaturated

### After Fix
- Preserve Color: ON
- Apply Sharpening: ON
- Result: Natural colors, proper sharpening

## When to Use Each Mode

### Preserve Color ON (Recommended)
- **Use for:** Color photos, portraits, landscapes
- **Effect:** Denoises and sharpens brightness only
- **Result:** Vibrant, natural colors maintained
- **Best for:** Most photography

### Preserve Color OFF
- **Use for:** Grayscale images, artistic effects
- **Effect:** Denoises and sharpens all channels
- **Result:** May affect color saturation
- **Best for:** Black & white, special cases

## Technical Details

### Color Space Conversion

When `preserve_color=True`:

1. Convert RGB → LAB color space
2. Extract L (lightness) channel
3. Apply sharpening to L channel only
4. Keep A (green-red) and B (blue-yellow) unchanged
5. Convert back to RGB

### Why LAB?

- **L channel** = Brightness/luminance
- **A channel** = Green to red
- **B channel** = Blue to yellow
- Separating these prevents color shifts

### Sharpening Algorithm

Unsharp mask formula:
```
sharpened = original + amount × (original - blurred)
```

When color-preserving:
- Applied only to L channel
- A and B channels pass through unchanged
- Result: Sharp edges without color artifacts

## Verification

Check the log output:

```
============================================================
PROCESSING SETTINGS:
============================================================
Preserve color: ON
Apply sharpening: ON
  • Sharpen amount: 1.5
  • Sharpen radius: 1.5
============================================================
[1/1] Processing: photo.jpg
  ✓ Non-local means: ... [color-preserving]
  ✓ Applied sharpening (amount=1.5, radius=1.5) [color-preserving]
```

Both operations should show `[color-preserving]` tag.

## Related Settings

All these now work together correctly:

- ✅ Preserve Color
- ✅ Apply Sharpening
- ✅ Sharpen Amount
- ✅ Sharpen Radius
- ✅ All filter types (Gaussian, Median, Non-local)

## Summary

The fix ensures that when "Preserve Color" is enabled, **both denoising and sharpening** work in the luminance channel only, preventing color boost and maintaining natural, vibrant colors throughout the entire processing pipeline.
