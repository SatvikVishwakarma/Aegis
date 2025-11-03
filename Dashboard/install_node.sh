#!/bin/bash

# Node.js Installation Script for Ubuntu Server
# This script installs Node.js 18.x (LTS) using NodeSource repository

set -e  # Exit on any error

echo "=========================================="
echo "Node.js Installation for Ubuntu Server"
echo "=========================================="
echo ""

# Check if running on Ubuntu/Debian
if ! command -v apt-get &> /dev/null; then
    echo "Error: This script is for Ubuntu/Debian systems only"
    exit 1
fi

# Check if Node.js is already installed
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "Node.js is already installed: $NODE_VERSION"
    read -p "Do you want to reinstall/update? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
fi

echo "[Step 1/5] Updating package list..."
sudo apt-get update

echo ""
echo "[Step 2/5] Installing prerequisites..."
sudo apt-get install -y curl gnupg2 ca-certificates lsb-release ubuntu-keyring

echo ""
echo "[Step 3/5] Adding NodeSource repository for Node.js 18.x (LTS)..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -

echo ""
echo "[Step 4/5] Installing Node.js and npm..."
sudo apt-get install -y nodejs

echo ""
echo "[Step 5/5] Verifying installation..."
NODE_VERSION=$(node --version)
NPM_VERSION=$(npm --version)

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo "Node.js version: $NODE_VERSION"
echo "npm version: $NPM_VERSION"
echo ""
echo "You can now run the dashboard setup script:"
echo "  cd ~/Aegis/Dashboard"
echo "  chmod +x setup_and_start.sh"
echo "  ./setup_and_start.sh"
echo "=========================================="
