# Aegis Dashboard Setup and Start Script (Windows PowerShell)
# This script installs dependencies and starts the Next.js development server

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Aegis Dashboard Setup and Start (Windows)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if Node.js is installed
Write-Host "[Step 1/5] Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    $npmVersion = npm --version
    Write-Host "[OK] Node.js version: $nodeVersion" -ForegroundColor Green
    Write-Host "[OK] npm version: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Node.js is not installed!" -ForegroundColor Red
    Write-Host "Please install Node.js from: https://nodejs.org/" -ForegroundColor Yellow
    Write-Host "Recommended version: 18.x or higher" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Step 2: Create .env.local file if it doesn't exist
Write-Host "[Step 2/5] Checking environment configuration..." -ForegroundColor Yellow
if (-not (Test-Path ".env.local")) {
    Write-Host "Creating .env.local file..." -ForegroundColor Gray
    
    # Create .env.local file content
    $envLines = @()
    $envLines += "# Aegis Dashboard Environment Variables"
    $envLines += "# Generated on $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    $envLines += ""
    $envLines += "# Backend API URL"
    $envLines += "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1"
    $envLines += ""
    $envLines += "# Optional: Dashboard API Key (must match server's DASHBOARD_API_KEY)"
    $envLines += "# NEXT_PUBLIC_DASHBOARD_API_KEY=your-dashboard-api-key"
    $envLines += ""
    $envLines += "# WebSocket URL"
    $envLines += "NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws"
    
    $envLines | Out-File -FilePath ".env.local" -Encoding UTF8
    Write-Host "[OK] .env.local file created" -ForegroundColor Green
} else {
    Write-Host "[OK] .env.local file already exists" -ForegroundColor Green
}
Write-Host ""

# Step 3: Install dependencies
Write-Host "[Step 3/5] Installing Node.js dependencies..." -ForegroundColor Yellow
if (-not (Test-Path "node_modules")) {
    Write-Host "Running npm install (this may take a few minutes)..." -ForegroundColor Gray
    npm install
    Write-Host "[OK] Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "node_modules exists. Checking for updates..." -ForegroundColor Gray
    npm install
    Write-Host "[OK] Dependencies up to date" -ForegroundColor Green
}
Write-Host ""

# Step 4: Show installed packages info
Write-Host "[Step 4/5] Project information:" -ForegroundColor Yellow
$packageJson = Get-Content "package.json" | ConvertFrom-Json
Write-Host "  Project: $($packageJson.name)" -ForegroundColor White
Write-Host "  Version: $($packageJson.version)" -ForegroundColor White
Write-Host "  Framework: Next.js" -ForegroundColor White
Write-Host ""

# Step 5: Start the development server
Write-Host "[Step 5/5] Starting Aegis Dashboard..." -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Dashboard configuration:" -ForegroundColor White
Write-Host "  - Development server: http://localhost:3000" -ForegroundColor White
Write-Host "  - API endpoint: http://localhost:8000/api/v1" -ForegroundColor White
Write-Host "" 
Write-Host "Features:" -ForegroundColor White
Write-Host "  [OK] Hot Module Replacement (HMR)" -ForegroundColor Green
Write-Host "  [OK] Auto-refresh on file changes" -ForegroundColor Green
Write-Host "  [OK] Dark/Light theme toggle" -ForegroundColor Green
Write-Host "  [OK] Real-time WebSocket updates" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[INFO] Opening browser in a few seconds..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Wait a moment then open browser
Start-Sleep -Seconds 2
Start-Process "http://localhost:3000"

# Start the Next.js dev server
npm run dev
