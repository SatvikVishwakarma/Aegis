#!/bin/bash

echo "========================================"
echo "  Aegis Security Dashboard"
echo "  Setup Script"
echo "========================================"
echo ""

echo "[1/3] Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python not found! Please install Python 3.9+"
    exit 1
fi
python3 --version
echo "✓ Python found"
echo ""

echo "[2/3] Installing Backend Dependencies..."
cd Server
pip3 install -r ../requirments.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install Python dependencies"
    exit 1
fi
cd ..
echo "✓ Backend dependencies installed"
echo ""

echo "[3/3] Installing Frontend Dependencies..."
cd Dashboard
npm install
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install Node.js dependencies"
    exit 1
fi
cd ..
echo "✓ Frontend dependencies installed"
echo ""

echo "========================================"
echo "  Setup Complete! 🎉"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Run: ./start.sh"
echo "  2. Open: http://localhost:3000"
echo "  3. Login: admin / password123"
echo ""
echo "Or run manually:"
echo "  Terminal 1: cd Server && uvicorn app:app --reload"
echo "  Terminal 2: cd Dashboard && npm run dev"
echo ""
