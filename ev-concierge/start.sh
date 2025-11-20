#!/bin/bash

echo "🚗 EV Concierge - Quick Start"
echo "=============================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
bash install_deps.sh

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your AWS credentials if needed"
fi

# Check AWS credentials
echo "🔐 Checking AWS credentials..."
if aws sts get-caller-identity &> /dev/null; then
    echo "✅ AWS credentials configured"
else
    echo "⚠️  AWS credentials not found. Run 'aws configure' or set environment variables."
fi

echo ""
echo "🚀 Starting EV Concierge..."
echo "📱 Access the UI at: http://localhost:8501"
echo ""

streamlit run app_streamlit.py --server.port=8501 --server.address=0.0.0.0
