#!/bin/bash

# Agentic AI Project Setup Script
# This script automates the initial setup of the project

echo "╔══════════════════════════════════════════════════════════╗"
echo "║        Agentic AI Project - Setup Script                ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "🔍 Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    exit 1
fi
echo "✅ Python 3 is installed"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists, skipping..."
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip
echo "✅ Pip upgraded"
echo ""

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to install dependencies"
    exit 1
fi
echo "✅ Dependencies installed"
echo ""

# Setup .env file
echo "⚙️  Setting up environment file..."
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists, skipping..."
else
    cp .env.example .env
    echo "✅ Created .env file from template"
    echo "⚠️  IMPORTANT: Edit .env and add your API keys!"
fi
echo ""

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p data
mkdir -p memory_data
echo "✅ Directories created"
echo ""

# Run tests
echo "🧪 Running tests..."
pytest tests/ -v
if [ $? -ne 0 ]; then
    echo "⚠️  Some tests failed, but setup is complete"
else
    echo "✅ All tests passed!"
fi
echo ""

# Display success message
echo "╔══════════════════════════════════════════════════════════╗"
echo "║            🎉 Setup Complete! 🎉                         ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your API keys"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Run examples: python examples/basic_usage.py"
echo "4. Or use CLI: python main.py --agent research --task 'Your task'"
echo ""
echo "📚 See QUICKSTART.md for detailed usage instructions"
echo "📖 See docs/DOCUMENTATION.md for comprehensive documentation"
echo ""
