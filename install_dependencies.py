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


def install_dependencies():
    """Install required dependencies from requirements.txt."""
    print("=" * 60)
    print("Image Denoiser - Dependency Installer")
    print("=" * 60)
    print()
    
    # Check if pip is available
    if not check_pip():
        print("❌ Error: pip is not installed or not accessible.")
        print("Please install pip first: https://pip.pypa.io/en/stable/installation/")
        return False
    
    print("✓ pip is available")
    print()
    
    # Check if requirements.txt exists
    if not os.path.exists('requirements.txt'):
        print("❌ Error: requirements.txt not found")
        print("Please make sure you're running this script from the project directory.")
        return False
    
    print("Installing dependencies from requirements.txt...")
    print("-" * 60)
    print()
    
    try:
        # Install dependencies
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True
        )
        
        print()
        print("-" * 60)
        print("✓ All dependencies installed successfully!")
        print()
        print("You can now run the denoiser:")
        print("  python denoiserBatch.py")
        print()
        return True
        
    except subprocess.CalledProcessError as e:
        print()
        print("-" * 60)
        print("❌ Installation failed!")
        print(f"Error: {e}")
        print()
        print("Try installing manually:")
        print("  pip install numpy scikit-image scipy")
        print()
        return False


def verify_installation():
    """Verify that all required packages are importable."""
    print("Verifying installation...")
    print()
    
    packages = {
        'numpy': 'NumPy',
        'skimage': 'scikit-image',
        'scipy': 'SciPy'
    }
    
    all_ok = True
    for module, name in packages.items():
        try:
            __import__(module)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ❌ {name} - Not found")
            all_ok = False
    
    print()
    return all_ok


if __name__ == "__main__":
    success = install_dependencies()
    
    if success:
        print("=" * 60)
        if verify_installation():
            print("✓ Installation verified - All packages working!")
        else:
            print("⚠ Some packages could not be imported")
            print("Try restarting your terminal/IDE")
        print("=" * 60)
    else:
        sys.exit(1)
