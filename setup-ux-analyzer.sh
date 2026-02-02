#!/bin/bash
set -e

echo "=================================================="
echo "UX Analyzer - Dependency Installation Script"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo -e "${GREEN}✓${NC} Detected Linux system"
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo -e "${GREEN}✓${NC} Detected macOS system"
    OS="mac"
else
    echo -e "${RED}✗${NC} Unsupported OS: $OSTYPE"
    exit 1
fi

echo ""
echo "Step 1: Installing system dependencies..."
echo "=========================================="

if [[ "$OS" == "linux" ]]; then
    # Check if running with sudo
    if [ "$EUID" -ne 0 ]; then
        echo -e "${YELLOW}Note: System package installation requires sudo${NC}"
        echo "You may be prompted for your password..."
        echo ""
    fi
    
    # Update package list
    echo "Updating package list..."
    sudo apt-get update -qq
    
    # Install system dependencies
    echo "Installing system packages..."
    sudo apt-get install -y \
        python3-full \
        python3-venv \
        python3-pip \
        python3-dev \
        build-essential \
        libopencv-dev \
        python3-opencv \
        libgl1 \
        libglib2.0-0t64 \
        wget
    
    echo -e "${GREEN}✓${NC} System packages installed"
    
elif [[ "$OS" == "mac" ]]; then
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo -e "${RED}✗${NC} Homebrew not found. Please install from https://brew.sh"
        exit 1
    fi
    
    echo "Installing system packages via Homebrew..."
    brew install python opencv
    echo -e "${GREEN}✓${NC} System packages installed"
fi

echo ""
echo "Step 2: Setting up Python virtual environment..."
echo "================================================="

# Remove old venv if exists
if [ -d "ux-analyzer-venv" ]; then
    echo "Removing old virtual environment..."
    rm -rf ux-analyzer-venv
fi

# Create new venv
echo "Creating virtual environment..."
python3 -m venv ux-analyzer-venv

# Activate venv
source ux-analyzer-venv/bin/activate

echo -e "${GREEN}✓${NC} Virtual environment created"

echo ""
echo "Step 3: Installing Python packages..."
echo "======================================"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip -q

# Install packages
echo "Installing opencv-python-headless..."
pip install opencv-python-headless -q

echo "Installing pillow..."
pip install pillow -q

echo "Installing numpy..."
pip install numpy -q

echo "Installing easyocr (this may take a moment)..."
pip install easyocr -q

echo -e "${GREEN}✓${NC} Python packages installed"

echo ""
echo "Step 4: Verifying installation..."
echo "=================================="

# Test imports
python3 << 'PYTHON_TEST'
import sys
errors = []

try:
    import cv2
    print("✓ opencv-python: OK (version: {})".format(cv2.__version__))
except ImportError as e:
    errors.append("opencv-python: FAILED - {}".format(e))

try:
    import PIL
    print("✓ pillow: OK (version: {})".format(PIL.__version__))
except ImportError as e:
    errors.append("pillow: FAILED - {}".format(e))

try:
    import numpy as np
    print("✓ numpy: OK (version: {})".format(np.__version__))
except ImportError as e:
    errors.append("numpy: FAILED - {}".format(e))

try:
    import easyocr
    print("✓ easyocr: OK")
except ImportError as e:
    errors.append("easyocr: FAILED - {}".format(e))

if errors:
    print("\n❌ Installation verification FAILED:")
    for error in errors:
        print("  - " + error)
    sys.exit(1)
else:
    print("\n✅ All dependencies verified successfully!")
PYTHON_TEST

if [ $? -ne 0 ]; then
    echo -e "${RED}✗${NC} Installation verification failed"
    exit 1
fi

echo ""
echo "Step 5: Creating activation script..."
echo "======================================"

# Create activation script
cat > activate-ux-analyzer.sh << 'ACTIVATE_SCRIPT'
#!/bin/bash
# Activation script for UX Analyzer

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/ux-analyzer-venv/bin/activate"

echo "✓ UX Analyzer environment activated"
echo ""
echo "Usage:"
echo "  python ux-analyzer.py <image.png> -o output.json"
echo "  python ux-analyzer.py <image.png> -o output.json -v visualization.png"
echo ""
echo "To deactivate: deactivate"
ACTIVATE_SCRIPT

chmod +x activate-ux-analyzer.sh

echo -e "${GREEN}✓${NC} Activation script created: activate-ux-analyzer.sh"

echo ""
echo "=================================================="
echo "Installation Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Activate the environment:"
echo "   ${GREEN}source activate-ux-analyzer.sh${NC}"
echo ""
echo "2. Run the analyzer:"
echo "   ${GREEN}python ux-analyzer.py \"reference screen.png\" -o analysis.json${NC}"
echo ""
echo "3. With visualization:"
echo "   ${GREEN}python ux-analyzer.py \"reference screen.png\" -o analysis.json -v visual.png${NC}"
echo ""
echo "The virtual environment is located at: ./ux-analyzer-venv"
echo ""
