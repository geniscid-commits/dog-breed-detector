#!/bin/bash

echo "Starting Dog Breed Detector..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Start Flask server
echo ""
echo "================================================"
echo "Dog Breed Detector Server Started"
echo "================================================"
echo ""
echo "Backend: http://localhost:5000"
echo "Frontend: Open index.html in your browser"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python server.py
