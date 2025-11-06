#!/bin/bash

# OmniScope AI Startup Script
# This script starts both the Next.js frontend and Python backend

echo "🚀 Starting OmniScope AI Platform..."

# Activate virtual environment and check if Python dependencies are installed
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

if ! python -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Start Python backend in background
echo "🐍 Starting Python backend on port 8000..."
python main.py &
PYTHON_PID=$!

# Wait a moment for Python backend to start
sleep 3

# Start Next.js frontend
echo "⚛️ Starting Next.js frontend on port 3000..."
npm run dev &
NEXTJS_PID=$!

echo "✅ OmniScope AI is starting up..."
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8001"
echo "📚 API Docs: http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop both services"

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Stopping OmniScope AI..."
    kill $PYTHON_PID 2>/dev/null
    kill $NEXTJS_PID 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for both processes
wait