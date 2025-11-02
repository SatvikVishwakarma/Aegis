#!/bin/bash

echo "====================================="
echo "  Aegis Security Dashboard"
echo "  Starting Backend and Frontend..."
echo "====================================="
echo ""

# Start Backend in background
echo "Starting FastAPI Backend..."
cd Server
uvicorn app:app --reload &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start Frontend
echo "Starting Next.js Frontend..."
cd Dashboard
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "====================================="
echo "  Aegis Dashboard is running!"
echo "====================================="
echo ""
echo "Backend API: http://localhost:8000"
echo "API Docs:    http://localhost:8000/docs"
echo "Frontend:    http://localhost:3000"
echo ""
echo "Login with: admin / password123"
echo ""
echo "Press Ctrl+C to stop all services"
echo "====================================="

# Trap Ctrl+C and kill both processes
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT

# Wait for both processes
wait
