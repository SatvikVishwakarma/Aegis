# Aegis Agent - Package Builder
# This script creates a portable agent package with embedded configuration
# Run this on your BUILD SERVER (not on endpoints)

param(
    [string]$ServerIP = "",
    [string]$ApiKey = "",
    [string]$NodeGroup = "Windows-Default"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Aegis Agent - Package Builder" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get Server IP if not provided
if ([string]::IsNullOrWhiteSpace($ServerIP)) {
    $ServerIP = Read-Host "Enter Aegis Server IP address or hostname (e.g., 192.168.1.100)"
    if ([string]::IsNullOrWhiteSpace($ServerIP)) {
        Write-Host "ERROR: Server IP is required!" -ForegroundColor Red
        exit 1
    }
}

# Get API Key if not provided
if ([string]::IsNullOrWhiteSpace($ApiKey)) {
    $ApiKey = Read-Host "Enter Agent API Key (from server .env file)"
    if ([string]::IsNullOrWhiteSpace($ApiKey)) {
        Write-Host "ERROR: API Key is required!" -ForegroundColor Red
        exit 1
    }
}

# Get Node Group
if ([string]::IsNullOrWhiteSpace($NodeGroup)) {
    $NodeGroup = Read-Host "Enter Node Group name (default: Windows-Default)"
    if ([string]::IsNullOrWhiteSpace($NodeGroup)) {
        $NodeGroup = "Windows-Default"
    }
}

Write-Host ""
Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  Server IP: $ServerIP" -ForegroundColor White
Write-Host "  API Key: $($ApiKey.Substring(0, [Math]::Min(10, $ApiKey.Length)))..." -ForegroundColor White
Write-Host "  Node Group: $NodeGroup" -ForegroundColor White
Write-Host ""

$confirm = Read-Host "Continue with this configuration? (Y/N)"
if ($confirm -ne "Y" -and $confirm -ne "y") {
    Write-Host "Cancelled by user." -ForegroundColor Yellow
    exit 0
}

# Get script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host ""
Write-Host "Step 1: Checking .NET SDK..." -ForegroundColor Cyan
$dotnetVersion = dotnet --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: .NET SDK not found!" -ForegroundColor Red
    Write-Host "Please install .NET 8.0 SDK from: https://dotnet.microsoft.com/download" -ForegroundColor Yellow
    exit 1
}
Write-Host ".NET SDK Version: $dotnetVersion" -ForegroundColor Green

Write-Host ""
Write-Host "Step 2: Restoring NuGet packages..." -ForegroundColor Cyan
dotnet restore
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to restore packages!" -ForegroundColor Red
    exit 1
}
Write-Host "Packages restored successfully." -ForegroundColor Green

Write-Host ""
Write-Host "Step 3: Building agent (Release mode)..." -ForegroundColor Cyan
dotnet build -c Release
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Build failed!" -ForegroundColor Red
    exit 1
}
Write-Host "Build successful." -ForegroundColor Green

Write-Host ""
Write-Host "Step 4: Publishing self-contained package..." -ForegroundColor Cyan
dotnet publish -c Release -r win-x64 --self-contained -o "publish/AegisAgent"
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Publish failed!" -ForegroundColor Red
    exit 1
}
Write-Host "Publish successful." -ForegroundColor Green

# Create appsettings.json with provided configuration
Write-Host ""
Write-Host "Step 5: Generating appsettings.json..." -ForegroundColor Cyan

$appSettings = @{
    Server = @{
        ApiUrl = "http://$ServerIP:8000/api/v1"
        ApiKey = $ApiKey
    }
    Node = @{
        Hostname = "auto"
        IpAddress = "auto"
        Group = $NodeGroup
    }
    Monitoring = @{
        HeartbeatIntervalSeconds = 60
        EventBatchSize = 10
        EventBatchIntervalSeconds = 5
        StatusCheckIntervalSeconds = 30
    }
    Collectors = @{
        ProcessMonitor = @{
            Enabled = $true
            ScanIntervalSeconds = 10
        }
        NetworkMonitor = @{
            Enabled = $true
            ScanIntervalSeconds = 30
        }
        RegistryMonitor = @{
            Enabled = $true
            ScanIntervalSeconds = 60
        }
        ProcessControl = @{
            Enabled = $true
            ScanIntervalSeconds = 5
            Action = "alert"
        }
    }
    Logging = @{
        LogLevel = @{
            Default = "Information"
            Microsoft = "Warning"
        }
    }
}

$appSettingsJson = $appSettings | ConvertTo-Json -Depth 10
$appSettingsJson | Out-File -FilePath "publish/AegisAgent/appsettings.json" -Encoding UTF8
Write-Host "Configuration file created." -ForegroundColor Green

# Create installation script for endpoints
Write-Host ""
Write-Host "Step 6: Creating endpoint installation script..." -ForegroundColor Cyan

$installScript = @'
# Aegis Agent - Endpoint Installer
# Run this script as Administrator on the endpoint machine

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Aegis Agent - Installation" -ForegroundColor Cyan
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
'@

$installScript | Out-File -FilePath "publish/AegisAgent/INSTALL.ps1" -Encoding UTF8
Write-Host "Installation script created." -ForegroundColor Green

# Create uninstallation script
Write-Host ""
Write-Host "Step 7: Creating uninstallation script..." -ForegroundColor Cyan

$uninstallScript = @'
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
'@

$uninstallScript | Out-File -FilePath "publish/AegisAgent/UNINSTALL.ps1" -Encoding UTF8
Write-Host "Uninstallation script created." -ForegroundColor Green

# Create README for endpoints
Write-Host ""
Write-Host "Step 8: Creating deployment README..." -ForegroundColor Cyan

$deployReadme = @"
# Aegis Agent - Deployment Package

## Quick Start

### Installation on Endpoint

1. **Copy this entire folder** to the target Windows machine
2. **Right-click PowerShell** and select "Run as Administrator"
3. **Navigate to this folder** and run:
   ``````powershell
   .\INSTALL.ps1
   ``````
4. **Choose installation type**:
   - Option 1: Windows Service (Recommended - Auto-starts on boot)
   - Option 2: Console Mode (For testing)

### Configuration

This package is pre-configured with:
- **Server**: http://$ServerIP:8000/api/v1
- **Node Group**: $NodeGroup
- **All collectors enabled** (Process, Network, Registry, Process Control)

To modify settings, edit ``appsettings.json`` before running INSTALL.ps1

### Management

#### Service Mode Commands (requires Administrator):
``````powershell
# Check status
Get-Service -Name AegisAgent

# Start service
Start-Service -Name AegisAgent

# Stop service
Stop-Service -Name AegisAgent

# Restart service
Restart-Service -Name AegisAgent
``````

#### Uninstall:
``````powershell
.\UNINSTALL.ps1
``````

### Monitoring

Once installed:
1. Go to Aegis Dashboard
2. Navigate to **Nodes** page
3. Your endpoint should appear as "online"
4. Navigate to **Events** page → Select group → Click on node
5. View real-time events

### Security Features

This agent includes:
- ✅ Process monitoring and control
- ✅ Network connection monitoring
- ✅ Registry change detection
- ✅ Automatic threat response (default: alert mode)

**Process Control is in ALERT mode** - it will only log blacklisted processes.
To enable kill/suspend mode, edit ``appsettings.json`` and change:
``````json
"ProcessControl": {
  "Action": "kill"  // Options: alert, suspend, kill
}
``````

### Troubleshooting

**Service won't start:**
1. Check Event Viewer: ``eventvwr.msc``
2. Look for AegisAgent errors
3. Verify network connectivity to server
4. Check firewall rules

**No events in dashboard:**
1. Verify service is running: ``Get-Service -Name AegisAgent``
2. Check server IP and API key in ``appsettings.json``
3. Test connectivity: ``Test-NetConnection -ComputerName $ServerIP -Port 8000``

### Requirements

- Windows 10/11 or Windows Server 2016+
- Administrator privileges
- Network access to Aegis server
- No .NET installation required (self-contained)

### Package Contents

- ``AegisAgent.exe`` - Main executable (self-contained)
- ``appsettings.json`` - Pre-configured settings
- ``INSTALL.ps1`` - Installation script
- ``UNINSTALL.ps1`` - Uninstallation script
- ``README.txt`` - This file
- ``*.dll`` - Required libraries (do not delete)

---

**Built on:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Server:** $ServerIP
**Group:** $NodeGroup
"@

$deployReadme | Out-File -FilePath "publish/AegisAgent/README.txt" -Encoding UTF8
Write-Host "Deployment README created." -ForegroundColor Green

# Create a compressed package
Write-Host ""
Write-Host "Step 9: Creating ZIP package..." -ForegroundColor Cyan

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$zipFileName = "AegisAgent-$timestamp.zip"
$zipPath = Join-Path $scriptPath "publish/$zipFileName"

# Remove old zip if exists
if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}

# Compress the folder
Compress-Archive -Path "publish/AegisAgent/*" -DestinationPath $zipPath -CompressionLevel Optimal

Write-Host "Package created: $zipFileName" -ForegroundColor Green

# Final summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Build Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Package Location:" -ForegroundColor Cyan
Write-Host "  Folder: $(Join-Path $scriptPath 'publish\AegisAgent')" -ForegroundColor White
Write-Host "  ZIP:    $zipPath" -ForegroundColor White
Write-Host ""
Write-Host "Package Size: $([math]::Round((Get-Item $zipPath).Length / 1MB, 2)) MB" -ForegroundColor White
Write-Host ""
Write-Host "Deployment Instructions:" -ForegroundColor Cyan
Write-Host "  1. Copy the ZIP file to target endpoints" -ForegroundColor White
Write-Host "  2. Extract the ZIP file" -ForegroundColor White
Write-Host "  3. Run INSTALL.ps1 as Administrator" -ForegroundColor White
Write-Host "  4. Choose installation type (Service recommended)" -ForegroundColor White
Write-Host ""
Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  Server: http://$ServerIP:8000/api/v1" -ForegroundColor White
Write-Host "  Group: $NodeGroup" -ForegroundColor White
Write-Host "  Process Control: Alert mode (safe)" -ForegroundColor White
Write-Host ""
Write-Host "To create another package with different settings:" -ForegroundColor Yellow
Write-Host "  Run this script again!" -ForegroundColor Yellow
Write-Host ""
