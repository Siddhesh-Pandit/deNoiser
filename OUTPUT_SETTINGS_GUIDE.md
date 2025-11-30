# Output Settings - Effect on AI vs Classical Denoising

## Summary

**YES** - All output settings affect AI denoising the same way they affect classical denoising.

## Output Settings Breakdown

### 1. Output Format & Quality
**Settings**: Format (PNG/JPEG/TIFF), JPEG Quality, Preserve Original Format

**Effect on AI**: ✅ YES
- AI output is saved in selected format
- JPEG quality applies to AI outputs
- Format preservation works for AI

**Example**:
- Format: JPEG, Quality: 95
- AI output: `image_nonlocal_ai.jpg` at 95% quality

---

### 2. Preserve Color
**Setting**: Preserve Color checkbox

**Effect on AI**: ❌ NO (AI handles color internally)
- AI models are trained on RGB images
- They preserve color naturally
- This setting only affects classical filters

**Note**: AI doesn't need this setting because neural networks learn to preserve color during training.

---

### 3. Sharpening
**Settings**: Apply Sharpening, Sharpen Amount, Sharpen Radius

**Effect on AI**: ✅ YES
- Applied AFTER AI denoising
- Helps restore structure that AI might smooth
- Mask-aware (only sharpens masked areas if mask present)

**Processing Order**:
```
1. AI denoising
2. Apply mask (if present)
3. Apply sharpening (if enabled)
```

**Recommended for AI**:
- Enable sharpening: ✅ Yes
- Amount: 0.5-0.8 (lighter than classical)
- Radius: 1.0-1.5

---

### 4. Saturation Boost
**Settings**: Boost Saturation, Saturation Amount

**Effect on AI**: ✅ YES
- Applied AFTER AI denoising
- Enhances colors in AI output
- Mask-aware (only boosts masked areas if mask present)

**Processing Order**:
```
1. AI denoising
2. Apply mask (if present)
3. Apply sharpening (if enabled)
4. Apply saturation boost (if enabled)
```

**Recommended for AI**:
- Usually not needed (AI preserves colors well)
- Use if colors look dull: Amount 1.1-1.2

---

### 5. Brightness Boost
**Settings**: Boost Brightness, Brightness Amount

**Effect on AI**: ✅ YES
- Applied AFTER AI denoising
- Lightens AI output
- Mask-aware (only brightens masked areas if mask present)

**Processing Order**:
```
1. AI denoising
2. Apply mask (if present)
3. Apply sharpening (if enabled)
4. Apply saturation boost (if enabled)
5. Apply brightness boost (if enabled)
```

**Recommended for AI**:
- Use if AI output is too dark
- Amount: 1.05-1.15

---

### 6. Selective Denoising (Mask)
**Setting**: Edit Mask button

**Effect on AI**: ✅ YES - FULLY SUPPORTED
- AI denoises only masked areas
- Unmasked areas remain original
- Same behavior as classical filters

**How it works**:
```python
# AI denoises entire image
ai_result = ai_denoise(image)

# Blend with original using mask
final = ai_result * mask + original * (1 - mask)
```

---

## Complete Processing Pipeline

### AI Mode (with all output settings enabled):

```
1. Load image
2. AI denoising (SCUNet or NAFNet)
3. Apply mask (if present)
   → Masked areas = AI denoised
   → Unmasked areas = Original
4. Apply sharpening (if enabled)
   → Only to masked areas if mask present
5. Apply saturation boost (if enabled)
   → Only to masked areas if mask present
6. Apply brightness boost (if enabled)
   → Only to masked areas if mask present
7. Save in selected format
```

### Classical Mode (for comparison):

```
1. Load image
2. Classical denoising (Gaussian/Median/Non-local Means)
3. Apply mask (if present)
4. Apply sharpening (if enabled)
5. Apply saturation boost (if enabled)
6. Apply brightness boost (if enabled)
7. Save in selected format
```

**Same pipeline!** Only step 2 differs (AI vs Classical).

---

## Settings Comparison Table

| Setting | Classical | AI | Notes |
|---------|-----------|----|----|
| **Output Format** | ✅ | ✅ | Same |
| **JPEG Quality** | ✅ | ✅ | Same |
| **Preserve Color** | ✅ | ❌ | AI doesn't need it |
| **Sharpening** | ✅ | ✅ | Same (lighter amount recommended for AI) |
| **Saturation Boost** | ✅ | ✅ | Same (less needed for AI) |
| **Brightness Boost** | ✅ | ✅ | Same |
| **Selective Mask** | ✅ | ✅ | Same |

---

## Recommended Settings

### For AI Denoising:

**Minimal (AI does most of the work)**:
```
AI Denoiser: ✅ Enabled
Model: SCUNet
Preserve Color: N/A (AI handles it)
Sharpening: ❌ Disabled (try without first)
Saturation: ❌ Disabled (AI preserves colors)
Brightness: ❌ Disabled (unless output is dark)
```

**Enhanced (for extra pop)**:
```
AI Denoiser: ✅ Enabled
Model: NAFNet
Sharpening: ✅ Enabled (amount: 0.6, radius: 1.2)
Saturation: ✅ Enabled (amount: 1.1)
Brightness: ❌ Disabled
```

**Selective (with mask)**:
```
AI Denoiser: ✅ Enabled
Edit Mask: Paint subject area
Sharpening: ✅ Enabled (amount: 0.8)
Saturation: ✅ Enabled (amount: 1.2)
→ Only subject is AI denoised and enhanced
→ Background stays original
```

### For Classical Denoising:

**Standard**:
```
Non-local Means: ✅ Enabled
Preserve Color: ✅ Enabled
Sharpening: ✅ Enabled (amount: 1.0-1.2)
Saturation: ❌ Disabled
```

---

## Key Takeaways

1. **Most output settings work the same** for AI and classical
2. **Preserve Color** is only for classical (AI doesn't need it)
3. **Post-processing** (sharpening, saturation, brightness) applies to both
4. **Masks** work identically for both AI and classical
5. **AI needs less post-processing** - it's already high quality

---

## Testing Recommendations

Try these combinations to see what works best:

**Test 1: AI Alone**
- AI: ✅, All post-processing: ❌
- See pure AI output

**Test 2: AI + Light Sharpening**
- AI: ✅, Sharpening: ✅ (0.6), Others: ❌
- Adds structure back

**Test 3: AI + Full Enhancement**
- AI: ✅, Sharpening: ✅, Saturation: ✅, Brightness: ✅
- Maximum enhancement

**Test 4: AI + Selective Mask**
- AI: ✅, Mask: Paint subject, Sharpening: ✅
- Enhanced subject, original background

Compare results to find your preferred settings!
