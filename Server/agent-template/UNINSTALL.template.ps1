# Aegis Agent - Uninstaller
# Run as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Aegis Agent - Uninstallation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    exit 1
}

$serviceName = "AegisAgent"
$service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue

if ($service) {
    Write-Host "Stopping service..." -ForegroundColor Cyan
    if ($service.Status -eq 'Running') {
        Stop-Service -Name $serviceName -Force
    }
    
    Write-Host "Removing service..." -ForegroundColor Cyan
    sc.exe delete $serviceName
    
    Write-Host "Service removed successfully!" -ForegroundColor Green
} else {
    Write-Host "Service not found." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Uninstallation complete." -ForegroundColor Green
