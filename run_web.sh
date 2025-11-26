#!/bin/bash
# Run Babel: The Word Alchemist Web Version

echo "Installing dependencies..."
pip3 install -r requirements.txt --quiet

echo "Starting Flask server..."
echo "Open your browser and go to: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""

python3 app.py
