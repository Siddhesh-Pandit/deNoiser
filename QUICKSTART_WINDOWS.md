# Windows Quick Start - 5 Minutes

Get Image Denoiser running on Windows in 5 minutes or less.

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  🪟 WINDOWS INSTALLATION (5 minutes)                    │
│                                                         │
│  1. Install Python 3.12                                 │
│  2. Download project (ZIP)                              │
│  3. Run install_dependencies.bat                        │
│  4. Run run_gui.bat                                     │
│  5. Done! ✅                                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Installation Steps

### Installation (5 minutes)

**No releases yet - follow these steps:**

#### Step 1: Install Python (2 minutes)
1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Download Python 3.12
3. Run installer
4. ✅ **CHECK "Add Python to PATH"** ← Important!
5. Click "Install Now"

#### Step 2: Get the Code (1 minute)
1. Download ZIP from GitHub (green "Code" button)
2. Extract to a folder (e.g., Desktop)

#### Step 3: Install Dependencies (1 minute)
1. Open the extracted folder
2. Double-click `install_dependencies.bat`
3. Wait for "Installation complete!"

#### Step 4: Run It (1 minute)
1. Double-click `run_gui.bat` (no console window)
   - Or use `run_gui_debug.bat` to see console output for debugging
2. Start denoising!

#### Optional: AI Denoising (Better Quality)
1. In the GUI, check "Enable AI Denoiser 🤖"
2. Click "Yes" to install AI dependencies (~500MB)
3. Wait for installation (3-5 minutes)
4. Restart the app
5. Enjoy better denoising quality!

---

## First Time Using the App?

### Quick Tutorial

1. **Click "Folder" or "Files"** to select images
2. **Click "Browse..."** to choose output folder
3. **Try a preset:** Click "📷 Photos" for best results
4. **Click "Start Processing"**
5. **Click "🔍 View Comparison"** to see before/after

### Recommended Settings for Beginners

**For Photos:**
- Use "📷 Photos" preset
- Leave all settings as-is
- Just click "Start Processing"

**For Scanned Documents:**
- Use "📄 Documents" preset
- Click "Start Processing"

**For Night Photos:**
- Use "🌙 Low-Light" preset
- Click "Start Processing"

---

## Common First-Time Issues

### "Python is not recognized"
**Fix:** Reinstall Python and check "Add Python to PATH"

### "No module named..."
**Fix:** Run `install_dependencies.bat` again

### Antivirus Warning
**Fix:** Click "More info" → "Run anyway" (it's safe)

### Nothing Happens When I Click
**Fix:** Check the log at the bottom of the window for errors

---

## What's Next?

✅ **Working?** Great! Read [USAGE.md](USAGE.md) for advanced features

❌ **Problems?** See [WINDOWS_INSTALL.md](WINDOWS_INSTALL.md) for detailed troubleshooting

💡 **Want to build your own .exe?** See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)

---

## File Locations

After installation, you'll have:

```
📁 ImageDenoiser/
  ├── 🚀 run_gui.bat          ← Double-click this to start (no console)
  ├── 🔧 run_gui_debug.bat    ← Use this to see console output
  ├── ⚙️ install_dependencies.bat  ← Run this first (if from source)
  ├── 🤖 install_ai.bat       ← Optional: Install AI denoising
  ├── 📝 config.ini           ← Settings file
  ├── 🐍 gui.py               ← Main program
  └── 📖 USAGE.md             ← Full documentation
```

---

## Tips for Best Results

1. **Start with presets** - They're optimized for common scenarios
2. **Use PNG output** - Best quality (default)
3. **Process a test image first** - Before batch processing hundreds
4. **Check the comparison** - Use "🔍 View Comparison" to verify results
5. **Read the log** - It shows what's happening

---

## Support

- 📖 Full Guide: [WINDOWS_INSTALL.md](WINDOWS_INSTALL.md)
- 📚 User Manual: [USAGE.md](USAGE.md)
- 🐛 Issues: [GitHub Issues](../../issues)
