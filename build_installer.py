"""Build script for creating Windows installer."""
import PyInstaller.__main__
import os
import sys

# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))

# PyInstaller arguments
args = [
    'gui.py',  # Main script
    '--name=ImageDenoiser',  # Name of the executable
    '--onefile',  # Create a single executable
    '--windowed',  # No console window (GUI app)
    '--icon=icon.ico',  # Application icon (if available)
    '--add-data=config.ini;.',  # Include config file
    '--add-data=README.md;.',  # Include README
    '--add-data=USAGE.md;.',  # Include usage guide
    '--hidden-import=skimage.restoration',
    '--hidden-import=skimage.metrics',
    '--hidden-import=scipy.ndimage',
    '--hidden-import=pywt',
    '--hidden-import=rawpy',
    '--collect-all=skimage',
    '--collect-all=scipy',
    '--collect-all=pywt',
    '--noconfirm',  # Overwrite without asking
]

print("Building Windows installer...")
print("This may take a few minutes...")
print()

try:
    PyInstaller.__main__.run(args)
    print()
    print("=" * 60)
    print("Build complete!")
    print("Executable location: dist/ImageDenoiser.exe")
    print("=" * 60)
except Exception as e:
    print(f"Build failed: {e}")
    sys.exit(1)
