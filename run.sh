#!/bin/bash

# Startup script for LLM Quiz Solver

set -e

echo "🚀 Starting LLM Quiz Solver..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python -m venv venv
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if [ ! -f "venv/bin/playwright" ]; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    echo "🎭 Installing Playwright browsers..."
    playwright install chromium
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found!"
    echo "Please create a .env file based on .env.example"
    echo "Run: cp .env.example .env"
    echo "Then edit .env with your actual credentials"
    exit 1
fi

# Create temp directories
mkdir -p temp downloads

echo "✅ Starting application..."
python app.py
