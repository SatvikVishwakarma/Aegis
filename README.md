# Aegis Security Monitoring System# Aegis - Security Monitoring Dashboard



Complete security monitoring platform with centralized dashboard, real-time event collection, and automated threat response for Windows endpoints.> **A next-generation security dashboard with real-time monitoring, policy management, and event visualization**



---Aegis is a comprehensive security monitoring platform featuring a modern FastAPI backend and a beautiful Next.js dashboard with fluid animations, real-time updates, and intuitive UX.



## 🎯 Overview![License](https://img.shields.io/badge/license-MIT-blue.svg)

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)

**Aegis** is a three-tier security monitoring system:![Node](https://img.shields.io/badge/node-18+-green.svg)

- **Server** (Python/FastAPI) - Backend API and event processing![Next.js](https://img.shields.io/badge/next.js-14-black.svg)

- **Dashboard** (Next.js/React) - Web-based management interface  

- **Agent** (C#/.NET 8) - Windows endpoint monitoring and enforcement---



### Key Features## Table of Contents



#### 🖥️ Dashboard- [Features](#features)

- Real-time event monitoring- [Quick Start](#quick-start)

- Node management and grouping- [User Management](#user-management)

- User authentication (JWT-based)- [Architecture](#architecture)

- Group-based organization- [API Documentation](#api-documentation)

- Detailed event logs per node- [Deployment](#deployment)

- [Troubleshooting](#troubleshooting)

#### 🔒 Server- [Contributing](#contributing)

- RESTful API with FastAPI

- SQLite database---

- WebSocket support for real-time updates

- JWT authentication## Features

- Event ingestion and storage

### Modern UI/UX

#### 🛡️ Agent (Windows)- **Fluid Animations** - Powered by Framer Motion for smooth page transitions and interactions

- **Process Monitoring** - Track all process creation/termination- **Dark Mode** - Seamlessly integrated theme switcher with persistent preferences

- **Network Monitoring** - Monitor TCP connections- **Responsive Design** - Works flawlessly on mobile, tablet, and desktop (320px - 1920px+)

- **Registry Monitoring** - Detect registry changes in critical keys- **Command Palette** - Quick navigation with Ctrl+K keyboard shortcut

- **Process Control** - Kill/suspend/alert on blacklisted processes- **Beautiful Typography** - Inter font with clear visual hierarchy

- **Windows Service** - Persistent operation with auto-start

- **Auto-registration** - Automatically registers with server### Performance & Real-time

- **WebSocket Support** - Real-time updates for nodes and events without page refresh

---- **Optimistic UI** - Instant feedback on all user actions using TanStack Query

- **Skeleton Loaders** - Better UX than traditional spinners during data loading

## 📋 Prerequisites- **Debounced Filtering** - Efficient search and filter operations (300ms delay)

- **Smart Caching** - Intelligent data caching and auto-refresh (5-10 second intervals)

### Server & Dashboard

- **Python 3.8+** (for Server)### Dashboard Pages

- **Node.js 18+** (for Dashboard)

- **npm or yarn** (for Dashboard)#### 1. Dashboard Home

- Animated stat cards (Total Nodes, Online, Events, Critical Alerts)

### Agent- Real-time event chart with Recharts visualization

- **Windows 10/11 or Windows Server 2016+**- Live activity feed with recent events

- **.NET 8.0 SDK** (for building only, not required on endpoints)- Auto-refresh every 5 seconds

- **Administrator privileges** (for installation and monitoring)

#### 2. Nodes Management

---- Instant fuzzy search with Fuse.js

- Staggered row animations for smooth data loading

## 🚀 Quick Start- Pulsing online indicators (CSS keyframe animations)

- Add, edit, and delete nodes with modal dialogs

### 1. Server Setup- Real-time online/offline status tracking

- Last seen timestamps

```bash

cd Server#### 3. Policies Management

- Visual policy cards with categorized display

# Create virtual environment- Monaco Editor for JSON rule editing with syntax highlighting

python -m venv aegis- Create and delete policies with confirmation

aegis\Scripts\activate  # Windows- View assigned nodes per policy

source aegis/bin/activate  # Linux/Mac- Policy type badges (Firewall, IDS, Access Control, etc.)



# Install dependencies#### 4. Event Viewer

pip install -r requirments.txt- Debounced filtering by severity, type, and node

- Expandable rows to view full event details

# Setup database- Color-coded severity badges (Low, Medium, High, Critical)

python database_setup.py- Formatted timestamps for better readability

- JSON pretty-printing for event data

# Configure environment- Real-time event streaming

# Copy .env.example to .env and edit:

cp .env.example .env### Animations & Interactions

notepad .env  # Edit SECRET_KEY, AGENT_API_KEY, etc.- Page transitions with fade-in and slide-up effects

- Staggered data loading (0.03s-0.05s delays per row)

# Start server- Button hover effects with scale and color transitions

python app.py- Modal scaling with spring animations

```- Pulsing status indicators

- Smooth scrollbar styling

**Server runs on:** `http://localhost:8000`

### Security

**Default API Key:** Check `.env` file for `AGENT_API_KEY`- JWT authentication with secure token storage

- Protected routes with automatic redirects

### 2. Dashboard Setup- Password hashing with bcrypt

- CORS protection

```bash- Input validation with Pydantic schemas

cd Dashboard- API key support for event ingestion



# Install dependencies### Advanced Features

npm install- Fuzzy search across nodes

- JSON editor with Monaco (VS Code editor component)

# Configure environment- Toast notifications for user feedback

# Create .env.local:- Zustand state management for theme and auth

echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local- Persistent sessions with localStorage

- Keyboard navigation and accessibility

# Start dashboard

npm run dev---

```

## Quick Start

**Dashboard runs on:** `http://localhost:3000`

### Prerequisites

**Default Login:**- Python 3.9 or higher

- Username: `admin`- Node.js 18 or higher

- Password: `admin123`- npm or yarn



### 3. Agent Deployment### Automated Setup (Recommended)



#### On Build Server (One-time setup):**Step 1: Clone the repository**

```bash

```powershellgit clone https://github.com/SatvikVishwakarma/Aegis.git

cd Agentcd Aegis

```

# Run the package builder

.\build-agent-package.ps1**Step 2: Start the backend**

``````bash

cd Server

**The script will ask:**chmod +x setup_and_start.sh

1. Server IP address (e.g., `192.168.1.100` or `localhost`)./setup_and_start.sh

2. Agent API Key (from Server's `.env` file - `AGENT_API_KEY`)```

3. Node Group name (e.g., `Windows-Production`)

This will automatically:

**Output:**- **Create `.env` file with secure random SECRET_KEY and AGENT_API_KEY**

- ZIP file: `publish/AegisAgent-YYYYMMDD-HHMMSS.zip`- Create a virtual environment named `aegis`

- Contains everything needed for deployment- Install all Python dependencies

- Initialize the database

#### On Target Endpoints:- **Generate a secure 10-character admin password**

- **Display the admin password (SAVE IT IMMEDIATELY!)**

1. Copy the ZIP file to the Windows machine- Start the server on port 8000

2. Extract to a permanent location (e.g., `C:\AegisAgent\`)

3. Open PowerShell as Administrator:**⚠️ CRITICAL:** The setup script generates a single admin account with a random password that will only be shown ONCE. You must save it during setup!



```powershell**Step 3: Start the dashboard** (in a new terminal)

cd C:\AegisAgent```bash

.\INSTALL.ps1cd Dashboard

```chmod +x setup_and_start.sh

./setup_and_start.sh

4. Choose installation type:```

   - **Option 1**: Windows Service (Recommended - Auto-starts on boot)

   - **Option 2**: Console Mode (For testing)This will:

- Install all Node.js dependencies

**Done!** The agent will appear in the Dashboard's Nodes page.- Start the development server on port 3000



---**Step 4: Access the dashboard**

- Open http://localhost:3000

## 📁 Project Structure- Login with:

  - **Username:** `admin`

```  - **Password:** (the 10-character password shown during server setup)

Aegis/

├── Server/              # Python FastAPI backend---

│   ├── app.py          # Main application

│   ├── authentication.py## Authentication & Security

│   ├── database_setup.py

│   ├── models.pyAegis uses a single admin account system with enhanced security measures.

│   ├── .env            # Configuration (create from .env.example)

│   └── requirments.txt### Admin Account

│

├── Dashboard/          # Next.js frontendThe system creates **one admin account** during initial setup:

│   ├── src/- **Username:** `admin` (fixed)

│   │   ├── app/       # Pages and routes- **Password:** 10-character secure random alphanumeric string

│   │   ├── components/ # Reusable components- **Generated during:** First server setup (`./setup_and_start.sh`)

│   │   ├── lib/       # API client and utilities- **⚠️ Displayed once:** During setup - you MUST save it!

│   │   └── types/     # TypeScript definitions

│   ├── package.json### Password Generation

│   └── .env.local     # Configuration

│The admin password is automatically generated using Python's `secrets` module:

└── Agent/             # C# Windows agent- **Length:** 10 characters

    ├── Program.cs- **Character set:** Letters (A-Z, a-z) and digits (0-9)

    ├── AgentService.cs- **No special characters:** For easier copying and typing

    ├── PolicyManager.cs- **Cryptographically secure:** Uses `secrets.choice()` for random generation

    ├── Collectors/    # Event collectors

    │   ├── ProcessMonitorCollector.cs### Deletion Protection

    │   ├── NetworkMonitorCollector.cs

    │   ├── RegistryMonitorCollector.csTo prevent accidental deletions, the system requires password confirmation:

    │   └── ProcessControlCollector.cs- **When deleting nodes:** You must enter the admin password

    ├── appsettings.json- **When deleting policies:** You must enter the admin password

    └── build-agent-package.ps1  # Package builder- The backend verifies the password before executing the deletion

```- Invalid passwords return a 401 Unauthorized error



---This ensures that only authorized users can perform destructive operations.



## ⚙️ Configuration### Lost Password Recovery



### Server Configuration (`.env`)If you lose the admin password:

1. Stop the server (`Ctrl+C`)

```env2. Delete the database and environment files:

# Security   ```bash

SECRET_KEY=your-secret-key-here-change-this-in-production   cd Server

AGENT_API_KEY=your-agent-api-key-change-this   rm aegis.db .env

   ```

# Database3. Run the setup script again: `./setup_and_start.sh`

DATABASE_URL=sqlite:///./aegis.db4. A new admin account with a new password will be created

5. **Save the new password immediately!**

# Server

HOST=0.0.0.0**⚠️ Warning:** This will delete all your nodes, policies, and events data!

PORT=8000

```### Advanced User Management



### Dashboard Configuration (`.env.local`)For advanced users who need to manage the admin account manually:



```env**Step 1: Activate the virtual environment**

NEXT_PUBLIC_API_URL=http://localhost:8000```bash

```cd Server

source aegis/bin/activate  # Linux/Mac

For production, change to your server's public URL:# OR

```envaegis\Scripts\activate     # Windows

NEXT_PUBLIC_API_URL=http://your-server-ip:8000```

```

**Step 2: Initialize the database**

### Agent Configuration (Automatic)```bash

python database_setup.py

The `build-agent-package.ps1` script automatically generates `appsettings.json` with your provided configuration. You can manually edit it if needed:```



```jsonThis will:

{1. Create all database tables

  "Server": {2. Generate an admin account with a secure random password

    "ApiUrl": "http://YOUR_SERVER:8000/api/v1",3. Display the admin credentials (save them immediately!)

    "ApiKey": "YOUR_AGENT_API_KEY"

  },**Admin Account:**

  "Node": {- Username: `admin`

    "Hostname": "auto",- Password: Auto-generated 10-character alphanumeric string (displayed once)

    "IpAddress": "auto",- Email: `admin@aegis.local`

    "Group": "Windows-Production"

  },**⚠️ Important:** Save the password when displayed - it will not be shown again!

  "Collectors": {

    "ProcessMonitor": { "Enabled": true, "ScanIntervalSeconds": 10 },### Password Management

    "NetworkMonitor": { "Enabled": true, "ScanIntervalSeconds": 30 },

    "RegistryMonitor": { "Enabled": true, "ScanIntervalSeconds": 60 },The admin password is used for:

    "ProcessControl": { - Dashboard login

      "Enabled": true, - Confirming deletion of nodes and policies

      "ScanIntervalSeconds": 5,

      "Action": "alert"  // Options: alert, suspend, kill**To reset the admin password:**

    }1. Delete the database file: `rm aegis.db`

  }2. Run initialization again: `python database_setup.py`

}3. Save the new password

```

### Authentication Flow

---

**Login to dashboard:**

## 🔐 Security Features1. Navigate to `http://localhost:3000`

2. Enter username: `admin`

### Agent Capabilities3. Enter the auto-generated password

4. Receive JWT token stored in localStorage

#### Process Control5. All subsequent requests include the token

- **Default Blacklist**: mimikatz, psexec, netcat, procdump, lazagne

- **Actions**:**API authentication:**

  - `alert` - Log only (safe)```bash

  - `suspend` - Freeze process (reversible)# Login

  - `kill` - Terminate process (permanent)curl -X POST http://localhost:8000/api/v1/auth/login \

  -H "Content-Type: application/x-www-form-urlencoded" \

⚠️ **Start with "alert" mode and test thoroughly before using "kill" mode!**  -d "username=admin&password=YourPassword123"



#### Registry Monitoring# Response

Monitors critical Windows registry paths:{

- Autorun locations (`HKLM/HKCU\...\Run`, `RunOnce`)  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",

- Windows Services (`HKLM\SYSTEM\CurrentControlSet\Services`)  "token_type": "bearer"

- Winlogon settings}



#### Event Types# Use token in subsequent requests

- `process_started` - New process detectedcurl -X GET http://localhost:8000/api/v1/nodes \

- `process_terminated` - Process ended  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

- `blacklisted_process_detected` - Blacklisted process found```

- `process_terminated_by_policy` - Process killed by policy

- `process_suspended_by_policy` - Process suspended by policy**Delete user:**

- `network_connection` - New TCP connection```bash

- `registry_value_added` - Registry value createdDELETE /api/v1/users/{user_id}

- `registry_value_modified` - Registry value changed```

- `registry_value_deleted` - Registry value removed

### User Database

---

Users are stored in the SQLite database at `Server/security_monitor.db` with:

## 📊 Usage- Bcrypt hashed passwords (never stored in plain text)

- Unique usernames and emails

### Dashboard Navigation- Account enable/disable status

- Creation timestamps

1. **Login** - `http://localhost:3000/login`

   - Default: `admin` / `admin123`**Backup Recommendation:**

```bash

2. **Dashboard** - Overview and statisticscp Server/security_monitor.db Server/security_monitor.db.backup

```

3. **Nodes** - View all registered agents

   - Click on a node to see detailed logsFor detailed user management documentation, see [USER_MANAGEMENT.md](USER_MANAGEMENT.md).



4. **Events** - Browse by groups---

   - Select group → Select node → View events

## Architecture

5. **Policies** - Manage security policies (future feature)

### Backend Structure

### Agent Management

```

#### Check Agent StatusServer/

```powershell├── app.py              # FastAPI main application & WebSocket endpoint

Get-Service -Name AegisAgent├── websocket.py        # WebSocket connection manager

```├── authentication.py   # Password hashing & JWT token management

├── auth_routes.py      # Authentication endpoints (/auth/login, /auth/verify)

#### Start/Stop Agent├── database_setup.py   # Database initialization & admin account creation

```powershell├── nodes.py            # Node management endpoints

Start-Service -Name AegisAgent├── logs.py             # Event/log endpoints with broadcasting

Stop-Service -Name AegisAgent├── policies.py         # Policy management endpoints

Restart-Service -Name AegisAgent├── models.py           # SQLAlchemy database models (User, Node, Policy, Event)

```├── schemas.py          # Pydantic validation schemas

├── rules.py            # Rule engine for policy evaluation

#### Uninstall Agent├── db.py               # Database connection & session management

```powershell├── .env.example        # Environment variables template

cd C:\AegisAgent└── setup_and_start.sh  # Automated setup script

.\UNINSTALL.ps1```

```

**Key Technologies:**

#### View Agent Logs- **FastAPI** - Modern async web framework

```powershell- **SQLAlchemy** - Async ORM for database operations

# Event Viewer- **SQLite** - Lightweight database (easily swappable)

Get-EventLog -LogName Application -Source AegisAgent -Newest 50- **WebSockets** - Real-time bidirectional communication

- **JWT** - Secure authentication tokens

# Or run in console mode for debugging- **Pydantic** - Data validation and serialization

cd C:\AegisAgent

.\AegisAgent.exe### Frontend Structure

```

```

---Dashboard/

├── src/

## 🔧 Development│   ├── app/                    # Next.js App Router

│   │   ├── layout.tsx          # Root layout with providers

### Server Development│   │   ├── page.tsx            # Redirect to login

│   │   ├── globals.css         # Global styles + Tailwind

```bash│   │   ├── login/page.tsx      # Authentication page

cd Server│   │   └── dashboard/

python -m venv aegis│   │       ├── layout.tsx      # Dashboard layout with nav

aegis\Scripts\activate│   │       ├── page.tsx        # Dashboard home

pip install -r requirments.txt│   │       ├── nodes/page.tsx  # Node management

│   │       ├── policies/page.tsx  # Policy management

# Run with auto-reload│   │       └── events/page.tsx    # Event viewer

python app.py│   │

```│   ├── components/

│   │   ├── providers/          # React context providers

**API Documentation:** `http://localhost:8000/docs`│   │   │   ├── ThemeProvider.tsx

│   │   │   └── QueryProvider.tsx

### Dashboard Development│   │   └── ui/                 # Reusable UI components

│   │       ├── StatCard.tsx

```bash│   │       ├── Skeleton.tsx

cd Dashboard│   │       ├── Modal.tsx

npm install│   │       └── CommandPalette.tsx

npm run dev│   │

```│   ├── lib/

│   │   ├── api.ts              # Axios API client

**Dev Server:** `http://localhost:3000`│   │   └── utils.ts            # Helper utilities

│   │

### Agent Development│   ├── store/

│   │   └── index.ts            # Zustand state stores

```powershell│   │

cd Agent│   └── types/

│       └── index.ts            # TypeScript type definitions

# Build│

dotnet build├── package.json                # Dependencies

├── tsconfig.json               # TypeScript configuration

# Run in debug mode├── tailwind.config.ts          # Tailwind CSS config

dotnet run├── postcss.config.js           # PostCSS config

└── next.config.js              # Next.js configuration

# Build release```

dotnet build -c Release

```### Data Flow



---```

User Action → Dashboard → API Request → Backend → Database

## 📡 API Endpoints                ↓                           ↓

            Optimistic UI              WebSocket Broadcast

### Authentication                ↓                           ↓

- `POST /api/v1/auth/login` - User login            Instant Feedback          All Connected Clients

- `POST /api/v1/auth/register` - User registration```



### Nodes---

- `POST /api/v1/nodes/register` - Agent registration

- `POST /api/v1/nodes/heartbeat` - Agent heartbeat## API Documentation

- `GET /api/v1/nodes` - List all nodes

- `GET /api/v1/nodes/{id}` - Get node details### Authentication



### Events**POST** `/api/v1/auth/login` - Login and get JWT token

- `POST /api/v1/logs/ingest` - Ingest events from agent```json

- `GET /api/v1/logs` - Query events{

- `GET /api/v1/logs/node/{node_id}` - Get events for specific node  "username": "admin",

  "password": "your_generated_password"

---}

```

## 🐛 Troubleshooting

**Response:**

### Server Issues```json

{

**Server won't start:**  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",

- Check if port 8000 is available  "token_type": "bearer"

- Verify Python version: `python --version`}

- Check database file permissions```

- Review `.env` configuration

**GET** `/api/v1/auth/verify` - Verify current token

**Database errors:**```

- Delete `aegis.db` and run `python database_setup.py` againAuthorization: Bearer <token>

- Check file permissions```



### Dashboard Issues### Nodes



**Dashboard won't connect to server:**| Method | Endpoint | Description |

- Verify `NEXT_PUBLIC_API_URL` in `.env.local`|--------|----------|-------------|

- Check if server is running on specified URL| GET | `/api/v1/nodes` | List all nodes |

- Check browser console for CORS errors| POST | `/api/v1/nodes/register` | Register a new node |

- Verify firewall settings| PUT | `/api/v1/nodes/{node_id}` | Update node details |

| DELETE | `/api/v1/nodes/{node_id}` | Delete a node |

**Login fails:**

- Check server logs### Policies

- Verify server is running

- Check network connectivity| Method | Endpoint | Description |

|--------|----------|-------------|

### Agent Issues| GET | `/api/v1/policies` | List all policies |

| POST | `/api/v1/policies` | Create a new policy |

**Agent won't register:**| DELETE | `/api/v1/policies/{policy_id}` | Delete a policy |

- Verify server URL in `appsettings.json`| POST | `/api/v1/policies/assign` | Assign policy to node |

- Check API key matches server's `AGENT_API_KEY`

- Test connectivity: `Test-NetConnection -ComputerName SERVER_IP -Port 8000`### Events/Logs

- Check firewall rules

| Method | Endpoint | Description |

**Service won't start:**|--------|----------|-------------|

- Check Event Viewer for errors| GET | `/api/v1/logs` | List events with filters |

- Verify `appsettings.json` exists in same folder as `AegisAgent.exe`| POST | `/api/v1/logs/ingest` | Ingest a new event |

- Run as Administrator

- Check server accessibility### WebSocket



**No events in dashboard:****WS** `/ws` - Real-time updates

- Verify agent service is running: `Get-Service -Name AegisAgent`- Broadcasts: `node_created`, `node_updated`, `node_deleted`, `event_created`

- Check collectors are enabled in `appsettings.json`

- Review agent logs**Interactive API Documentation:** http://localhost:8000/docs

- Verify server is receiving data

---

**High CPU usage:**

Increase scan intervals in `appsettings.json`:## Deployment

```json

"ProcessMonitor": { "ScanIntervalSeconds": 30 },### Ubuntu Server Deployment

"NetworkMonitor": { "ScanIntervalSeconds": 60 },

"RegistryMonitor": { "ScanIntervalSeconds": 120 }#### 1. Install Dependencies

```

```bash

---# Update system

sudo apt update && sudo apt upgrade -y

## 🔒 Security Considerations

# Install Python

### Production Deploymentsudo apt install python3 python3-pip python3-venv -y



#### Server# Install Node.js 20

- ✅ Change `SECRET_KEY` in `.env` to a strong random valuecurl -fsSL https://deb.nodesource.com/setup_20.x | sudo -bash -

- ✅ Change `AGENT_API_KEY` to a strong random valuesudo apt install nodejs -y

- ✅ Use HTTPS (configure reverse proxy like Nginx)

- ✅ Enable firewall rules (allow only necessary ports)# Install git

- ✅ Use strong database passwordssudo apt install git -y

- ✅ Regularly backup `aegis.db````

- ✅ Change default admin password immediately

#### 2. Clone and Setup

#### Dashboard

- ✅ Use HTTPS in production```bash

- ✅ Update `NEXT_PUBLIC_API_URL` to use HTTPS# Clone repository

- ✅ Enable rate limitinggit clone https://github.com/SatvikVishwakarma/Aegis.git

- ✅ Use environment variables for sensitive datacd Aegis



#### Agent# Quick setup with automated script (RECOMMENDED)

- ✅ Protect the deployment package (contains API key)cd Server

- ✅ Use different API keys for different environmentschmod +x setup_and_start.sh

- ✅ Start with "alert" mode before enabling "kill" mode./setup_and_start.sh

- ✅ Test in staging environment first# Save the auto-generated admin password!

- ✅ Rotate API keys periodically

- ✅ Secure communication channel (use HTTPS)# OR manual setup:

# Setup backend

### Process Control Safetypython3 -m venv aegis

source aegis/bin/activate

⚠️ **Process Control "kill" mode is DANGEROUS!**pip install -r requirments.txt



**Recommended Testing Path:**# Initialize database and create admin user

1. **Week 1**: Run with `Action: "alert"` - Monitor detectionspython database_setup.py

2. **Week 2**: Review all alerts, adjust blacklist# ⚠️ SAVE THE DISPLAYED PASSWORD!

3. **Week 3**: Test `Action: "suspend"` in staging

4. **Week 4**: Deploy `Action: "kill"` in production (if needed)# Setup frontend

cd ../Dashboard

**Start conservative, increase enforcement gradually!**npm install

npm run build

---```



## 📈 Performance**⚠️ CRITICAL: Save the admin password displayed during setup!**



### Server#### 3. Create Systemd Services

- CPU: ~5-10% (idle), ~20-30% (under load)

- RAM: ~100-200 MB**Backend Service** (`/etc/systemd/system/aegis-backend.service`):

- Disk: Minimal (database grows with events)```ini

[Unit]

### DashboardDescription=Aegis Backend Server

- Runs in browserAfter=network.target

- Minimal server resources (static site)

[Service]

### AgentType=simple

- CPU: <1% (normal operation)User=your-username

- RAM: ~50-100 MBWorkingDirectory=/home/your-username/Aegis

- Network: ~10-50 KB/s (depending on event volume)Environment="PATH=/home/your-username/Aegis/venv/bin"

- Disk: No persistent storageExecStart=/home/your-username/Aegis/venv/bin/python Server/app.py

Restart=always

---

[Install]

## 🔄 Update WorkflowWantedBy=multi-user.target

```

### Updating Server

```bash**Frontend Service** (`/etc/systemd/system/aegis-dashboard.service`):

cd Server```ini

git pull[Unit]

pip install -r requirments.txtDescription=Aegis Dashboard

python app.pyAfter=network.target aegis-backend.service

```

[Service]

### Updating DashboardType=simple

```bashUser=your-username

cd DashboardWorkingDirectory=/home/your-username/Aegis/Dashboard

git pullExecStart=/usr/bin/npm start

npm installRestart=always

npm run buildEnvironment=NODE_ENV=production

npm start  # For productionEnvironment=PORT=3000

```

[Install]

### Updating AgentsWantedBy=multi-user.target

1. Build new package: `.\build-agent-package.ps1````

2. Deploy to endpoints

3. Run `INSTALL.ps1` (will stop old service, install new version)#### 4. Enable and Start Services



---```bash

sudo systemctl daemon-reload

## 📞 Supportsudo systemctl enable aegis-backend aegis-dashboard

sudo systemctl start aegis-backend aegis-dashboard

### Common Commands Referencesudo systemctl status aegis-backend aegis-dashboard

```

#### Server

```bash#### 5. Configure Nginx (Optional but Recommended)

# Start server

python app.py```nginx

server {

# Reset database    listen 80;

python database_setup.py    server_name your-domain.com;



# Check logs    location / {

tail -f aegis.db  # View database activity        proxy_pass http://localhost:3000;

```        proxy_http_version 1.1;

        proxy_set_header Upgrade $http_upgrade;

#### Dashboard        proxy_set_header Connection 'upgrade';

```bash        proxy_set_header Host $host;

# Development    }

npm run dev

    location /api {

# Production build        proxy_pass http://localhost:8000;

npm run build        proxy_http_version 1.1;

npm start        proxy_set_header Host $host;

```    }



#### Agent    location /ws {

```powershell        proxy_pass http://localhost:8000;

# Build package        proxy_http_version 1.1;

.\build-agent-package.ps1        proxy_set_header Upgrade $http_upgrade;

        proxy_set_header Connection "upgrade";

# Check service status    }

Get-Service -Name AegisAgent}

```

# View logs

Get-EventLog -LogName Application -Source AegisAgent -Newest 50#### 6. Configure Firewall



# Debug mode (console)```bash

.\AegisAgent.exesudo ufw allow 22/tcp    # SSH

```sudo ufw allow 80/tcp    # HTTP

sudo ufw allow 443/tcp   # HTTPS

---sudo ufw enable

```

## 🎯 Quick Reference

## Troubleshooting

### Ports

- **Server**: 8000 (default, configurable)### Environment Variable Errors

- **Dashboard**: 3000 (development), 80/443 (production)

**Error: `ValueError: SECRET_KEY environment variable not set`**

### Default Credentials

- **Dashboard Login**: admin / admin123 (⚠️ CHANGE IN PRODUCTION!)This error means the required environment variables for JWT authentication are missing.



### File Sizes**Solution 1 (Automatic - Recommended):**

- **Server**: ~50 MB (with dependencies)```bash

- **Dashboard**: ~200 MB (with node_modules)cd Server

- **Agent Package**: ~20-25 MB (compressed ZIP)./setup_and_start.sh

- **Agent Installed**: ~70-80 MB (includes .NET runtime)```

The script will automatically create a `.env` file with secure random keys.

### Requirements

- **Server**: Python 3.8+, ~200 MB disk**Solution 2 (Manual):**

- **Dashboard**: Node.js 18+, ~500 MB disk```bash

- **Agent**: Windows 10+, No .NET required on endpoints!cd Server



---# Generate secure random keys

python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))" >> .env

## 🚀 Production Checklistpython3 -c "import secrets; print('AGENT_API_KEY=' + secrets.token_urlsafe(32))" >> .env



Before deploying to production:# Add other required variables

echo "ALGORITHM=HS256" >> .env

### Serverecho "ACCESS_TOKEN_EXPIRE_MINUTES=30" >> .env

- [ ] Change `SECRET_KEY` in `.env`echo "DATABASE_URL=sqlite+aiosqlite:///./aegis.db" >> .env

- [ ] Change `AGENT_API_KEY` in `.env````

- [ ] Change default admin password

- [ ] Setup HTTPS (reverse proxy)For detailed setup instructions, see [Server/ENVIRONMENT_SETUP.md](Server/ENVIRONMENT_SETUP.md)

- [ ] Configure firewall

- [ ] Setup database backups### Backend Issues

- [ ] Enable logging

- [ ] Test API endpoints**Backend not starting?**

```bash

### Dashboard# Check Python version

- [ ] Update `NEXT_PUBLIC_API_URL` to production serverpython3 --version  # Should be 3.9+

- [ ] Build production version: `npm run build`

- [ ] Setup HTTPS# Reinstall dependencies (from Server directory)

- [ ] Configure web server (Nginx/Apache)cd Server

- [ ] Test all pagespip install -r requirments.txt --force-reinstall



### Agent# Check logs

- [ ] Test in staging environmentpython app.py

- [ ] Verify all collectors work```

- [ ] Test service installation

- [ ] Test service recovery (restart on failure)### Frontend Issues

- [ ] Start with "alert" mode

- [ ] Monitor for false positives**Frontend not starting?**

- [ ] Document deployment procedure```bash

# Check Node version

---node --version  # Should be 18+



**Aegis Security Monitoring System - Complete Setup Guide**# Clear cache

rm -rf node_modules package-lock.json
npm install

# Build fresh
npm run build
```

**CORS errors?**
- Ensure backend is on port 8000
- Ensure frontend is on port 3000
- Both should be on `localhost`

**TypeScript errors?**
- Run `npm install` to install all dependencies
- Restart VS Code TypeScript server

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## Authors

- **Satvik Vishwakarma** - [@SatvikVishwakarma](https://github.com/SatvikVishwakarma)

---

## Support

For issues or questions:
- Open an issue on GitHub
- Check the [API documentation](http://localhost:8000/docs)
- Review the [User Management Guide](USER_MANAGEMENT.md)
- See the Quick Start guide above

---

**Enjoy monitoring your infrastructure with Aegis!**
