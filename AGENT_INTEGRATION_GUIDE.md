# C# Agent Integration Guide

## What's Already Done

✅ Complete C# agent project structure created in `Agent/` folder
✅ All collectors implemented (System Logs, Files, Processes, Network)
✅ Node registration and heartbeat mechanism
✅ Event queuing and batch sending
✅ Configuration system with appsettings.json

## What You Need to Do

### 1. Get the Agent API Key from Server

The AGENT_API_KEY is in your server's `.env` file:

```bash
# On the server
cd D:\Github\Aegis\Server
cat .env | findstr AGENT_API_KEY
```

Copy the value (it's a base64-encoded string).

### 2. Configure the Agent

Edit `Agent/appsettings.json`:

```json
{
  "Server": {
    "ApiUrl": "http://YOUR_SERVER_IP:8000/api/v1",
    "ApiKey": "PASTE_AGENT_API_KEY_HERE"
  },
  "Node": {
    "Group": "Windows-Production"
  }
}
```

Replace:
- `YOUR_SERVER_IP` with your server's IP (or `localhost` if testing locally)
- `PASTE_AGENT_API_KEY_HERE` with the actual API key

### 3. Build and Run

```powershell
cd D:\Github\Aegis\Agent
.\setup.ps1
```

This will:
- Check for .NET 8.0 SDK
- Restore NuGet packages
- Build the agent
- Verify configuration

### 4. Run the Agent (As Administrator)

Right-click PowerShell → Run as Administrator

```powershell
cd D:\Github\Aegis\Agent
dotnet run
```

Or run the compiled executable:

```powershell
cd D:\Github\Aegis\Agent\bin\Release\net8.0
.\AegisAgent.exe
```

## What Happens When Agent Runs

1. **Registration Phase**
   - Agent detects hostname and IP address
   - Sends POST to `/api/v1/nodes/register`
   - Server responds with Node ID
   - Node appears in dashboard as "online"

2. **Monitoring Phase**
   - Starts all enabled collectors:
     - Windows Event Logs (Security, System, Application)
     - File system changes
     - Process creation/termination
     - Network connections
   - Events are queued in memory

3. **Heartbeat Loop**
   - Every 60 seconds: POST to `/api/v1/nodes/heartbeat`
   - Updates `last_seen` timestamp
   - Keeps node status as "online"

4. **Event Processing Loop**
   - Every 5 seconds: Send up to 10 events
   - POST to `/api/v1/logs/ingest` for each event
   - Events appear in dashboard in real-time
   - Failed events are re-queued

## Server-Side: Optional Timeout Feature

To automatically mark nodes as offline when they stop sending heartbeats, add this to `Server/app.py`:

```python
from datetime import datetime, timedelta
import asyncio

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(check_node_status())

async def check_node_status():
    """Mark nodes offline if no heartbeat for 2 minutes"""
    while True:
        async with AsyncSession(engine) as db:
            stmt = select(models.Node).where(models.Node.status == "online")
            result = await db.execute(stmt)
            nodes = result.scalars().all()
            
            timeout = timedelta(minutes=2)
            now = datetime.utcnow()
            
            for node in nodes:
                if now - node.last_seen > timeout:
                    node.status = "offline"
                    await db.commit()
                    await manager.broadcast({
                        "type": "node_updated",
                        "data": schemas.NodeResponse.model_validate(node).model_dump()
                    })
        
        await asyncio.sleep(30)
```

Don't forget to add the import:
```python
from datetime import datetime, timedelta
```

## Testing the Integration

### 1. Start the Server
```powershell
cd D:\Github\Aegis\Server
.\aegis\Scripts\Activate.ps1
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Start the Dashboard
```powershell
cd D:\Github\Aegis\Dashboard
npm run dev
```

### 3. Start the Agent (As Administrator)
```powershell
cd D:\Github\Aegis\Agent
dotnet run
```

### 4. Verify in Dashboard

1. Go to `http://localhost:3000`
2. Login with admin credentials
3. Navigate to "Nodes" - you should see the agent's node as "online"
4. Navigate to "Events" - click on the node's group
5. Click on the node - you should see event and network logs

## Event Examples You'll See

### From System Log Collector
- **Event ID 4624**: successful_login
- **Event ID 4625**: failed_login
- **Event ID 4688**: process_created

### From Process Monitor
- **process_started**: When any new process starts
- **process_terminated**: When a process exits

### From File Monitor
- **file_created**: New files in monitored directories
- **file_modified**: File changes
- **file_deleted**: File deletions

### From Network Monitor
- **network_connection**: New TCP connections established

## Troubleshooting

### "Access Denied" Errors
- Run PowerShell as Administrator
- The agent needs elevated privileges for Security logs

### Node Not Appearing in Dashboard
- Check API URL in appsettings.json
- Verify API key matches server's AGENT_API_KEY
- Check server logs for errors
- Ensure server is running and accessible

### No Events Appearing
- Verify collectors are enabled in appsettings.json
- Check agent logs for errors
- Ensure agent has registered (check Node ID in logs)
- Trigger some activity (create files, start processes)

### Agent Crashes on Startup
- Check .NET 8.0 is installed: `dotnet --version`
- Verify appsettings.json is valid JSON
- Check server is running and accessible

## Project Structure

```
Agent/
├── Program.cs                          # Entry point
├── AgentService.cs                     # Main service
├── Configuration.cs                    # Config models
├── Models.cs                           # Data models
├── ApiClient.cs                        # HTTP client
├── NodeManager.cs                      # Registration/heartbeat
├── EventQueue.cs                       # Event buffer
├── Collectors/
│   ├── IEventCollector.cs             # Interface
│   ├── SystemLogCollector.cs          # Windows Event Logs
│   ├── ProcessMonitorCollector.cs     # Process monitoring
│   ├── NetworkMonitorCollector.cs     # Network monitoring
│   └── FileMonitorCollector.cs        # File system monitoring
├── AegisAgent.csproj                   # Project file
├── appsettings.json                    # Configuration
├── setup.ps1                           # Setup script
└── README.md                           # Documentation
```

## Next Steps

1. **Configure and test the agent** with your server
2. **Deploy to production nodes** as a Windows Service
3. **Monitor the Events page** to see real-time security events
4. **Customize collectors** based on your needs (add/remove watch paths, adjust intervals)
5. **Set up alerting** based on specific event types or severities

## Production Deployment

To run as a Windows Service:

```powershell
# Build for production
dotnet publish -c Release -r win-x64 --self-contained

# Install as service (using NSSM)
nssm install AegisAgent "C:\Path\To\Agent\bin\Release\net8.0\win-x64\AegisAgent.exe"
nssm set AegisAgent AppDirectory "C:\Path\To\Agent"
nssm set AegisAgent Start SERVICE_AUTO_START
nssm start AegisAgent
```

This creates a self-contained executable that runs automatically on system startup.
