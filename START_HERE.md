# START HERE - Image Denoiser

**Everything a basic user needs to know in one place.**

> **Note:** No pre-built executables available yet. Installation takes ~5 minutes.
> 
> **Future:** Once releases are available, you'll be able to just download and run an .exe (Windows), .app (Mac), or AppImage (Linux) with no setup needed.

---

## Step 1: Get the App Running

### Windows:

1. **Install Python 3.12**
   - Download from [python.org/downloads](https://www.python.org/downloads/)
   - Run installer
   - ✅ **CHECK "Add Python to PATH"** (important!)
   - Click "Install Now"

2. **Download this project**
   - Click the green "Code" button at the top of this page
   - Select "Download ZIP"
   - Extract the ZIP to a folder (e.g., Desktop or Documents)

3. **Install dependencies**
   - Open the extracted folder
   - Double-click `install_dependencies.bat`
   - Wait for "Installation complete!"

4. **Run the app**
   - Double-click `run_gui.bat`
   - The app window will open ✅

### Mac/Linux:

1. **Install Python 3.12**
   - Mac: Download from [python.org](https://www.python.org/downloads/) or use `brew install python@3.12`
   - Linux: Use your package manager (e.g., `sudo apt install python3.12`)

2. **Download this project**
   - Click the green "Code" button → Download ZIP
   - Extract to a folder

3. **Install dependencies**
   - Open Terminal in the project folder
   - Run: `chmod +x install_dependencies.sh`
   - Run: `./install_dependencies.sh`

4. **Run the app**
   - Run: `chmod +x run_gui.sh`
   - Run: `./run_gui.sh`
   - The app window will open ✅

---

## Step 2: Use the App

### First Time? Use a Preset:

1. **Click "Folder" or "Files"** → Select your noisy images
2. **Click "Browse..."** → Choose where to save results
3. **Click a preset button:**
   - **📷 Photos** - For portraits, landscapes (best for most photos)
   - **📄 Documents** - For scanned documents, text
   - **🌙 Low-Light** - For night photos, high ISO images
4. **Click "Start Processing"**
5. **Click "🔍 View Comparison"** to see before/after

### That's It!

Your denoised images are saved in the output folder with names like:
- `photo_nonlocal.png` (processed with Non-local Means filter)
- `photo_gaussian.png` (processed with Gaussian filter)
- etc.

---

## Common Questions

**Q: Which preset should I use?**
- Photos of people/places → **📷 Photos**
- Scanned documents → **📄 Documents**  
- Dark/grainy photos → **🌙 Low-Light**
- Not sure? → **📷 Photos** (works for most things)

**Q: Can I adjust settings?**
- Yes! But presets work great for 90% of cases
- If you want to customize, all settings are in the GUI

**Q: What image formats work?**
- JPEG, PNG, TIFF, BMP, GIF (always work)
- RAW formats (NEF, CR2, ARW, etc.) - work if you have Python 3.8-3.13

**Q: How do I know if it worked?**
- Check the log at the bottom of the window
- Click "🔍 View Comparison" to see before/after
- Look in your output folder for the processed images

**Q: It's not working!**
- Check the log for error messages
- Make sure you selected both input and output folders
- Try the "📷 Photos" preset first

---

## Need More Help?

**Having Problems?**
- Windows: See [WINDOWS_INSTALL.md](WINDOWS_INSTALL.md) for detailed troubleshooting
- Other: See [README.md](README.md)

**Want Advanced Features?**
- See [USAGE.md](USAGE.md) for filter tuning, batch processing tips, etc.

**Want to Build Your Own Executable?**
- See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)

---

## Tips for Best Results

1. ✅ **Start with presets** - They're optimized for you
2. ✅ **Test one image first** - Before processing hundreds
3. ✅ **Use PNG output** - Best quality (it's the default)
4. ✅ **Check the comparison** - Make sure you like the result
5. ✅ **Keep originals** - The tool never modifies your original files

---

## That's All You Need!

Most users never need to read anything else. Just:
1. Get the app running (Step 1)
2. Use a preset (Step 2)
3. Done!

The app is designed to work great with zero configuration.
