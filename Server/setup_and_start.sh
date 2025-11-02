#!/bin/bash

# Aegis Server Setup and Start Script
# This script creates a virtual environment, installs dependencies, and starts the server

set -e  # Exit on any error

echo "=========================================="
echo "Aegis Server Setup and Start"
echo "=========================================="
echo ""

# Step 1: Create virtual environment
echo "[Step 1/4] Creating virtual environment 'aegis'..."
python3 -m venv aegis
echo "✓ Virtual environment created successfully"
echo ""

# Step 2: Activate virtual environment and install dependencies
echo "[Step 2/4] Installing dependencies from requirments.txt..."
source aegis/bin/activate
pip install --upgrade pip
pip install -r ../requirments.txt
echo "✓ Dependencies installed successfully"
echo ""

# Step 3: Show installed packages
echo "[Step 3/4] Installed packages:"
pip list
echo ""

# Step 4: Start the server
echo "[Step 4/4] Starting Aegis server on port 8000..."
echo "=========================================="
echo "Server will be available at:"
echo "  - API: http://localhost:8000"
echo "  - Docs: http://localhost:8000/docs"
echo "  - Health: http://localhost:8000/health"
echo "=========================================="
echo ""

uvicorn app:app --host 0.0.0.0 --port 8000 --reload
