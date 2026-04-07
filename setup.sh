#!/usr/bin/env bash
# setup.sh — One-command local environment setup for Quantum Circuit Lab
# Usage: bash setup.sh

set -e

PYTHON=${PYTHON:-python3}
VENV_DIR=".venv"

echo ""
echo "⚛  Quantum Circuit Lab — Setup"
echo "================================"

# Check Python version
PYTHON_VERSION=$($PYTHON -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_MAJOR=$($PYTHON -c "import sys; print(sys.version_info.major)")
PYTHON_MINOR=$($PYTHON -c "import sys; print(sys.version_info.minor)")

echo "→ Python version: $PYTHON_VERSION"

if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]; }; then
    echo "✗ Python 3.10+ is required. Found $PYTHON_VERSION."
    exit 1
fi

# Create virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "→ Creating virtual environment in $VENV_DIR ..."
    $PYTHON -m venv "$VENV_DIR"
else
    echo "→ Virtual environment already exists at $VENV_DIR"
fi

# Activate
source "$VENV_DIR/bin/activate"
echo "→ Activated: $VENV_DIR"

# Upgrade pip
pip install --upgrade pip --quiet

# Install dependencies
echo "→ Installing dependencies ..."
pip install -r requirements.txt --quiet

echo ""
echo "✓ Setup complete."
echo ""
echo "To start the app:"
echo "  source $VENV_DIR/bin/activate"
echo "  streamlit run app.py"
echo ""
echo "To run tests:"
echo "  pip install pytest"
echo "  pytest tests/ -v"
echo ""
