#!/bin/bash
set -e

echo "=== OpenBB Local Development Setup ==="

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Python version: $PYTHON_VERSION"

if [[ "$PYTHON_VERSION" < "3.10" ]]; then
    echo "Warning: Python 3.10+ is recommended for OpenBB"
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install OpenBB
echo "Installing OpenBB Platform..."
pip install openbb openbb-cli

# Install additional data providers (uncomment as needed)
# pip install openbb-fmp openbb-polygon openbb-fred

# Create local config directory
mkdir -p ~/.openbb_platform

# Copy default settings if not exists
if [ ! -f ~/.openbb_platform/user_settings.json ]; then
    cp config/user_settings.json ~/.openbb_platform/
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Get your PAT from https://my.openbb.co and set it:"
echo "   export OPENBB_PAT=your_token_here"
echo "3. Start the API server:"
echo "   python -c \"from openbb import obb; obb.account.login(); import uvicorn; uvicorn.run('openbb_core.api.rest_api:app', host='0.0.0.0', port=6900)\""
echo ""
echo "Or use Docker: cd docker && docker-compose up -d"
