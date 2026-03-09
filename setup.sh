#!/usr/bin/env bash

set -e

echo "========================================"
echo " ReqForge MCP Dev Kit Setup"
echo "========================================"

# --------------------------------------------------
# Check Python
# --------------------------------------------------

if ! command -v python3 &> /dev/null
then
    echo "❌ Python3 not found."
    echo "Please install Python 3.10+"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# --------------------------------------------------
# Create Virtual Environment
# --------------------------------------------------

if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
else
    echo "ℹ️ Virtual environment already exists"
fi

# Activate venv
source .venv/bin/activate

# --------------------------------------------------
# Upgrade pip
# --------------------------------------------------

echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# --------------------------------------------------
# Install requirements
# --------------------------------------------------

echo "📦 Installing dependencies..."
pip install -r requirements.txt

# --------------------------------------------------
# Create .env if missing
# --------------------------------------------------

if [ ! -f ".env" ]; then

echo "⚙️ Creating .env file..."

cat <<EOF > .env
# ReqForge API Key
REQFORGE_APIM_KEY=your_api_key_here
EOF

echo "⚠️ Please edit the .env file and add your API key."
else
    echo "ℹ️ .env file already exists"
fi

# --------------------------------------------------
# Done
# --------------------------------------------------

echo ""
echo "========================================"
echo " Setup completed"
echo "========================================"
echo ""

echo "Start MCP server with:"
echo ""

echo "source .venv/bin/activate"
echo "uvicorn mcp_server.reqforge_mcp_server:app --reload --port 8000"

echo ""
echo "Test the client:"
echo ""

echo "python examples/python-client.py"
echo ""