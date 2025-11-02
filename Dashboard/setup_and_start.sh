#!/bin/bash

# Aegis Dashboard Setup and Start Script
# This script installs dependencies and starts the Next.js dashboard

set -e  # Exit on any error

echo "=========================================="
echo "Aegis Dashboard Setup and Start"
echo "=========================================="
echo ""

# Step 1: Check if Node.js is installed
echo "[Step 1/4] Checking Node.js installation..."
if ! command -v node &> /dev/null
then
    echo "❌ Error: Node.js is not installed"
    echo "Please install Node.js 18 or higher from https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node --version)
echo "✓ Node.js $NODE_VERSION found"
echo ""

# Step 2: Install dependencies
echo "[Step 2/4] Installing dependencies from package.json..."
npm install
echo "✓ Dependencies installed successfully"
echo ""

# Step 3: Show installed packages
echo "[Step 3/4] Installed packages summary:"
npm list --depth=0
echo ""

# Step 4: Start the dashboard
echo "[Step 4/4] Starting Aegis dashboard on port 3000..."
echo "=========================================="
echo "Dashboard will be available at:"
echo "  - URL: http://localhost:3000"
echo "  - Login: admin / password123"
echo "=========================================="
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

npm run dev
