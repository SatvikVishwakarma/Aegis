# Aegis Server Setup and Start Script (Windows PowerShell)
# This script creates a virtual environment, installs dependencies, and starts the server

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Aegis Server Setup and Start (Windows)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Create .env file with secure keys if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "[Step 1/7] Creating .env file with secure random keys..." -ForegroundColor Yellow
    
    # Generate secure random keys using .NET
    $rng = New-Object System.Security.Cryptography.RNGCryptoServiceProvider
    $secretKeyBytes = New-Object byte[] 32
    $agentKeyBytes = New-Object byte[] 32
    $dashboardKeyBytes = New-Object byte[] 32
    $rng.GetBytes($secretKeyBytes)
    $rng.GetBytes($agentKeyBytes)
    $rng.GetBytes($dashboardKeyBytes)
    $SECRET_KEY = [Convert]::ToBase64String($secretKeyBytes)
    $AGENT_API_KEY = [Convert]::ToBase64String($agentKeyBytes)
    $DASHBOARD_API_KEY = [Convert]::ToBase64String($dashboardKeyBytes)
    
    # Create .env file content
    $envLines = @()
    $envLines += "# Aegis Server Environment Variables"
    $envLines += "# Generated on $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    $envLines += ""
    $envLines += "# JWT Secret Key - DO NOT SHARE"
    $envLines += "SECRET_KEY=$SECRET_KEY"
    $envLines += ""
    $envLines += "# JWT Algorithm"
    $envLines += "ALGORITHM=HS256"
    $envLines += ""
    $envLines += "# Access token expiration time in minutes"
    $envLines += "ACCESS_TOKEN_EXPIRE_MINUTES=30"
    $envLines += ""
    $envLines += "# Agent/Node API Key - DO NOT SHARE"
    $envLines += "AGENT_API_KEY=$AGENT_API_KEY"
    $envLines += ""
    $envLines += "# Dashboard API Key (Optional) - Adds extra security layer"
    $envLines += "# If set, dashboard must send this key in X-Dashboard-Key header"
    $envLines += "DASHBOARD_API_KEY=$DASHBOARD_API_KEY"
    $envLines += ""
    $envLines += "# Database URL"
    $envLines += "DATABASE_URL=sqlite+aiosqlite:///./aegis.db"
    
    $envLines | Out-File -FilePath ".env" -Encoding UTF8
    
    Write-Host "? .env file created with secure random keys" -ForegroundColor Green
    Write-Host "  SECRET_KEY: $($SECRET_KEY.Substring(0, 20))..." -ForegroundColor Gray
    Write-Host "  AGENT_API_KEY: $($AGENT_API_KEY.Substring(0, 20))..." -ForegroundColor Gray
    Write-Host "  DASHBOARD_API_KEY: $($DASHBOARD_API_KEY.Substring(0, 20))..." -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "[Step 1/7] .env file already exists, skipping..." -ForegroundColor Gray
    Write-Host ""
}

# Step 2: Create virtual environment
Write-Host "[Step 2/7] Creating virtual environment 'aegis'..." -ForegroundColor Yellow
if (-not (Test-Path "aegis")) {
    python -m venv aegis
    Write-Host "? Virtual environment created successfully" -ForegroundColor Green
} else {
    Write-Host "? Virtual environment already exists" -ForegroundColor Green
}
Write-Host ""

# Step 3: Activate virtual environment and install dependencies
Write-Host "[Step 3/7] Installing dependencies from requirments.txt..." -ForegroundColor Yellow
& ".\aegis\Scripts\Activate.ps1"
python -m pip install --upgrade pip
pip install -r requirments.txt
Write-Host "? Dependencies installed successfully" -ForegroundColor Green
Write-Host ""

# Step 4: Show installed packages
Write-Host "[Step 4/7] Installed packages:" -ForegroundColor Yellow
pip list
Write-Host ""

# Step 5: Initialize database
Write-Host "[Step 5/7] Initializing database..." -ForegroundColor Yellow

# Remove old database if it exists to start fresh
if (Test-Path "aegis.db") {
    Write-Host "  Removing old database file..." -ForegroundColor Gray
    Remove-Item "aegis.db" -Force
}

# Run database_setup.py and capture the admin password
$initOutput = & python database_setup.py 2>&1 | Out-String
Write-Host $initOutput

# Extract the password from output
$passwordMatch = $initOutput | Select-String -Pattern "Password:\s+(\S+)"
if ($passwordMatch) {
    $adminPassword = $passwordMatch.Matches[0].Groups[1].Value
} else {
    $adminPassword = $null
}

# Ensure database has correct permissions (Windows doesn't need chmod)
if (Test-Path "aegis.db") {
    Write-Host "? Database created successfully" -ForegroundColor Green
}

Write-Host ""

# Step 6: User Management (Mandatory)
Write-Host "[Step 6/7] Admin Account Created" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan

if ($adminPassword) {
    Write-Host ""
    Write-Host "?? YOUR ADMIN CREDENTIALS:" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "  Username: admin" -ForegroundColor White
    Write-Host "  Password: $adminPassword" -ForegroundColor Yellow
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "??  IMPORTANT - SAVE THIS PASSWORD NOW!" -ForegroundColor Red
    Write-Host "  - Write it down or save it in a password manager" -ForegroundColor White
    Write-Host "  - You'll need this to:" -ForegroundColor White
    Write-Host "    * Login to the dashboard" -ForegroundColor White
    Write-Host "    * Confirm deletion of nodes and policies" -ForegroundColor White
    Write-Host "  - This password will NOT be shown again!" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter once you have saved the password"
} else {
    Write-Host "Admin user already exists from previous setup" -ForegroundColor Gray
}

Write-Host ""

# Step 7: Start the server
Write-Host "[Step 7/7] Starting Aegis server on port 8000..." -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Server configuration:" -ForegroundColor White
Write-Host "  - Binding to: 0.0.0.0 (accessible from network)" -ForegroundColor White
Write-Host "  - Port: 8000" -ForegroundColor White
Write-Host "" 
Write-Host "Access points:" -ForegroundColor White
Write-Host "  - Dashboard: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  - API: http://localhost:8000/api/v1" -ForegroundColor Cyan
Write-Host "  - Health check: http://localhost:8000/health" -ForegroundColor Cyan
Write-Host "  - Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

uvicorn app:app --host 0.0.0.0 --port 8000 --reload
