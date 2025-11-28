# Before/After Comparison Window Feature

## Overview

Added an interactive before/after comparison window that appears after processing images with multiple filters. Users can drag a slider to smoothly reveal the processed image over the original, making it easy to evaluate denoising effectiveness.

## How It Works

### Always-Available Button
The **"🔍 View Comparison"** button appears next to the "Start Processing" button:
- Initially disabled (grayed out)
- Becomes enabled after successful processing
- Remains available for repeated viewing
- Works with any filter configuration

### Automatic Dialog (Multiple Filters Only)
When processing with multiple filters, a dialog also appears asking:
- "Would you like to view a before/after comparison?"
- Clicking "Yes" opens the comparison window immediately
- Clicking "No" lets you open it later via the button

### User Experience
1. Process images with any filter configuration
2. After completion, the "🔍 View Comparison" button becomes active
3. Click the button anytime to open the comparison window
4. The window displays the first processed image with an interactive slider
5. Drag the slider left/right to reveal the processed image over the original

### Visual Design
- **White slider line** with circular handle in the center
- **Arrow indicators** (◀ ▶) on the handle showing drag direction
- **Zoom controls** at top: 🔍− / 100% / 🔍+ / Reset buttons
- **Labels** at bottom: "◀ BEFORE" and "AFTER ▶"
- **Black background** for clean presentation
- **Automatic scaling** to fit window while maintaining aspect ratio

## Technical Implementation

### New Class: `BeforeAfterWindow`
Located in `gui.py`, this class creates a Toplevel window with:
- Canvas-based image display
- PIL/Pillow for image loading and manipulation
- Real-time clipping of the "after" image based on slider position
- Mouse event handling for dragging

### Key Methods
- `scale_images()` - Scales images to fit display (max 980x600)
- `update_clip()` - Clips the after image at slider position
- `on_click()`, `on_drag()`, `on_release()` - Handle mouse interaction

### Integration Points
- `show_comparison_dialog()` - Decides whether to offer comparison
- `show_comparison_window()` - Opens the comparison window
- `last_processed_files` - Tracks processed files for comparison

## User Benefits

1. **Instant Visual Feedback** - See exactly what changed
2. **Easy Evaluation** - Quickly judge if denoising worked well
3. **No File Switching** - Compare without opening multiple files
4. **Intuitive Interface** - Natural drag interaction
5. **Zoom for Details** - Inspect fine details at up to 400% zoom
6. **Mouse Wheel Support** - Quick zoom with scroll wheel
7. **Automatic Scaling** - Works with any image size

## When Comparison is Available

| Preset | Button Available? | Auto-Dialog? |
|--------|------------------|--------------|
| Photos | ✅ Yes (after processing) | ❌ No |
| Documents | ✅ Yes (after processing) | ❌ No |
| Low-Light | ✅ Yes (after processing) | ❌ No |
| Compare All | ✅ Yes (after processing) | ✅ Yes |
| Custom (2+ filters) | ✅ Yes (after processing) | ✅ Yes |
| Custom (1 filter) | ✅ Yes (after processing) | ❌ No |

**Note:** The button is always available after processing. The automatic dialog only appears when using multiple filters.

## Dependencies

Uses existing Pillow dependency (already in requirements.txt for icon generation).

## Testing

Run `test_comparison.py` to test the comparison window with generated test images:
```bash
python test_comparison.py
```

This creates simple before/after images and opens the comparison window for testing.

## Zoom Feature

### Controls
- **🔍− button** - Zoom out by 25%
- **🔍+ button** - Zoom in by 25%
- **Reset button** - Return to 100% zoom
- **Mouse wheel** - Scroll to zoom in/out
- **Scrollbars** - Pan around when zoomed in
- **Zoom range** - 25% to 400%

### Usage
1. Open comparison window
2. Use zoom buttons or scroll wheel
3. Zoom in to inspect fine details
4. Use scrollbars to pan around zoomed image
5. Drag slider at any zoom level
6. Click Reset to return to original size

### Benefits
- **Fixed window size** - Window doesn't resize when zooming
- **Scrollable view** - Pan around large zoomed images
- **Inspect details** - See noise reduction at pixel level
- **Verify sharpness** - Check if edges are preserved
- **Compare textures** - Examine how filters affect fine detail
- **Quality check** - Ensure no artifacts introduced

## Future Enhancements

Potential improvements:
- Compare multiple filter outputs side-by-side
- Save comparison as split image
- Keyboard shortcuts for slider control
- Multiple image navigation (prev/next buttons)
- Pan support when zoomed in
