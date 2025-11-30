# Cancel Button Feature

## Overview

Added ability to cancel AI/classical processing mid-operation with a dedicated Cancel button.

## Implementation

### GUI Changes

**New Button:**
- Location: Between "Start Processing" and "View Comparison"
- Label: "⏹ Cancel"
- State: Disabled by default, enabled during processing
- Tooltip: "Cancel current processing operation"

**Button States:**
- **Idle**: Disabled (grayed out)
- **Processing**: Enabled (clickable)
- **Cancelling**: Disabled with "⏹ Cancelling..." status

### How It Works

1. **User clicks "Start Processing"**
   - Process button disabled
   - Cancel button enabled
   - `cancel_requested` flag set to False

2. **User clicks "Cancel"**
   - `cancel_requested` flag set to True
   - Cancel button disabled
   - Status shows "⏹ Cancelling..."
   - Log shows "⏹ Processing cancelled by user"

3. **Processor checks flag**
   - Before each image: Check `cancel_flag()`
   - If True: Break loop, cleanup, return

4. **Cleanup**
   - Processing flag reset
   - Buttons restored to normal state
   - Partial results saved (completed images)

### Code Flow

```
User clicks Cancel
    ↓
cancel_requested = True
    ↓
Processor checks cancel_flag()
    ↓
Break processing loop
    ↓
Save completed images
    ↓
Cleanup and restore UI
```

### Cancellation Points

The processor checks for cancellation:
- **Before each image** in batch processing
- **Before each file** in file processing
- **Not during** individual image processing (too late)

This means:
- ✓ Can cancel between images
- ✗ Cannot cancel mid-image (would corrupt output)

## User Experience

### Scenario 1: Cancel During Batch
```
Processing 100 images...
Image 1: ✓ Complete
Image 2: ✓ Complete
Image 3: [User clicks Cancel]
⏹ Cancelling...
⏹ Processing cancelled
Result: 2 images saved, 98 skipped
```

### Scenario 2: Cancel During AI Model Loading
```
🤖 AI: Loading model...
[User clicks Cancel]
⏹ Cancelling...
⏹ Processing cancelled
Result: No images processed
```

### Scenario 3: Cancel During Single Image
```
Processing image...
[User clicks Cancel]
⏹ Cancelling...
[Image completes anyway - too late]
Result: 1 image saved
```

## Benefits

1. **User Control** - Stop long operations
2. **Time Saving** - Don't wait for 100 images if you only needed 5
3. **Error Recovery** - Cancel if wrong settings detected
4. **Resource Management** - Free up CPU/GPU for other tasks

## Limitations

### Cannot Cancel During:
- Individual image AI processing (model inference)
- Individual image classical filtering
- File I/O operations (loading/saving)

### Why?
Cancelling mid-operation could:
- Corrupt output files
- Leave partial data in memory
- Cause model state issues

### Solution:
Cancellation happens **between** images, ensuring:
- Completed images are fully saved
- No partial/corrupt files
- Clean state for next operation

## Technical Details

### Cancel Flag
```python
self.cancel_requested = False  # GUI flag
processor.cancel_flag = lambda: self.cancel_requested  # Processor check
```

### Check Pattern
```python
for image in images:
    if hasattr(self, 'cancel_flag') and self.cancel_flag():
        self.logger.warning("⏹ Processing cancelled")
        break
    # Process image...
```

### Thread Safety
- Flag checked in processing thread
- UI updates via `root.after(0, callback)`
- No race conditions (simple boolean flag)

## Testing

### Test 1: Cancel After First Image
1. Select folder with 10 images
2. Click "Start Processing"
3. Wait for first image to complete
4. Click "Cancel"
5. **Expected:** 1 image saved, processing stops

### Test 2: Cancel During Model Loading
1. Enable AI (first time, model not downloaded)
2. Click "Start Processing"
3. During "Loading model..." click "Cancel"
4. **Expected:** Processing stops, no images saved

### Test 3: Cancel Button States
1. **Before processing:** Cancel button disabled
2. **During processing:** Cancel button enabled
3. **After cancel:** Cancel button disabled
4. **After completion:** Cancel button disabled

### Test 4: Multiple Cancels
1. Start processing
2. Cancel
3. Start processing again
4. Cancel again
5. **Expected:** Works correctly both times

## Future Improvements

1. **Finer-grained cancellation** - Cancel during AI inference (requires model support)
2. **Progress estimation** - Show "Cancelling after current image..."
3. **Partial results dialog** - "Cancelled. 5 of 10 images processed. View results?"
4. **Keyboard shortcut** - Esc key to cancel
5. **Confirmation dialog** - "Are you sure?" for long operations

## Files Modified

1. **gui.py**
   - Added cancel button
   - Added `cancel_requested` flag
   - Added `cancel_processing()` method
   - Pass cancel flag to processor
   - Handle cancellation in completion

2. **processor.py**
   - Check `cancel_flag()` before each image
   - Log cancellation message
   - Clean exit on cancellation
