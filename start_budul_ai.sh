#!/bin/bash

# Budul AI - Complete System Startup Script
# Starts both backend and frontend for the Islamic AI platform

echo "🚀 Starting Budul AI - Complete Islamic AI Platform"
echo "=================================================="

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Port $1 is already in use"
        return 1
    else
        return 0
    fi
}

# Function to start backend
start_backend() {
    echo "🔧 Starting Budul AI Backend (FastAPI)..."
    
    cd backend
    
    # Install Python dependencies if needed
    if [ ! -d "venv" ]; then
        echo "📦 Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate 2>/dev/null || source venv/Scripts/activate
    
    echo "📦 Installing backend dependencies..."
    pip install -q fastapi uvicorn python-multipart pydantic python-jose[cryptography] passlib[bcrypt] python-dotenv
    
    # Start the Islamic AI backend
    echo "🕌 Launching Islamic AI API on port 8000..."
    python3 -m uvicorn app.api.islamic_ai_endpoints:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    
    echo "✅ Backend started with PID: $BACKEND_PID"
    cd ..
}

# Function to start frontend
start_frontend() {
    echo "🌐 Starting Budul AI Frontend (Next.js)..."
    
    cd frontend
    
    # Install Node.js dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo "📦 Installing frontend dependencies..."
        npm install
    fi
    
    # Start the frontend
    echo "🎨 Launching Islamic AI Interface on port 3000..."
    npm run dev &
    FRONTEND_PID=$!
    
    echo "✅ Frontend started with PID: $FRONTEND_PID"
    cd ..
}

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down Budul AI..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "🔧 Backend stopped"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "🌐 Frontend stopped"
    fi
    echo "👋 Budul AI shutdown complete"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

echo ""
echo "🔍 Checking system requirements..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check if Node.js is available  
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed"
    exit 1
fi

echo "✅ Python 3: $(python3 --version)"
echo "✅ Node.js: $(node --version)"

echo ""
echo "🔍 Checking ports availability..."

# Check if ports are available
if ! check_port 8000; then
    echo "❌ Backend port 8000 is in use. Please stop the service using port 8000"
    exit 1
fi

if ! check_port 3000; then
    echo "❌ Frontend port 3000 is in use. Please stop the service using port 3000"
    exit 1
fi

echo "✅ Ports 8000 and 3000 are available"

echo ""
echo "🚀 Starting services..."

# Start backend
start_backend

# Wait a bit for backend to start
sleep 3

# Start frontend
start_frontend

echo ""
echo "🎉 Budul AI is now running!"
echo "=================================================="
echo "🕌 Islamic AI Backend:  http://localhost:8000"
echo "🌐 Frontend Interface:  http://localhost:3000"
echo "📚 API Documentation:   http://localhost:8000/docs"
echo "📊 API Stats:           http://localhost:8000/api/v1/stats"
echo ""
echo "🤖 Sunni Islamic AI Features Available:"
echo "   • ChatGPT-level Islamic conversations"
echo "   • 3,430+ authentic texts trained"
echo "   • Quran and Hadith search"
echo "   • Prayer times and Qibla direction"
echo "   • Fatwa generation with citations"
echo "   • Madhab-aware responses"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID