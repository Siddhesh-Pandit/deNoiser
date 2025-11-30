# Comparison Window with AI Mode & Output Settings

## Your Questions Answered

### Q1: Do output settings have an effect on AI mode?
**YES** - All output settings affect AI mode the same way they affect classical filters.

### Q2: Does the comparison window work with AI enabled + output settings?
**YES** - It should work. The comparison window looks for files with the `_nonlocal_ai` suffix when AI is enabled.

---

## How It Works

### Processing Order (AI Mode):
```
1. AI Denoising (SCUNet/NAFNet)
   ↓
2. Apply Mask (if present)
   ↓
3. Apply Sharpening (if enabled)
   ↓
4. Apply Saturation Boost (if enabled)
   ↓
5. Apply Brightness Boost (if enabled)
   ↓
6. Save as: filename_nonlocal_ai.png
```

### File Naming:

**Important:** When AI is enabled, it REPLACES the classical filter for each enabled filter.

**AI Disabled (Classical Filters):**
- Gaussian: `image_gaussian.png`
- Median: `image_median.png`
- Non-local Means: `image_nonlocal.png`

**AI Enabled (AI Replaces Classical):**
- AI + Gaussian enabled: `image_gaussian_ai.png`
- AI + Median enabled: `image_median_ai.png`
- AI + Non-local enabled: `image_nonlocal_ai.png`
- AI only (no classical filters): `image_nonlocal_ai.png`

The filename does NOT change based on output settings - they're baked into the saved file.

### Comparison Window Logic:
When you click "View Comparison", the window:
1. Checks which filters are enabled
2. Looks for files with matching suffixes (including `_ai` if AI is enabled)
3. Opens the first one found

**Priority order (AI Enabled):**
1. `nonlocal_ai` (if Non-local Means enabled)
2. `gaussian_ai` (if Gaussian enabled)
3. `median_ai` (if Median enabled)
4. `nonlocal_ai` (if no classical filters enabled)

**Priority order (AI Disabled):**
1. `gaussian` (if Gaussian enabled)
2. `median` (if Median enabled)
3. `nonlocal` (if Non-local Means enabled)

---

## Troubleshooting

### If comparison window doesn't work:

**Check 1: File exists?**
```
Look in your output folder for:

AI Enabled:
- image_gaussian_ai.png (if Gaussian enabled)
- image_median_ai.png (if Median enabled)
- image_nonlocal_ai.png (if Non-local Means enabled OR no classical filters)

AI Disabled:
- image_gaussian.png (if Gaussian enabled)
- image_median.png (if Median enabled)
- image_nonlocal.png (if Non-local Means enabled)
```

**Check 2: Output format matches?**
The comparison window looks for files with the format you selected (PNG/JPEG/TIFF).
If you changed the format after processing, it won't find the file.

**Check 3: Processing completed?**
Make sure the processing finished successfully. Check the log for:
```
✓ AI denoising complete
✓ Applied sharpening (if enabled)
✓ Boosted saturation (if enabled)
✓ Boosted brightness (if enabled)
```

**Check 4: Multiple filters enabled?**
If you have multiple filters enabled, the comparison shows the FIRST one found.
- With AI: Shows AI result
- Without AI: Shows Gaussian → Median → Non-local (in that order)

---

## Output Settings Effect on AI

All output settings work with AI mode:

| Setting | Effect on AI | Applied When |
|---------|-------------|--------------|
| **Output Format** | ✅ Yes | During save |
| **JPEG Quality** | ✅ Yes | During save (JPEG only) |
| **Preserve Color** | ❌ No | AI handles color internally |
| **Sharpening** | ✅ Yes | After AI, before save |
| **Saturation Boost** | ✅ Yes | After AI, before save |
| **Brightness Boost** | ✅ Yes | After AI, before save |
| **Selective Denoising (Mask)** | ✅ Yes | After AI, blends with original |

**Note:** "Preserve Color" only affects classical filters. AI models handle color preservation internally.

---

## Example Scenarios

### Scenario 1: AI + Sharpening + Saturation
```
Settings:
- AI: ✅ Enabled (SCUNet)
- Sharpening: ✅ Enabled (amount: 1.2)
- Saturation: ✅ Enabled (amount: 1.3)

Result:
- File: image_nonlocal_ai.png
- Contains: AI denoised + sharpened + saturated
- Comparison: Shows this combined result vs original
```

### Scenario 2: AI + Classical Filters
```
Settings:
- AI: ✅ Enabled
- Gaussian: ✅ Enabled
- Median: ✅ Enabled

Result:
- Files created:
  - image_gaussian_ai.png (AI replaces Gaussian)
  - image_median_ai.png (AI replaces Median)
- Comparison: Shows gaussian_ai result (first priority)

Note: When AI is enabled, it REPLACES the classical filter.
You don't get both classical and AI versions.
```

### Scenario 3: AI + Mask + Output Settings
```
Settings:
- AI: ✅ Enabled
- Mask: ✅ Created (painted areas)
- Sharpening: ✅ Enabled
- Saturation: ✅ Enabled

Result:
- File: image_nonlocal_ai.png
- Contains:
  - Masked areas: AI denoised + sharpened + saturated
  - Unmasked areas: Original (untouched)
- Comparison: Shows selective result vs original
```

---

## If You're Still Having Issues

Please check:
1. **Log output** - Does it show successful AI processing?
2. **Output folder** - Do you see the `_nonlocal_ai` file?
3. **File format** - Does it match your selected output format?
4. **Error messages** - Any errors in the log window?

If the comparison window still doesn't work, there might be a bug. Please share:
- Your settings (AI model, output format, enabled filters)
- Log output
- Whether the output file exists
