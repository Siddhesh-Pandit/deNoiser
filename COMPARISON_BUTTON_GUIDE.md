# View Comparison Button - Quick Guide

## Location

The **"🔍 View Comparison"** button is located next to the "Start Processing" button in the main GUI.

```
┌─────────────────────────────────────────┐
│                                         │
│  [Start Processing]  [🔍 View Comparison] │
│                                         │
└─────────────────────────────────────────┘
```

## Button States

### Before Processing
- **State:** Disabled (grayed out)
- **Tooltip:** "View before/after comparison of processed images (Available after processing)"
- **Action:** Cannot be clicked

### After Processing
- **State:** Enabled (clickable)
- **Tooltip:** Same as above
- **Action:** Opens interactive before/after comparison window

## What It Does

When clicked, the button:
1. Finds the first processed image from your last batch
2. Locates the corresponding output file (first available filter)
3. Opens an interactive comparison window
4. Shows a draggable slider to compare before/after

## Comparison Window Features

- **Draggable slider** - White vertical line with circular handle
- **Arrow indicators** - ◀ ▶ on the handle
- **Labels** - "◀ BEFORE" and "AFTER ▶" at bottom
- **Black background** - Clean, professional look
- **Auto-scaling** - Images fit window while maintaining aspect ratio
- **Real-time reveal** - Smooth transition as you drag

## Usage Tips

1. **Process first** - Button only works after successful processing
2. **Any preset works** - Photos, Documents, Low-Light, or Compare All
3. **Reusable** - Click multiple times to view again
4. **First image shown** - Shows first processed image by default
5. **First filter shown** - If multiple filters enabled, shows first available output

## Automatic Dialog

When using **multiple filters** (Compare All, or custom 2+ filters):
- A dialog appears after processing: "Would you like to view a before/after comparison?"
- Click "Yes" to open immediately
- Click "No" to skip (you can still use the button later)

When using **single filter** (Photos, Documents, Low-Light):
- No automatic dialog
- Just use the button when you're ready

## Troubleshooting

**Button stays disabled:**
- Make sure processing completed successfully
- Check the log for any errors

**"No Images" message:**
- Process some images first
- Button was clicked before any processing

**"Could not find processed image":**
- Output folder may have been moved/deleted
- Try processing again

**Comparison window doesn't open:**
- Check that output files exist in the output folder
- Verify image files are readable
