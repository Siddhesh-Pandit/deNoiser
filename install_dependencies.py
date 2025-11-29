"""Dependency installer for Image Denoiser."""
import subprocess
import sys
import os


def check_pip():
    """Check if pip is available."""
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False


def get_python_version():
    """Get Python version as tuple (major, minor)."""
    return (sys.version_info.major, sys.version_info.minor)


def install_dependencies():
    """Install required dependencies from requirements.txt."""
    print("=" * 60)
    print("Image Denoiser - Dependency Installer")
    print("=" * 60)
    print()
    
    # Show Python version
    py_version = get_python_version()
    print(f"Python version: {sys.version.split()[0]}")
    print()
    
    # Check if pip is available
    if not check_pip():
        print("❌ Error: pip is not installed or not accessible.")
        print("Please install pip first: https://pip.pypa.io/en/stable/installation/")
        return False
    
    print("✓ pip is available")
    print()
    
    # Check if requirements files exist
    if not os.path.exists('requirements-core.txt'):
        print("❌ Error: requirements-core.txt not found")
        print("Please make sure you're running this script from the project directory.")
        return False
    
    # Install core dependencies
    print("Installing core dependencies...")
    print("-" * 60)
    print()
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements-core.txt"],
            check=True
        )
        print()
        print("✓ Core dependencies installed successfully!")
        print()
    except subprocess.CalledProcessError as e:
        print()
        print("❌ Core installation failed!")
        print(f"Error: {e}")
        print()
        print("Try installing manually:")
        print("  pip install numpy scikit-image scipy pillow")
        print()
        return False
    
    # Try to install RAW support (optional)
    print("-" * 60)
    print("Installing RAW format support (optional)...")
    print()
    
    # Check Python version compatibility for rawpy
    if py_version >= (3, 14):
        print("⚠ Python 3.14+ detected - rawpy may not be available yet")
        print("  RAW format support will be skipped")
        print("  You can try installing it manually later:")
        print("    pip install rawpy")
        print()
    else:
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements-raw.txt"],
                check=True,
                capture_output=True
            )
            print("✓ RAW support (rawpy) installed successfully!")
            print()
        except subprocess.CalledProcessError:
            print("⚠ RAW support (rawpy) installation failed")
            print("  This is optional - the tool will work without it")
            print("  RAW formats (.nef, .cr2, etc.) won't be supported")
            print()
            print("  You can try installing it manually later:")
            print("    pip install rawpy")
            print()
    
    print("-" * 60)
    print("✓ Core installation complete!")
    print()
    
    # Ask about AI dependencies
    print("=" * 60)
    print("Optional: AI Denoising Support")
    print("=" * 60)
    print()
    print("AI denoising provides better quality but requires PyTorch (~500MB).")
    print()
    
    try:
        response = input("Install AI dependencies? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            print()
            print("Installing AI dependencies (PyTorch)...")
            print("This may take several minutes...")
            print()
            
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-r", "requirements-ai.txt"],
                    check=True
                )
                print()
                print("✓ AI dependencies installed successfully!")
                print()
            except subprocess.CalledProcessError:
                print()
                print("⚠ AI installation failed")
                print("  You can install it later with:")
                print("    pip install -r requirements-ai.txt")
                print()
        else:
            print()
            print("Skipping AI dependencies.")
            print("You can install them later with:")
            print("  pip install -r requirements-ai.txt")
            print()
    except (KeyboardInterrupt, EOFError):
        print()
        print("Skipping AI dependencies.")
        print()
    
    print("-" * 60)
    print("✓ Installation complete!")
    print()
    print("You can now run the denoiser:")
    print("  python denoiserBatch.py  (command line)")
    print("  python gui.py            (graphical interface)")
    print()
    return True


def verify_installation():
    """Verify that all required packages are importable."""
    print("=" * 60)
    print("Verifying installation...")
    print()
    
    packages = {
        'numpy': 'NumPy',
        'skimage': 'scikit-image',
        'scipy': 'SciPy',
        'PIL': 'Pillow'
    }
    
    optional_packages = {
        'rawpy': 'rawpy (RAW format support)'
    }
    
    # Check core packages
    print("Core packages:")
    all_ok = True
    for module, name in packages.items():
        try:
            __import__(module)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ❌ {name} - Not found")
            all_ok = False
    
    print()
    
    # Check optional packages
    print("Optional packages:")
    for module, name in optional_packages.items():
        try:
            __import__(module)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ⚠ {name} - Not installed (RAW formats not supported)")
    
    print()
    return all_ok


if __name__ == "__main__":
    success = install_dependencies()
    
    if success:
        if verify_installation():
            print("=" * 60)
            print("✓ Installation verified - Ready to use!")
            print("=" * 60)
        else:
            print("=" * 60)
            print("⚠ Some core packages could not be imported")
            print("Try restarting your terminal/IDE")
            print("=" * 60)
    else:
        sys.exit(1)
