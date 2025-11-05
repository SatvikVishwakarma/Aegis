# Aegis Security Monitoring Agent (C#)

## Overview

The Aegis Agent is a Windows-native security monitoring agent written in C# (.NET 8.0). It collects security events from the Windows system and sends them to the Aegis server for centralized monitoring and analysis.

## Features

- **Node Registration**: Automatically registers with the Aegis server on startup
- **Heartbeat Mechanism**: Sends periodic heartbeats to maintain online status
- **Event Collection**: Monitors multiple security event sources:
  - Windows Event Logs (Security, System, Application)
  - File system changes
  - Process creation/termination
  - Network connections
- **Event Queuing**: Buffers events and sends them in batches
- **Auto-configuration**: Automatically detects hostname and IP address

## Prerequisites

- .NET 8.0 SDK or Runtime
- Windows OS (Windows 10/11 or Windows Server 2016+)
- Administrator privileges (required for accessing security logs)
- Network access to Aegis server

## Installation

### 1. Get the Agent API Key

From your Aegis server's `.env` file, copy the `AGENT_API_KEY` value.

### 2. Configure the Agent

Edit `appsettings.json`:

```json
{
  "Server": {
    "ApiUrl": "http://YOUR_SERVER_IP:8000/api/v1",
    "ApiKey": "YOUR_AGENT_API_KEY_HERE"
  },
  "Node": {
    "Group": "Windows-Production"
  }
}
```

Replace:
- `YOUR_SERVER_IP` with your Aegis server IP address
- `YOUR_AGENT_API_KEY_HERE` with the API key from server

### 3. Build the Agent

```powershell
dotnet build -c Release
```

### 4. Run the Agent

**Run as Administrator** (required for security event log access):

```powershell
dotnet run --project AegisAgent.csproj
```

Or run the compiled executable:

```powershell
cd bin\Release\net8.0
.\AegisAgent.exe
```

## Configuration

### Server Settings

```json
"Server": {
  "ApiUrl": "http://localhost:8000/api/v1",
  "ApiKey": "YOUR_AGENT_API_KEY"
}
```

### Node Settings

```json
"Node": {
  "Hostname": "auto",        // "auto" to detect automatically
  "IpAddress": "auto",       // "auto" to detect automatically
  "Group": "Windows-Prod"    // Group name for organizing nodes
}
```

### Monitoring Settings

```json
"Monitoring": {
  "HeartbeatIntervalSeconds": 60,          // How often to send heartbeat
  "EventBatchSize": 10,                    // Max events per batch
  "EventBatchIntervalSeconds": 5,          // How often to send events
  "StatusCheckIntervalSeconds": 30         // Internal status check interval
}
```

### Collector Settings

#### System Logs
```json
"SystemLogs": {
  "Enabled": true,
  "LogNames": ["Security", "System", "Application"]
}
```

#### File Monitor
```json
"FileMonitor": {
  "Enabled": true,
  "WatchPaths": [
    "C:\\Windows\\System32\\drivers\\etc",
    "C:\\ProgramData"
  ],
  "ExcludePatterns": ["*.tmp", "*.log"]
}
```

#### Process Monitor
```json
"ProcessMonitor": {
  "Enabled": true,
  "ScanIntervalSeconds": 10
}
```

#### Network Monitor
```json
"NetworkMonitor": {
  "Enabled": true,
  "ScanIntervalSeconds": 30
}
```

## Event Types

The agent collects and reports the following event types:

### Security Events
- `successful_login` - User logged in successfully
- `failed_login` - Failed login attempt
- `logoff` - User logged off
- `privilege_escalation` - Privilege elevation (Event ID 4672)
- `user_created` - New user account created
- `user_deleted` - User account deleted

### Process Events
- `process_started` - New process created
- `process_terminated` - Process terminated

### File Events
- `file_created` - New file created
- `file_modified` - File modified
- `file_deleted` - File deleted
- `file_renamed` - File renamed

### Network Events
- `network_connection` - New network connection established

## Running as a Windows Service

### Install as Service

```powershell
# Using sc.exe
sc.exe create "AegisAgent" binPath= "C:\Path\To\AegisAgent.exe" start= auto
sc.exe description "AegisAgent" "Aegis Security Monitoring Agent"
sc.exe start "AegisAgent"
```

### Using NSSM (Non-Sucking Service Manager)

1. Download NSSM from https://nssm.cc/download
2. Install the service:

```powershell
nssm install AegisAgent "C:\Path\To\AegisAgent.exe"
nssm set AegisAgent AppDirectory "C:\Path\To\Agent"
nssm set AegisAgent Description "Aegis Security Monitoring Agent"
nssm set AegisAgent Start SERVICE_AUTO_START
nssm start AegisAgent
```

## Troubleshooting

### Agent Can't Register

- Check if the server URL is correct in `appsettings.json`
- Verify the API key matches the server's `AGENT_API_KEY`
- Ensure network connectivity to the server
- Check firewall rules

### No Events Being Collected

- Verify the agent is running as Administrator
- Check that collectors are enabled in configuration
- Review logs for error messages
- Ensure monitored paths exist and are accessible

### High CPU Usage

- Reduce scan intervals for process and network monitors
- Limit the number of file watch paths
- Adjust event batch settings

### Access Denied Errors

- Run the agent as Administrator
- Check file system permissions for monitored paths
- Ensure the agent has access to Event Logs

## Logging

Logs are output to the console by default. To configure file logging, add to `appsettings.json`:

```json
"Logging": {
  "LogLevel": {
    "Default": "Information",
    "Microsoft": "Warning",
    "AegisAgent": "Debug"
  }
}
```

## Architecture

```
AegisAgent
├── Program.cs              - Entry point
├── AgentService.cs         - Main background service
├── Configuration.cs        - Configuration models
├── Models.cs               - Data models
├── ApiClient.cs            - HTTP client for server communication
├── NodeManager.cs          - Node registration and heartbeat
├── EventQueue.cs           - Thread-safe event buffer
└── Collectors/
    ├── IEventCollector.cs          - Collector interface
    ├── SystemLogCollector.cs       - Windows Event Log monitoring
    ├── ProcessMonitorCollector.cs  - Process monitoring
    ├── NetworkMonitorCollector.cs  - Network monitoring
    └── FileMonitorCollector.cs     - File system monitoring
```

## Performance Considerations

- **Memory**: Agent uses ~50-100 MB RAM under normal load
- **CPU**: Typically <1% CPU usage
- **Network**: Minimal bandwidth (~10-50 KB/s depending on event volume)
- **Disk**: No persistent storage, all events sent to server

## Security

- API key is stored in `appsettings.json` - protect this file
- Agent requires Administrator privileges
- Use HTTPS in production (configure server URL with https://)
- Sensitive data in events is sent as-is - ensure secure network

## Development

### Build

```powershell
dotnet build
```

### Run in Development

```powershell
dotnet run
```

### Publish for Deployment

```powershell
dotnet publish -c Release -r win-x64 --self-contained
```

This creates a standalone executable that doesn't require .NET to be installed.

## License

Part of the Aegis Security Monitoring System.
