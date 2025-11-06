#!/bin/bash

# Aegis Dashboard Setup and Start Script
# This script installs dependencies and starts the Next.js dashboard

set -e  # Exit on any error

echo "=========================================="
echo "Aegis Dashboard Setup and Start"
echo "=========================================="
echo ""

# Step 1: Create .env.local if it doesn't exist
if [ ! -f .env.local ]; then
    echo "[Step 1/5] Creating .env.local file..."
    
    # Prompt for server URL
    echo ""
    read -p "Enter your Aegis Server URL (e.g., http://12.10.9.219:8000): " SERVER_URL
    
    # Default to localhost if empty
    if [ -z "$SERVER_URL" ]; then
        SERVER_URL="http://localhost:8000"
        echo "Using default: $SERVER_URL"
    fi
    
    # Remove trailing slash if present
    SERVER_URL="${SERVER_URL%/}"
    
    # Extract WebSocket URL properly
    if [[ $SERVER_URL == https://* ]]; then
        # For HTTPS, use WSS
        WS_URL="${SERVER_URL/https:/wss:}/ws"
    else
        # For HTTP, use WS
        WS_URL="${SERVER_URL/http:/ws:}/ws"
    fi
    
    # Create .env.local file
    cat > .env.local << EOF
# Aegis Dashboard Environment Variables
# Generated on $(date)

# Backend API URL
NEXT_PUBLIC_API_URL=$SERVER_URL

# WebSocket URL
NEXT_PUBLIC_WS_URL=$WS_URL
EOF
    
    echo "✓ .env.local file created"
    echo "  API URL: $SERVER_URL"
    echo "  WebSocket URL: $WS_URL"
    echo ""
else
    echo "[Step 1/5] .env.local file already exists, skipping..."
    echo "  Current API URL: $(grep NEXT_PUBLIC_API_URL .env.local | cut -d '=' -f2)"
    echo ""
fi

# Step 2: Check if Node.js is installed
echo "[Step 2/5] Checking Node.js installation..."
if ! command -v node &> /dev/null
then
    echo "❌ Error: Node.js is not installed"
    echo "Please install Node.js 18 or higher from https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node --version)
echo "✓ Node.js $NODE_VERSION found"
echo ""

# Step 3: Install dependencies
echo "[Step 3/5] Installing dependencies from package.json..."
npm install
echo "✓ Dependencies installed successfully"
echo ""

# Step 4: Show installed packages
echo "[Step 4/5] Installed packages summary:"
npm list --depth=0
echo ""

# Step 5: Start the dashboard
echo "[Step 5/5] Starting Aegis dashboard on port 3000..."
echo ""
echo "=========================================="
echo "Dashboard started successfully!"
echo "=========================================="
echo "  - Dashboard: http://localhost:3000"
echo "  - Make sure the backend server is running on port 8000"
echo "  - Login with the user account you created during server setup"
echo "=========================================="
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

npm run dev
