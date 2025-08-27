#!/bin/bash

echo "🚀 Starting JD Parser Agent Testing Interface..."
echo "📁 Project: Agentic AI CV Analysis"
echo "🤖 Agent: Job Description Parser"
echo ""

# Check if we're in the right directory
if [ ! -f "agents/jd_parser/test_interface.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "Current directory: $(pwd)"
    exit 1
fi

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Install requirements if needed
echo "📦 Installing dependencies..."
cd agents/jd_parser

if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found"
    exit 1
fi

pip3 install -r requirements.txt -q

echo "✅ Dependencies installed"
echo ""

# Start the testing interface
echo "🌐 Launching web interface at http://localhost:5000"
echo "💡 Use Ctrl+C to stop the server"
echo ""

python3 test_interface.py