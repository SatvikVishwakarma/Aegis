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
    echo "[Step 1/7] Creating .env file with secure random keys..."
    
    # Generate secure random keys
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    AGENT_API_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    DASHBOARD_API_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    
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

# Dashboard API Key (Optional) - Adds extra security layer
# If set, dashboard must send this key in X-Dashboard-Key header
DASHBOARD_API_KEY=$DASHBOARD_API_KEY

# Database URL
DATABASE_URL=sqlite+aiosqlite:///./aegis.db
EOF
    
    echo "✓ .env file created with secure random keys"
    echo "  SECRET_KEY: ${SECRET_KEY:0:20}..."
    echo "  AGENT_API_KEY: ${AGENT_API_KEY:0:20}..."
    echo "  DASHBOARD_API_KEY: ${DASHBOARD_API_KEY:0:20}..."
    echo ""
else
    echo "[Step 1/7] .env file already exists, skipping..."
    echo ""
fi

# Step 2: Create virtual environment
echo "[Step 2/7] Creating virtual environment 'aegis'..."
python3 -m venv aegis
echo "✓ Virtual environment created successfully"
echo ""

# Step 3: Activate virtual environment and install dependencies
echo "[Step 3/7] Installing dependencies from requirments.txt..."
source aegis/bin/activate
pip install --upgrade pip
pip install -r requirments.txt
echo "✓ Dependencies installed successfully"
echo ""

# Step 4: Show installed packages
echo "[Step 4/7] Installed packages:"
pip list
echo ""

# Step 5: Initialize database
echo "[Step 5/7] Initializing database..."

# Remove old database if it exists to start fresh
if [ -f aegis.db ]; then
    echo "  Removing old database file..."
    rm -f aegis.db
fi

# Run init_db.py and capture the admin password
INIT_OUTPUT=$(python init_db.py)
echo "$INIT_OUTPUT"

# Extract the password from output
ADMIN_PASSWORD=$(echo "$INIT_OUTPUT" | grep "Password:" | awk '{print $2}')

# Ensure database has correct permissions
if [ -f aegis.db ]; then
    chmod 664 aegis.db
    echo "✓ Database permissions set correctly"
fi

echo ""

# Step 6: User Management (Mandatory)
echo "[Step 6/7] Admin Account Created"
echo "=========================================="

if [ -n "$ADMIN_PASSWORD" ]; then
    echo ""
    echo "🔐 YOUR ADMIN CREDENTIALS:"
    echo "=========================================="
    echo "  Username: admin"
    echo "  Password: $ADMIN_PASSWORD"
    echo "=========================================="
    echo ""
    echo "⚠️  IMPORTANT - SAVE THIS PASSWORD NOW!"
    echo "  - Write it down or save it in a password manager"
    echo "  - You'll need this to:"
    echo "    * Login to the dashboard"
    echo "    * Confirm deletion of nodes and policies"
    echo "  - This password will NOT be shown again!"
    echo ""
    read -p "Press Enter once you have saved the password..."
else
    echo "Admin user already exists from previous setup"
fi

echo ""

# Step 7: Start the server
echo "[Step 7/7] Starting Aegis server on port 8000..."
echo "=========================================="
echo "Server configuration:"
echo "  - Binding to: 0.0.0.0 (accessible from network)"
echo "  - Port: 8000"
echo ""
echo "Access points:"
echo "  - Dashboard: http://localhost:3000"
echo "  - API: http://localhost:8000/api/v1"
echo "  - Health check: http://localhost:8000/health"
echo "  - Docs: http://localhost:8000/docs"
echo "=========================================="
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn app:app --host 0.0.0.0 --port 8000 --reload
