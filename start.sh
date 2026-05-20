#!/bin/bash
# Quick start script for AURVEXIS AI

set -e

echo "================================"
echo "AURVEXIS AI - Quick Start"
echo "================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python version: $(python3 --version)"
echo ""

# Check if in correct directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found. Please run from project root."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt --quiet

# Check for GROQ API key
echo ""
if [ -z "$GROQ_API_KEY" ] && [ ! -f ".env" ]; then
    echo "⚠️  GROQ_API_KEY not set!"
    echo "   Create .env file with: GROQ_API_KEY=your_key_here"
    echo "   Or set environment variable: export GROQ_API_KEY=your_key_here"
    echo ""
fi

# Validate modules
echo "✓ Validating modules..."
python validate.py

# Run app
echo ""
echo "🚀 Starting AURVEXIS AI..."
echo "   Open your browser to: http://localhost:8501"
echo ""
echo "   Press Ctrl+C to stop"
echo ""

streamlit run app.py
