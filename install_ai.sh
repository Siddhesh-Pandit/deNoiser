#!/bin/bash
# Unix/Linux/Mac shell script to install AI dependencies

echo "============================================================"
echo "Image Denoiser - AI Dependencies Installer (Unix/Linux/Mac)"
echo "============================================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed or not in PATH"
    echo ""
    echo "Please install Python 3.7 or higher"
    echo ""
    exit 1
fi

echo "This will install PyTorch for AI denoising (~500MB download)."
echo ""
read -p "Continue? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    exit 0
fi

echo ""
echo "Installing AI dependencies..."
echo "This may take several minutes..."
echo ""

python3 -m pip install -r requirements-ai.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================================"
    echo "AI dependencies installed successfully!"
    echo "============================================================"
    echo ""
    echo "You can now use AI denoising in the GUI."
    echo "Enable it in the 'AI Denoiser' section."
    echo ""
else
    echo ""
    echo "============================================================"
    echo "Installation failed!"
    echo "============================================================"
    echo ""
    echo "Please try manually:"
    echo "  pip install -r requirements-ai.txt"
    echo ""
fi

read -p "Press Enter to continue..."
