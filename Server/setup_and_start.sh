#!/bin/bash

# Aegis Server Setup and Start Script
# This script creates a virtual environment, installs dependencies, and starts the server

set -e  # Exit on any error

echo "=========================================="
echo "Aegis Server Setup and Start"
echo "=========================================="
echo ""

# Step 1: Create .env file with secure keys if it doesn't exist
if [ ! -f .env ]; then
    echo "[Step 1/6] Creating .env file with secure random keys..."
    
    # Generate secure random keys
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    AGENT_API_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    
    # Create .env file
    cat > .env << EOF
# Aegis Server Environment Variables
# Generated on $(date)

# JWT Secret Key - DO NOT SHARE
SECRET_KEY=$SECRET_KEY

# JWT Algorithm
ALGORITHM=HS256

# Access token expiration time in minutes
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Agent/Node API Key - DO NOT SHARE
AGENT_API_KEY=$AGENT_API_KEY

# Database URL
DATABASE_URL=sqlite+aiosqlite:///./aegis.db
EOF
    
    echo "✓ .env file created with secure random keys"
    echo "  SECRET_KEY: $SECRET_KEY"
    echo "  AGENT_API_KEY: $AGENT_API_KEY"
    echo ""
else
    echo "[Step 1/6] .env file already exists, skipping..."
    echo ""
fi

# Step 2: Create virtual environment
echo "[Step 2/6] Creating virtual environment 'aegis'..."
python3 -m venv aegis
echo "✓ Virtual environment created successfully"
echo ""

# Step 3: Activate virtual environment and install dependencies
echo "[Step 3/6] Installing dependencies from requirments.txt..."
source aegis/bin/activate
pip install --upgrade pip
pip install -r requirments.txt
echo "✓ Dependencies installed successfully"
echo ""

# Step 4: Show installed packages
echo "[Step 4/6] Installed packages:"
pip list
echo ""

# Step 5: Initialize database
echo "[Step 5/6] Initializing database..."
python init_db.py
echo ""

# Step 6: Start the server
echo "[Step 6/6] Starting Aegis server on port 8000..."
echo "=========================================="
echo "Server will be available at:"
echo "  - API: http://localhost:8000"
echo "  - Docs: http://localhost:8000/docs"
echo "  - Health: http://localhost:8000/health"
echo "=========================================="
echo ""

uvicorn app:app --host 0.0.0.0 --port 8000 --reload
