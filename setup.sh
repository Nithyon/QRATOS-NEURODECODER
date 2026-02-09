#!/bin/bash
# Setup script for QRATOS-NEURODECODER
# Installs all dependencies for quantum EEG analysis

set -e  # Exit on error

echo "================================================================"
echo "           QRATOS-NEURODECODER Setup Script"
echo "        Kipu Quantum-Inspired EEG Analysis Platform"
echo "================================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
echo "→ Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓${NC} Python found: $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Node.js is installed
echo "→ Checking Node.js installation..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓${NC} Node.js found: $NODE_VERSION"
else
    echo -e "${YELLOW}⚠${NC} Node.js not found. Frontend setup will be skipped."
fi

# Check if pip is installed
echo "→ Checking pip installation..."
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version)
    echo -e "${GREEN}✓${NC} pip found: $PIP_VERSION"
else
    echo -e "${RED}✗${NC} pip not found. Please install pip."
    exit 1
fi

echo ""
echo "================================================================"
echo "Installing Python Dependencies"
echo "================================================================"
echo ""

# Upgrade pip
echo "→ Upgrading pip..."
pip3 install --upgrade pip

# Install quantum computing libraries
echo ""
echo "→ Installing quantum computing libraries (Qiskit)..."
pip3 install qiskit qiskit-aer qiskit-ibmq-provider || {
    echo -e "${YELLOW}⚠${NC} Warning: Qiskit installation failed. Some features may not work."
}

echo ""
echo "→ Installing PennyLane (quantum ML)..."
pip3 install pennylane pennylane-qiskit || {
    echo -e "${YELLOW}⚠${NC} Warning: PennyLane installation failed. ML features may be limited."
}

# Install scientific computing libraries
echo ""
echo "→ Installing scientific computing libraries..."
pip3 install numpy scipy pandas matplotlib seaborn || {
    echo -e "${RED}✗${NC} Failed to install scientific libraries."
    exit 1
}

# Install EEG processing libraries
echo ""
echo "→ Installing EEG processing libraries..."
pip3 install mne pyedflib || {
    echo -e "${YELLOW}⚠${NC} Warning: MNE installation failed. Real EEG data processing may be limited."
}

# Install machine learning libraries
echo ""
echo "→ Installing machine learning libraries..."
pip3 install scikit-learn || {
    echo -e "${YELLOW}⚠${NC} Warning: scikit-learn installation failed."
}

# Install API dependencies
echo ""
echo "→ Installing API dependencies (Flask)..."
pip3 install flask flask-cors || {
    echo -e "${RED}✗${NC} Failed to install Flask."
    exit 1
}

# Install from requirements.txt if it exists
if [ -f "requirements.txt" ]; then
    echo ""
    echo "→ Installing remaining dependencies from requirements.txt..."
    pip3 install -r requirements.txt || {
        echo -e "${YELLOW}⚠${NC} Some dependencies from requirements.txt failed to install."
    }
fi

# Setup Node.js dependencies if Node is available
if command -v node &> /dev/null && [ -d "qratos" ]; then
    echo ""
    echo "================================================================"
    echo "Installing Node.js Dependencies"
    echo "================================================================"
    echo ""
    
    cd qratos
    
    if [ -f "package.json" ]; then
        echo "→ Installing npm packages..."
        npm install || {
            echo -e "${YELLOW}⚠${NC} npm install failed. Frontend may not work."
        }
    else
        echo -e "${YELLOW}⚠${NC} package.json not found in qratos directory"
    fi
    
    cd ..
fi

echo ""
echo "================================================================"
echo "Verifying Installation"
echo "================================================================"
echo ""

# Test imports
echo "→ Testing Python imports..."

python3 << EOF
import sys
errors = []

try:
    import numpy
    print("✓ NumPy")
except ImportError:
    errors.append("NumPy")
    print("✗ NumPy")

try:
    import scipy
    print("✓ SciPy")
except ImportError:
    errors.append("SciPy")
    print("✗ SciPy")

try:
    import qiskit
    print("✓ Qiskit")
except ImportError:
    errors.append("Qiskit")
    print("✗ Qiskit (quantum features will not work)")

try:
    import flask
    print("✓ Flask")
except ImportError:
    errors.append("Flask")
    print("✗ Flask")

try:
    import matplotlib
    print("✓ Matplotlib")
except ImportError:
    errors.append("Matplotlib")
    print("✗ Matplotlib")

if errors:
    print(f"\n⚠ Some imports failed: {', '.join(errors)}")
    sys.exit(1)
else:
    print("\n✓ All critical imports successful!")
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "================================================================"
    echo -e "${GREEN}✓ Installation Completed Successfully!${NC}"
    echo "================================================================"
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. Test the quantum circuits:"
    echo "   python3 quantum_backend/circuits/__init__.py"
    echo ""
    echo "2. Test EEG processing:"
    echo "   python3 quantum_backend/eeg_processing/__init__.py"
    echo ""
    echo "3. Run quick start examples:"
    echo "   python3 examples/quick_start.py"
    echo ""
    echo "4. Run complete demo:"
    echo "   python3 examples/complete_demo.py"
    echo ""
    echo "5. Start the API server:"
    echo "   python3 quantum_backend/api/__init__.py"
    echo ""
    echo "6. Start the frontend (if Node.js is installed):"
    echo "   cd qratos && npm run dev"
    echo ""
    echo "For more information, see README.md"
    echo "================================================================"
else
    echo ""
    echo "================================================================"
    echo -e "${RED}✗ Installation completed with errors${NC}"
    echo "================================================================"
    echo "Please check the error messages above and install missing dependencies manually."
    exit 1
fi
