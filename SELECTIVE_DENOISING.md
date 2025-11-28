# Selective Denoising with Mask Editor

## Overview

The Mask Editor allows you to paint specific areas of an image to denoise, leaving other areas untouched. This is perfect for:
- Denoising subject while keeping background sharp
- Processing only noisy areas
- Protecting important details from processing

## How to Use

### 1. Select Single Image

- Click **"Files"** button
- Select **ONE image** (mask editor only works with single images)
- The **"🎨 Edit Mask"** button will become enabled

### 2. Open Mask Editor

- Click **"🎨 Edit Mask (Selective Denoising)"** button
- Mask editor window opens showing your image

### 3. Paint Mask

**Brush Tool (Default):**
- Paint areas you want to denoise (shows as green overlay)
- Click and drag to paint
- Painted areas = will be denoised
- Unpainted areas = will be skipped

**Eraser Tool:**
- Remove painted areas
- Click **"🧹 Eraser"** or press **E** key
- Click and drag to erase mask

**Adjust Brush Size:**
- Use spinbox to change size (5-100 pixels)
- Larger brush for broad areas
- Smaller brush for precise work

### 4. Clear or Reset

- Click **"🗑️ Clear All"** to remove entire mask
- Start over if needed

### 5. Apply Mask

- Click **"✓ Apply Mask"** when done
- Mask is saved and window closes
- Green checkmark appears: "✓ Mask applied"

### 6. Process Image

- Configure denoising settings as usual
- Click **"Start Processing"**
- Only masked areas will be denoised
- Unmasked areas remain completely unchanged
- Edges are smoothly blended (no visible seams)

## Keyboard Shortcuts

- **B** - Select Brush tool
- **E** - Select Eraser tool
- **C** - Clear all mask

## Visual Guide

```
┌─────────────────────────────────────────────────────┐
│ 🖌️ Brush | 🧹 Eraser | Size: [20] | 🗑️ Clear All  │
├─────────────────────────────────────────────────────┤
│                                                     │
│         [Image with green overlay on              │
│          painted areas]                            │
│                                                     │
│                                                     │
├─────────────────────────────────────────────────────┤
│ 💡 Paint areas to denoise    Tool: Brush          │
│                               ✓ Apply | ✗ Cancel   │
└─────────────────────────────────────────────────────┘
```

## Tips

### For Best Results

1. **Paint generously** - Include some margin around noisy areas
2. **Use larger brush** for broad areas, then refine with smaller brush
3. **Preview before applying** - Green overlay shows what will be processed
4. **Don't worry about precision** - Mask edges are automatically blended

### Common Use Cases

**Portrait with Noisy Background:**
- Paint only the subject (face, body)
- Leave background unpainted
- Result: Clean subject, original background

**Landscape with Noisy Sky:**
- Paint only the sky
- Leave foreground unpainted
- Result: Clean sky, sharp foreground

**Product Photo:**
- Paint only the product
- Leave background/table unpainted
- Result: Clean product, original context

## Technical Details

### Mask Format

- **White (255)** = Denoise this area
- **Black (0)** = Skip this area
- Mask is automatically scaled to match image resolution

### Processing

1. Mask is applied to image
2. Only masked areas are denoised
3. Edges are smoothly blended
4. Unmasked areas remain unchanged

### Limitations

- **Single image only** - Mask editor not available for batch processing
- **No auto-selection** - Manual painting only (for now)
- **No gradient** - Binary mask (on/off)

## Future Enhancements

Planned features:
- Auto selection (GrabCut algorithm)
- Gradient/feathered edges
- Save/load masks
- Multiple masks per image
- Invert mask option

## Troubleshooting

**"Edit Mask button is disabled"**
- Make sure you selected exactly ONE file
- Button only works with single file selection

**"Empty Mask warning"**
- You didn't paint anything
- Either paint some areas or click Cancel

**"Mask not applied"**
- Make sure you clicked "✓ Apply Mask"
- Check for green checkmark: "✓ Mask applied"

**"Entire image is denoised"**
- Mask might not be applied
- Check for "✓ Mask applied" status
- Try creating mask again

## Example Workflow

1. Select single noisy portrait image
2. Click "🎨 Edit Mask"
3. Paint over the face and body (green overlay)
4. Leave background unpainted
5. Click "✓ Apply Mask"
6. Select "📷 Photos" preset
7. Click "Start Processing"
8. Result: Clean subject, original background

The mask editor gives you precise control over which areas get denoised!
