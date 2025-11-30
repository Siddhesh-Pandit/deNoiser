# AI Tensor Dimension Fix - Auto-Padding

## Problem

AI models (SCUNet, NAFNet) require image dimensions to be divisible by 8. When processing images with incompatible dimensions, the model fails with:

```
RuntimeError: Sizes of tensors must match except in dimension 1. 
Expected size 1634 but got size 1633 for tensor number 1 in the list.
```

**Example:**
- Image: 1633 × 1634 pixels
- 1633 % 8 = 1 (not divisible)
- 1634 % 8 = 2 (not divisible)
- Result: Tensor mismatch error

## Solution: Auto-Padding

The AI denoiser now automatically pads images to compatible dimensions:

### How It Works

1. **Check dimensions**: Calculate padding needed
   ```python
   pad_h = (8 - height % 8) % 8
   pad_w = (8 - width % 8) % 8
   ```

2. **Pad if needed**: Add padding using reflection mode
   ```python
   # Reflection mode avoids edge artifacts
   padded = np.pad(image, ((0, pad_h), (0, pad_w), (0, 0)), mode='reflect')
   ```

3. **Process**: Run AI model on padded image

4. **Crop back**: Remove padding from output
   ```python
   output = output[:original_height, :original_width, :]
   ```

### Example

**Before (Failed):**
```
Image: 1633 × 1634
AI Model: ✗ Error - dimensions not divisible by 8
Fallback: Classical filters
```

**After (Success):**
```
Image: 1633 × 1634
Padding: +7 height, +6 width
Padded: 1640 × 1640 (divisible by 8)
AI Model: ✓ Success
Cropped: 1633 × 1634 (back to original)
```

## Why Reflection Padding?

**Reflection mode** mirrors pixels at the edges:
```
Original:  [a b c d]
Reflected: [a b c d c b]
```

This avoids:
- Black borders (zero padding)
- Discontinuities (edge padding)
- Artifacts at image edges

## Logging

The AI denoiser now logs padding operations:
```
ℹ Padded image from 1633×1634 to 1640×1640 (divisible by 8)
✓ AI denoising complete
ℹ Cropped output back to original size 1633×1634
```

## Performance Impact

**Minimal:**
- Padding: < 1ms (NumPy operation)
- Processing: Same (model runs on padded size)
- Cropping: < 1ms (array slicing)

**Worst case:**
- Image: 1×1 pixel
- Padded to: 8×8 pixels
- Overhead: ~64× more pixels (but still tiny)

**Typical case:**
- Image: 1633×1634 pixels
- Padded to: 1640×1640 pixels
- Overhead: ~0.8% more pixels (negligible)

## Edge Cases

### 1. Already Compatible
```
Image: 1600 × 1600 (divisible by 8)
Padding: 0 × 0 (no padding needed)
Result: Processed as-is
```

### 2. One Dimension Compatible
```
Image: 1600 × 1633
Padding: 0 × 7
Result: Only width padded
```

### 3. Very Small Image
```
Image: 5 × 5
Padding: 3 × 3
Padded: 8 × 8
Result: Works correctly
```

### 4. Grayscale Image
```
Image: 1633 × 1634 × 1 (grayscale)
Padding: Applied to H×W only
Result: Channel dimension unchanged
```

## Testing

### Test 1: Odd Dimensions
```python
# Image with dimensions not divisible by 8
image = np.random.randint(0, 255, (1633, 1634, 3), dtype=np.uint8)
result = denoise_with_ai(image)
assert result.shape == (1633, 1634, 3)  # Same as input
```

### Test 2: Already Compatible
```python
# Image with dimensions divisible by 8
image = np.random.randint(0, 255, (1600, 1600, 3), dtype=np.uint8)
result = denoise_with_ai(image)
assert result.shape == (1600, 1600, 3)  # No padding needed
```

### Test 3: Small Image
```python
# Very small image
image = np.random.randint(0, 255, (5, 5, 3), dtype=np.uint8)
result = denoise_with_ai(image)
assert result.shape == (5, 5, 3)  # Padded to 8×8, then cropped back
```

## Files Modified

**ai_denoiser.py:**
- Added padding calculation before tensor conversion
- Added reflection padding for incompatible dimensions
- Added cropping after inference to restore original size
- Added logging for padding/cropping operations

## Benefits

1. **No more tensor errors** - All images work with AI
2. **Transparent to user** - Automatic, no configuration needed
3. **Preserves quality** - Reflection padding avoids artifacts
4. **Minimal overhead** - Typically < 1% extra pixels
5. **Maintains dimensions** - Output matches input exactly

## Before vs After

### Before This Fix
- ✗ 1633×1634 image → Error → Fallback to classical
- ✓ 1600×1600 image → Success

### After This Fix
- ✓ 1633×1634 image → Auto-pad → Success
- ✓ 1600×1600 image → No padding → Success
- ✓ Any dimension → Works!

## Future Improvements

1. **Tile processing** - For very large images, process in tiles
2. **Smart padding** - Use content-aware padding for better edges
3. **Dimension warning** - Show tooltip if heavy padding needed (>10%)
4. **Padding visualization** - Show padded area in preview (debug mode)
