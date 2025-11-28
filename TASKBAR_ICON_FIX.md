# Taskbar Icon Fix for Windows

## The Issue

When running the app from Python on Windows, the taskbar shows the generic Python icon instead of the custom Image Denoiser icon.

## Why This Happens

Windows groups Python scripts together under the Python executable's icon by default. To show a custom icon in the taskbar, Windows needs to know this is a separate application.

## The Fix

Added Windows-specific code to set the Application User Model ID:

```python
if sys.platform == 'win32':
    import ctypes
    myappid = 'imagedenoiser.gui.1.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
```

This tells Windows to treat the app as separate from Python and use the custom icon.

## What You'll See

### Before Fix:
- Taskbar: Generic Python icon 🐍
- Window title bar: Custom icon ✅

### After Fix:
- Taskbar: Custom Image Denoiser icon ✅
- Window title bar: Custom icon ✅

## Platform Behavior

| Platform | Taskbar Icon | Window Icon |
|----------|--------------|-------------|
| Windows (before fix) | Python icon | Custom icon |
| Windows (after fix) | Custom icon | Custom icon |
| macOS | Custom icon | Custom icon |
| Linux | Custom icon | Custom icon |

## Notes

- The fix only applies when running from Python
- Standalone .exe builds automatically have the correct icon
- The fix is Windows-specific and doesn't affect other platforms
- Uses `ctypes` which is built into Python (no extra dependencies)

## Testing

To verify the fix works:

1. Run the app: `python gui.py`
2. Check the Windows taskbar
3. You should see the blue sparkle icon instead of the Python icon

## Fallback

If the fix fails for any reason:
- The app still works normally
- Only the taskbar icon is affected
- The window title bar icon still shows correctly
- Error is silently caught and ignored

## For Standalone Executables

When you build a standalone .exe using PyInstaller:
- The icon is embedded in the executable
- No special handling needed
- Taskbar icon works automatically
- See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) for building
