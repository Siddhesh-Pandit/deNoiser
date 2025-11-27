#!/bin/bash
# Unix/Linux/Mac shell script to install dependencies

echo "============================================================"
echo "Image Denoiser - Dependency Installer (Unix/Linux/Mac)"
echo "============================================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed or not in PATH"
    echo ""
    echo "Please install Python 3.7 or higher:"
    echo ""
    echo "  macOS (using Homebrew):"
    echo "    brew install python3"
    echo ""
    echo "  Ubuntu/Debian:"
    echo "    sudo apt-get update"
    echo "    sudo apt-get install python3 python3-pip"
    echo ""
    echo "  Fedora/RHEL:"
    echo "    sudo dnf install python3 python3-pip"
    echo ""
    echo "Or download from: https://www.python.org/downloads/"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo "Checking Python version..."
python3 --version
echo ""

python3 install_dependencies.py

echo ""
read -p "Press Enter to continue..."
