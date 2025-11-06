# Aegis Agent - Deployment Package

**Group:** {{GROUP}}
**Server:** {{SERVER_URL}}

## Quick Installation

1. **Extract this folder** to a permanent location (e.g., `C:\AegisAgent\`)
2. **Right-click PowerShell** and select "Run as Administrator"
3. **Navigate to this folder** and run:
   ```powershell
   .\INSTALL.ps1
   ```
4. **Choose installation type**:
   - Option 1: Windows Service (Recommended)
   - Option 2: Console Mode (For testing)

## Management Commands

### Service Control (requires Administrator):
```powershell
# Check status
Get-Service -Name AegisAgent

# Start service
Start-Service -Name AegisAgent

# Stop service
Stop-Service -Name AegisAgent

# Restart service
Restart-Service -Name AegisAgent
```

### Uninstall:
```powershell
.\UNINSTALL.ps1
```

## Verification

Once installed, check the Aegis Dashboard:
1. Go to **Nodes** page
2. Your endpoint should appear as "online"
3. Go to **Events** page → {{GROUP}} → Your hostname
4. View real-time security events

## Troubleshooting

**Service won't start:**
- Check Event Viewer: `eventvwr.msc`
- Look for AegisAgent errors
- Verify network connectivity to {{SERVER_URL}}

**No events in dashboard:**
- Verify service is running: `Get-Service -Name AegisAgent`
- Test connectivity: `Test-NetConnection -ComputerName {{SERVER_HOST}} -Port {{SERVER_PORT}}`

## Configuration

This agent is pre-configured with:
- **Server:** {{SERVER_URL}}
- **Group:** {{GROUP}}
- **Process Control:** Alert mode (safe)
- **All collectors enabled**

To modify settings, edit `appsettings.json` before running INSTALL.ps1

## Requirements

- Windows 10/11 or Windows Server 2016+
- Administrator privileges
- Network access to Aegis server
- No .NET installation required (self-contained)

---

**Package built:** {{BUILD_TIME}}
