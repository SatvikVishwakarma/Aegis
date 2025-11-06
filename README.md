# Aegis - Security Monitoring Dashboard

Aegis is a **comprehensive security monitoring platform** designed for real-time visibility, incident response, and endpoint control.  
It unifies a **FastAPI backend**, a **Next.js dashboard**, and a **Windows Agent** built in **C# (.NET 8)** to deliver enterprise-grade monitoring and enforcement capabilities.

---

## Overview

| Component | Technology | Description |
|------------|-------------|--------------|
| **Server** | Python (FastAPI) | Handles authentication, API requests, event ingestion, and real-time WebSocket communication. |
| **Dashboard** | Next.js / React | Web-based user interface for managing nodes, visualizing events, and configuring policies. |
| **Agent** | C# (.NET 8) | Windows service that continuously monitors processes, registry, and network activities. |

**License:** MIT  
**Supported OS:** Windows 10/11 or Windows Server 2016+  
**Languages:** Python 3.9+, Node.js 18+, C#/.NET 8  

---

## Key Features

### 1. Real-Time Monitoring
- Collect and visualize events from multiple endpoints instantly.
- WebSocket-driven updates without page reloads.
- Optimistic UI with instant feedback and minimal latency.

### 2. Node Management
- Add, edit, group, or remove nodes directly from the dashboard.
- Track node health, status, and last seen timestamps.
- Fuzzy search and filtering using Fuse.js for quick lookups.

### 3. Event Viewer
- Advanced filtering by severity, node, or category.
- JSON pretty-printing and expandable event rows.
- Live stream of process, network, and registry events.

### 4. Policy Management
- Define and deploy security policies via JSON editor (Monaco).
- Assign firewall, IDS, and process control policies per node group.
- Enforce process actions: **alert**, **suspend**, or **kill**.

### 5. Agent Capabilities
- **Process Control**: Kill, suspend, or alert on blacklisted processes (mimikatz, psexec, etc.)
- **Registry Monitoring**: Track changes to Run keys, Services, and Winlogon
- **Process Monitoring**: Detect process creation and termination
- **Network Monitoring**: Track network connections
- **Windows Service**: Persistent operation with auto-start and recovery
- **Self-Contained**: No .NET runtime installation required on endpoints

### 6. One-Click Agent Deployment
- **Dashboard-Based Builder**: Generate customized agent packages directly from the web UI
- **Pre-Built Template**: Server uses pre-compiled agent binaries (no compilation needed)
- **Automatic Configuration**: Server URL, API key, and group assignment injected automatically
- **Ready-to-Deploy**: Download ZIP contains executable, config, and installation scripts
- **Fast Downloads**: ~20-25 MB compressed packages generated in seconds
- **Multi-Endpoint**: Build packages for different groups with different configurations

### 7. Security
- JWT-based authentication with bcrypt password hashing.
- API key validation for agent communication.
- Encrypted configuration files and token storage.
- Role-based endpoint protection for destructive actions.

---

## Architecture Overview

```
Aegis/
├── Server/              # FastAPI backend (API + Database + Auth)
│   ├── app.py
│   ├── authentication.py
│   ├── database_setup.py
│   ├── models.py
│   ├── schemas.py
│   ├── websocket.py
│   └── requirements.txt
│
├── Dashboard/           # Next.js frontend (React + Tailwind)
│   ├── src/
│   │   ├── app/         # Routes and pages
│   │   ├── components/  # UI and logic modules
│   │   ├── lib/         # API clients and utils
│   │   ├── store/       # Zustand state stores
│   │   └── types/       # TypeScript type definitions
│   ├── package.json
│   └── .env.local
│
└── Agent/               # Windows Agent (.NET 8)
    ├── Program.cs
    ├── Collectors/
    ├── PolicyManager.cs
    ├── AgentService.cs
    └── build-agent-package.ps1
```

---

## Quick Start Guide

### 1. Backend Setup

```bash
# Navigate to Server
cd Server

# Create virtual environment
python -m venv aegis
aegis\Scripts\activate   # Windows
# or
source aegis/bin/activate   # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Initialize database
python database_setup.py

# Create and edit environment file
cp .env.example .env
# Edit .env to set SECRET_KEY and AGENT_API_KEY

# Run server
python app.py
```

**Server URL:** http://localhost:8000  
**Default Admin Username:** `admin`  
**Admin Password:** Randomly generated during setup (displayed once).

---

### 2. Dashboard Setup

```bash
cd Dashboard
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev
```

**Dashboard URL:** http://localhost:3000  

---

### 3. Agent Deployment (Windows)

#### Method 1: Dashboard Builder (Recommended)

1. **Login to Dashboard** at http://localhost:3000
2. **Navigate to** "Download Agent" in the top menu
3. **Fill in the form:**
   - Server URL: Auto-filled (e.g., http://192.168.1.100:8000)
   - Node Group: Select existing or create new (e.g., "production", "workstations")
4. **Click "Download Agent Package"**
5. **Extract ZIP** on target endpoint (e.g., `C:\AegisAgent\`)
6. **Run PowerShell as Administrator** and execute:
   ```powershell
   cd C:\AegisAgent
   .\INSTALL.ps1
   ```
7. **Choose installation type:**
   - Option 1: Windows Service (auto-start, recommended for production)
   - Option 2: Console Mode (for testing and troubleshooting)

**The endpoint will appear in the Dashboard's Nodes page within 30 seconds.**

#### Method 2: Manual Build (For Development)

```powershell
cd Agent
.\build-agent-package.ps1
```

This will:
- Prompt for Server IP, API Key, and Group
- Build self-contained Windows executable
- Generate installation scripts
- Create timestamped ZIP file in `publish/` folder

#### Deploy Manually Built Package
```powershell
# Extract package to permanent location
Expand-Archive -Path AegisAgent-*.zip -DestinationPath C:\AegisAgent

# Install as Windows Service
cd C:\AegisAgent
.\INSTALL.ps1
```
---

## Environment Configuration

### `.env` (Server)
```env
SECRET_KEY=<your-secure-key>
AGENT_API_KEY=<agent-registration-key>
DATABASE_URL=sqlite:///./aegis.db
HOST=0.0.0.0
PORT=8000
```

### `.env.local` (Dashboard)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Security Highlights

- **JWT Authentication:** All routes are token-protected.  
- **Bcrypt Passwords:** Never stored in plaintext.  
- **Admin Confirmation:** Required for all destructive actions (delete node/policy).  
- **WebSocket Encryption:** Validates session tokens before data streaming.  
- **Key Rotation:** API keys can be regenerated without downtime.

---

## Deployment (Ubuntu Server)

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv git -y
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -bash -
sudo apt install nodejs -y

git clone https://github.com/SatvikVishwakarma/Aegis.git
cd Aegis/Server
chmod +x setup_and_start.sh
./setup_and_start.sh
```

**Server runs on port 8000**  
**Dashboard runs on port 3000**

---

## Troubleshooting

| Issue | Possible Cause | Fix |
|--------|----------------|-----|
| Server won’t start | Port already in use | Kill process on port 8000 or change `.env` |
| Dashboard not loading | Wrong API URL | Update `NEXT_PUBLIC_API_URL` |
| Agent not registering | Invalid API key | Verify key in `appsettings.json` |
| No events received | Collectors disabled | Enable in `appsettings.json` |
| Login fails | Expired JWT | Re-login to obtain new token |

---

## Security Best Practices

- Change all default passwords and keys immediately.
- Enable HTTPS (via Nginx reverse proxy).
- Start agents in **alert mode** before using **kill mode**.
- Use separate API keys for production and testing.
- Regularly backup `aegis.db` and rotate credentials.

---

## Performance Overview

| Component | CPU Usage | Memory | Notes |
|------------|------------|--------|-------|
| Server | 5–15% | ~200MB | Scales with number of nodes |
| Dashboard | Minimal | <150MB | Static assets served via Next.js |
| Agent | <1% | ~80MB | Auto-adjusts scan intervals |

---

## License

This project is licensed under the **MIT License**.  
See the `LICENSE` file for details.

---

## Contributing

Contributions are always welcome!

1. Fork the repository  
2. Create a new branch:
   ```bash
   git checkout -b feature/YourFeature
   ```
3. Make changes and commit:
   ```bash
   git commit -m "Add YourFeature"
   ```
4. Push and open a Pull Request.

---

## Author

**Satvik Vishwakarma**  
GitHub: [@SatvikVishwakarma](https://github.com/SatvikVishwakarma)

---

**Aegis Security Monitoring System — built for analysts, defenders, and researchers who need complete control over their infrastructure.**