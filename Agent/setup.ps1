# Aegis Agent Setup and Build Script (Windows PowerShell)

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Aegis Agent Setup and Build" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if .NET 8.0 SDK is installed
Write-Host "[Step 1/4] Checking .NET 8.0 SDK..." -ForegroundColor Yellow
try {
    $dotnetVersion = dotnet --version
    Write-Host "[OK] .NET SDK version: $dotnetVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] .NET 8.0 SDK is not installed!" -ForegroundColor Red
    Write-Host "Download and install from: https://dotnet.microsoft.com/download/dotnet/8.0" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Restore NuGet packages
Write-Host "[Step 2/4] Restoring NuGet packages..." -ForegroundColor Yellow
dotnet restore
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to restore packages" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Packages restored successfully" -ForegroundColor Green
Write-Host ""

# Build the project
Write-Host "[Step 3/4] Building the agent..." -ForegroundColor Yellow
dotnet build -c Release
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Build failed" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Build completed successfully" -ForegroundColor Green
Write-Host ""

# Check configuration
Write-Host "[Step 4/4] Checking configuration..." -ForegroundColor Yellow
if (Test-Path "appsettings.json") {
    $config = Get-Content "appsettings.json" | ConvertFrom-Json
    $apiKey = $config.Server.ApiKey
    
    if ($apiKey -eq "YOUR_AGENT_API_KEY_FROM_SERVER_ENV") {
        Write-Host "[WARNING] You need to configure the agent!" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Please edit appsettings.json and set:" -ForegroundColor Yellow
        Write-Host "  1. Server.ApiUrl - Your Aegis server URL" -ForegroundColor White
        Write-Host "  2. Server.ApiKey - The AGENT_API_KEY from your server's .env file" -ForegroundColor White
        Write-Host "  3. Node.Group - A group name for this node (optional)" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host "[OK] Configuration looks good" -ForegroundColor Green
        Write-Host "  API URL: $($config.Server.ApiUrl)" -ForegroundColor Gray
        Write-Host "  Group: $($config.Node.Group)" -ForegroundColor Gray
        Write-Host ""
    }
} else {
    Write-Host "[ERROR] appsettings.json not found!" -ForegroundColor Red
    exit 1
}

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To run the agent:" -ForegroundColor White
Write-Host "  dotnet run" -ForegroundColor Cyan
Write-Host ""
Write-Host "Or run the compiled executable:" -ForegroundColor White
Write-Host "  .\bin\Release\net8.0\AegisAgent.exe" -ForegroundColor Cyan
Write-Host ""
Write-Host "[IMPORTANT] The agent must run as Administrator" -ForegroundColor Yellow
Write-Host "            to access Security event logs" -ForegroundColor Yellow
Write-Host ""
