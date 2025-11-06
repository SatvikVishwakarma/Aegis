# Aegis Agent - Endpoint Installer
# Generated for Group: {{GROUP}}
# Run this script as Administrator on the endpoint machine

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Aegis Agent - Installation" -ForegroundColor Cyan
Write-Host "Group: {{GROUP}}" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Please right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$exePath = Join-Path $scriptPath "AegisAgent.exe"

if (-not (Test-Path $exePath)) {
    Write-Host "ERROR: AegisAgent.exe not found!" -ForegroundColor Red
    exit 1
}

Write-Host "Found: $exePath" -ForegroundColor Green
Write-Host ""

# Offer options
Write-Host "Installation Options:" -ForegroundColor Yellow
Write-Host "  1. Install as Windows Service (Recommended - Auto-start on boot)"
Write-Host "  2. Run as Console Application (Testing - Manual start)"
Write-Host ""
$choice = Read-Host "Select option (1 or 2)"

if ($choice -eq "1") {
    Write-Host ""
    Write-Host "Installing as Windows Service..." -ForegroundColor Cyan
    
    $serviceName = "AegisAgent"
    $existingService = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
    
    if ($existingService) {
        Write-Host "Service already exists. Stopping and removing..." -ForegroundColor Yellow
        if ($existingService.Status -eq 'Running') {
            Stop-Service -Name $serviceName -Force
        }
        sc.exe delete $serviceName
        Start-Sleep -Seconds 2
    }
    
    sc.exe create $serviceName binPath= "$exePath" start= auto DisplayName= "Aegis Security Monitoring Agent"
    sc.exe description $serviceName "Monitors system events and enforces security policies"
    sc.exe failure $serviceName reset= 86400 actions= restart/60000/restart/60000/restart/60000
    
    Write-Host "Starting service..." -ForegroundColor Cyan
    Start-Service -Name $serviceName
    
    $service = Get-Service -Name $serviceName
    if ($service.Status -eq 'Running') {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "Installation Successful!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Service Status: Running" -ForegroundColor White
        Write-Host "Service Name: $serviceName" -ForegroundColor White
        Write-Host "Group: {{GROUP}}" -ForegroundColor White
        Write-Host "Server: {{SERVER_URL}}" -ForegroundColor White
        Write-Host ""
        Write-Host "Management Commands:" -ForegroundColor Cyan
        Write-Host "  Start:   Start-Service -Name $serviceName" -ForegroundColor Gray
        Write-Host "  Stop:    Stop-Service -Name $serviceName" -ForegroundColor Gray
        Write-Host "  Restart: Restart-Service -Name $serviceName" -ForegroundColor Gray
        Write-Host "  Status:  Get-Service -Name $serviceName" -ForegroundColor Gray
    } else {
        Write-Host "WARNING: Service created but not running!" -ForegroundColor Yellow
        Write-Host "Check Event Viewer for errors." -ForegroundColor Yellow
    }
    
} elseif ($choice -eq "2") {
    Write-Host ""
    Write-Host "Starting agent in console mode..." -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to stop the agent." -ForegroundColor Yellow
    Write-Host ""
    & $exePath
    
} else {
    Write-Host "Invalid choice. Exiting." -ForegroundColor Red
    exit 1
}
