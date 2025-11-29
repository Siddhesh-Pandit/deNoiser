# AI Dependencies Installation - All Methods

## Overview

AI denoising is **optional** and requires PyTorch (~500MB). You have multiple ways to install it:

## 🌟 Method 1: In-GUI Installation (Recommended)

**Easiest for most users!**

### Steps:
1. Install basic dependencies first:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the GUI:
   ```bash
   python gui.py
   ```

3. Check "Enable AI Denoiser 🤖"

4. When prompted, click **"Yes"** to install automatically

5. Wait for installation (3-5 minutes, ~500MB download)

6. Restart the application

### Advantages:
- ✅ No command line needed
- ✅ Progress bar shows installation status
- ✅ Automatic error handling
- ✅ Works on Windows, Mac, Linux

### How it works:
```
User clicks "Enable AI" 
  → GUI checks if PyTorch installed
  → If not: Shows dialog with 3 options
     - Yes: Install automatically (runs pip in background)
     - No: Show manual instructions
     - Cancel: Disable AI
  → Installation runs with progress window
  → User restarts app when done
```

---

## 📦 Method 2: Installation Scripts

**Good for initial setup**

### Windows:
```bash
# Option A: Install everything at once
install_dependencies.bat
# Will prompt: "Install AI dependencies? (y/n)"

# Option B: Install AI separately
install_ai.bat
```

### Mac/Linux:
```bash
# Option A: Install everything at once
./install_dependencies.sh
# Will prompt: "Install AI dependencies? (y/n)"

# Option B: Install AI separately  
./install_ai.sh
```

### Advantages:
- ✅ Can install everything at once
- ✅ Interactive prompts
- ✅ Clear success/failure messages

---

## 💻 Method 3: Manual Command Line

**For advanced users**

### Basic Installation:
```bash
pip install -r requirements.txt
pip install -r requirements-ai.txt
```

### With GPU Support (NVIDIA):
```bash
pip install -r requirements.txt
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### With Apple Silicon (M1/M2/M3):
```bash
pip install -r requirements.txt
pip install torch torchvision
# MPS support is automatic in PyTorch 2.0+
```

### Advantages:
- ✅ Full control
- ✅ Can specify GPU version
- ✅ Fastest for experienced users

---

## 🔄 Comparison

| Method | Difficulty | Best For | GUI Required |
|--------|-----------|----------|--------------|
| In-GUI | ⭐ Easy | Beginners | Yes |
| Scripts | ⭐⭐ Medium | Most users | No |
| Manual | ⭐⭐⭐ Advanced | Power users | No |

---

## 📋 What Gets Installed

### Core Dependencies (required):
- numpy
- scikit-image
- scipy
- Pillow

**Size**: ~50MB

### AI Dependencies (optional):
- torch (PyTorch)
- torchvision

**Size**: ~500MB (CPU) or ~2GB (GPU with CUDA)

---

## 🎯 Recommended Workflow

### For Beginners:
1. Run `install_dependencies.bat` (Windows) or `./install_dependencies.sh` (Mac/Linux)
2. Say "no" to AI when prompted (try classical methods first)
3. Later, if you want better quality:
   - Enable AI in GUI
   - Click "Yes" to install
   - Restart app

### For Advanced Users:
1. Install everything at once:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-ai.txt
   ```
2. Run GUI and enable AI immediately

---

## ❓ FAQ

**Q: Can I use the app without AI?**
A: Yes! Classical methods work great for most photos.

**Q: How much disk space needed?**
A: Core: ~50MB, AI: ~500MB, Total: ~550MB

**Q: Can I install AI later?**
A: Yes! Use any of the 3 methods anytime.

**Q: Do I need to restart after installing AI?**
A: Yes, restart the GUI to load PyTorch.

**Q: What if in-GUI installation fails?**
A: Try Method 2 (scripts) or Method 3 (manual).

**Q: Can I uninstall AI dependencies?**
A: Yes: `pip uninstall torch torchvision`

**Q: Does AI work offline?**
A: Yes, after initial model download (~3-9MB).

---

## 🐛 Troubleshooting

### In-GUI Installation Fails
1. Check internet connection
2. Try manual installation:
   ```bash
   pip install -r requirements-ai.txt
   ```
3. Check logs in GUI for specific error

### "pip not found"
- Ensure Python is in PATH
- Try: `python -m pip install -r requirements-ai.txt`

### Installation Timeout
- Slow internet connection
- Use manual method with longer timeout
- Or download PyTorch separately from pytorch.org

### Out of Disk Space
- AI needs ~500MB free space
- Free up space and try again
- Or use classical methods only

---

## 📝 Files

Installation-related files in the project:

```
requirements.txt          - Core dependencies
requirements-ai.txt       - AI dependencies
install_dependencies.bat  - Windows installer (prompts for AI)
install_dependencies.sh   - Mac/Linux installer (prompts for AI)
install_ai.bat           - Windows AI-only installer
install_ai.sh            - Mac/Linux AI-only installer
```

---

## 🎉 Summary

**Easiest**: Enable AI in GUI → Click "Yes" → Wait → Restart

**Fastest**: `pip install -r requirements.txt requirements-ai.txt`

**Most Control**: Manual installation with GPU-specific PyTorch

Choose the method that works best for you!
