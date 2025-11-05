# Aegis - Security Monitoring Dashboard

Aegis is a complete security monitoring platform that offers real-time event collection, centralized visualization, and automated response for Windows endpoints. It features a **FastAPI backend**, a **Next.js dashboard**, and a **Windows Agent** built in C#.

---

## Overview

| Component | Technology | Description |
|------------|-------------|--------------|
| **Server** | Python (FastAPI) | Backend API, authentication, and event processing. |
| **Dashboard** | Next.js / React | Web interface for monitoring and management. |
| **Agent** | C# (.NET 8) | Windows service for process, network, and registry monitoring. |

**License:** MIT  
**Python:** 3.9+  
**Node.js:** 18+  
**Next.js:** 14+

---

## Features

### Dashboard
- Real-time event monitoring and visualization.
- Group-based node management.
- JWT-based authentication.
- Dark/light mode toggle.
- Keyboard navigation with Command Palette (Ctrl + K).
- Responsive UI with Framer Motion animations.

### Server
- RESTful API with FastAPI.
- SQLite database.
- Real-time WebSocket updates.
- JWT authentication.
- Pydantic schema validation.

### Agent
- Process, network, and registry monitoring.
- Policy-based process control (alert/suspend/kill).
- Auto-registration with server.
- Persistent Windows service.

---

## Quick Start

### 1. Server Setup
```bash
cd Server
python -m venv aegis
aegis\Scripts\activate  # Windows
# or
source aegis/bin/activate  # Linux/Mac

pip install -r requirements.txt
python database_setup.py
cp .env.example .env
python app.py
```
**Default API Key:** Found in `.env` → `AGENT_API_KEY`  
**Server runs on:** http://localhost:8000

---

### 2. Dashboard Setup
```bash
cd Dashboard
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev
```
**Dashboard runs on:** http://localhost:3000  
**Default Login:** admin / admin123

---

### 3. Agent Deployment
```powershell
git clone https://github.com/SatvikVishwakarma/Aegis.git
cd Agent
.\build-agent-package.ps1
```
Copy the generated ZIP to a Windows machine and install:
```powershell
cd C:\AegisAgent
.\INSTALL.ps1
```

---

## Project Structure
```
Aegis/
├── Server/         # FastAPI backend
├── Dashboard/      # Next.js frontend
└── Agent/          # Windows agent (.NET 8)
```

---

## License
Licensed under the MIT License. See `LICENSE` for details.

**Author:** [Satvik Vishwakarma](https://github.com/SatvikVishwakarma)