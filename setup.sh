#!/bin/bash
# ============================================
# Savage Reply - One-Click Setup Script
# ============================================

set -e

echo ""
echo "🔥 ============================================"
echo "   SAVAGE REPLY - AI Comeback Generator"
echo "   Setup Script"
echo "🔥 ============================================"
echo ""

# Check Python version
echo "📋 Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo "❌ Python not found! Please install Python 3.8+ first."
    exit 1
fi

PY_VERSION=$($PYTHON --version 2>&1 | awk '{print $2}')
echo "✅ Found Python $PY_VERSION"

# Check ffmpeg
echo ""
echo "📋 Checking ffmpeg (required for audio processing)..."
if command -v ffmpeg &> /dev/null; then
    echo "✅ ffmpeg is installed"
else
    echo "⚠️  ffmpeg not found. Installing..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y ffmpeg
    elif command -v brew &> /dev/null; then
        brew install ffmpeg
    elif command -v pacman &> /dev/null; then
        sudo pacman -S ffmpeg
    else
        echo "❌ Could not install ffmpeg automatically."
        echo "   Please install it manually: https://ffmpeg.org/download.html"
        exit 1
    fi
fi

# Create virtual environment
echo ""
echo "📋 Setting up virtual environment..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"

if [ ! -d "$VENV_DIR" ]; then
    $PYTHON -m venv "$VENV_DIR"
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Install dependencies
echo ""
echo "📋 Installing Python dependencies..."
pip install --upgrade pip -q
pip install -r "$SCRIPT_DIR/requirements.txt" -q
echo "✅ Dependencies installed"

# Setup .env file
echo ""
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo "📋 Setting up environment variables..."
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
    echo ""
    echo "⚠️  IMPORTANT: You need a Groq API key (FREE!)"
    echo "   1. Go to: https://console.groq.com"
    echo "   2. Sign up and get your API key"
    echo "   3. Edit the .env file: nano $SCRIPT_DIR/.env"
    echo "   4. Replace 'your_groq_api_key_here' with your actual key"
    echo ""
    read -p "   Enter your Groq API key now (or press Enter to do it later): " API_KEY
    if [ ! -z "$API_KEY" ]; then
        sed -i "s/your_groq_api_key_here/$API_KEY/" "$SCRIPT_DIR/.env"
        echo "   ✅ API key saved!"
    else
        echo "   ⏭️  Skipped. Remember to set it in .env before running!"
    fi
else
    echo "✅ .env file already exists"
fi

# Create audio cache directory
mkdir -p "$SCRIPT_DIR/audio_cache"

echo ""
echo "🎉 ============================================"
echo "   Setup Complete!"
echo "============================================"
echo ""
echo "   To run Savage Reply:"
echo ""
echo "   1. Activate the environment:"
echo "      source $VENV_DIR/bin/activate"
echo ""
echo "   2. Run the app:"
echo "      python $SCRIPT_DIR/app.py"
echo ""
echo "   3. Open on your phone:"
echo "      The app will show a public URL you can"
echo "      open on any device!"
echo ""
echo "🔥 Let's cook some comebacks! 🔥"
echo ""
