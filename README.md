# Aegis - Security Monitoring Dashboard

> **A next-generation security dashboard with real-time monitoring, policy management, and event visualization**

Aegis is a comprehensive security monitoring platform featuring a modern FastAPI backend and a beautiful Next.js dashboard with fluid animations, real-time updates, and intuitive UX.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Node](https://img.shields.io/badge/node-18+-green.svg)
![Next.js](https://img.shields.io/badge/next.js-14-black.svg)

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## Features

### Modern UI/UX
- **Fluid Animations** - Powered by Framer Motion for smooth page transitions and interactions
- **Dark Mode** - Seamlessly integrated theme switcher with persistent preferences
- **Responsive Design** - Works flawlessly on mobile, tablet, and desktop (320px - 1920px+)
- **Command Palette** - Quick navigation with Ctrl+K keyboard shortcut
- **Beautiful Typography** - Inter font with clear visual hierarchy

### Performance & Real-time
- **WebSocket Support** - Real-time updates for nodes and events without page refresh
- **Optimistic UI** - Instant feedback on all user actions using TanStack Query
- **Skeleton Loaders** - Better UX than traditional spinners during data loading
- **Debounced Filtering** - Efficient search and filter operations (300ms delay)
- **Smart Caching** - Intelligent data caching and auto-refresh (5-10 second intervals)

### Dashboard Pages

#### 1. Dashboard Home
- Animated stat cards (Total Nodes, Online, Events, Critical Alerts)
- Real-time event chart with Recharts visualization
- Live activity feed with recent events
- Auto-refresh every 5 seconds

#### 2. Nodes Management
- Instant fuzzy search with Fuse.js
- Staggered row animations for smooth data loading
- Pulsing online indicators (CSS keyframe animations)
- Add, edit, and delete nodes with modal dialogs
- Real-time online/offline status tracking
- Last seen timestamps

#### 3. Policies Management
- Visual policy cards with categorized display
- Monaco Editor for JSON rule editing with syntax highlighting
- Create and delete policies with confirmation
- View assigned nodes per policy
- Policy type badges (Firewall, IDS, Access Control, etc.)

#### 4. Event Viewer
- Debounced filtering by severity, type, and node
- Expandable rows to view full event details
- Color-coded severity badges (Low, Medium, High, Critical)
- Formatted timestamps for better readability
- JSON pretty-printing for event data
- Real-time event streaming

### Animations & Interactions
- Page transitions with fade-in and slide-up effects
- Staggered data loading (0.03s-0.05s delays per row)
- Button hover effects with scale and color transitions
- Modal scaling with spring animations
- Pulsing status indicators
- Smooth scrollbar styling

### Security
- JWT authentication with secure token storage
- Protected routes with automatic redirects
- Password hashing with bcrypt
- CORS protection
- Input validation with Pydantic schemas
- API key support for event ingestion

### Advanced Features
- Fuzzy search across nodes
- JSON editor with Monaco (VS Code editor component)
- Toast notifications for user feedback
- Zustand state management for theme and auth
- Persistent sessions with localStorage
- Keyboard navigation and accessibility


## Architecture

### Backend Structure

```
Server/
├── app.py              # FastAPI main application & WebSocket endpoint
├── websocket.py        # WebSocket connection manager
├── nodes.py            # Node management endpoints
├── logs.py             # Event/log endpoints with broadcasting
├── policies.py         # Policy management endpoints
├── login.py            # User authentication
├── auth.py             # JWT token utilities
├── models.py           # SQLAlchemy database models
├── schemas.py          # Pydantic validation schemas
├── rules.py            # Rule engine for policy evaluation
└── db.py               # Database connection & session management
```

**Key Technologies:**
- **FastAPI** - Modern async web framework
- **SQLAlchemy** - Async ORM for database operations
- **SQLite** - Lightweight database (easily swappable)
- **WebSockets** - Real-time bidirectional communication
- **JWT** - Secure authentication tokens
- **Pydantic** - Data validation and serialization

### Frontend Structure

```
Dashboard/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx          # Root layout with providers
│   │   ├── page.tsx            # Redirect to login
│   │   ├── globals.css         # Global styles + Tailwind
│   │   ├── login/page.tsx      # Authentication page
│   │   └── dashboard/
│   │       ├── layout.tsx      # Dashboard layout with nav
│   │       ├── page.tsx        # Dashboard home
│   │       ├── nodes/page.tsx  # Node management
│   │       ├── policies/page.tsx  # Policy management
│   │       └── events/page.tsx    # Event viewer
│   │
│   ├── components/
│   │   ├── providers/          # React context providers
│   │   │   ├── ThemeProvider.tsx
│   │   │   └── QueryProvider.tsx
│   │   └── ui/                 # Reusable UI components
│   │       ├── StatCard.tsx
│   │       ├── Skeleton.tsx
│   │       ├── Modal.tsx
│   │       └── CommandPalette.tsx
│   │
│   ├── lib/
│   │   ├── api.ts              # Axios API client
│   │   └── utils.ts            # Helper utilities
│   │
│   ├── store/
│   │   └── index.ts            # Zustand state stores
│   │
│   └── types/
│       └── index.ts            # TypeScript type definitions
│
├── package.json                # Dependencies
├── tsconfig.json               # TypeScript configuration
├── tailwind.config.ts          # Tailwind CSS config
├── postcss.config.js           # PostCSS config
└── next.config.js              # Next.js configuration
```

### Data Flow

```
User Action → Dashboard → API Request → Backend → Database
                ↓                           ↓
            Optimistic UI              WebSocket Broadcast
                ↓                           ↓
            Instant Feedback          All Connected Clients
```

---

## API Documentation

### Authentication

**POST** `/api/v1/token`
```json
{
  "username": "admin",
  "password": "password123"
}
```

### Nodes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/nodes` | List all nodes |
| POST | `/api/v1/nodes/register` | Register a new node |
| PUT | `/api/v1/nodes/{node_id}` | Update node details |
| DELETE | `/api/v1/nodes/{node_id}` | Delete a node |

### Policies

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/policies` | List all policies |
| POST | `/api/v1/policies` | Create a new policy |
| DELETE | `/api/v1/policies/{policy_id}` | Delete a policy |
| POST | `/api/v1/policies/assign` | Assign policy to node |

### Events/Logs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/logs` | List events with filters |
| POST | `/api/v1/logs/ingest` | Ingest a new event |


## Deployment

### Ubuntu Server Deployment

#### 1. Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3 python3-pip python3-venv -y

# Install Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -bash -
sudo apt install nodejs -y

# Install git
sudo apt install git -y
```

#### 2. Clone and Setup

```bash
# Clone repository
git clone https://github.com/SatvikVishwakarma/Aegis.git
cd Aegis

# Setup backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirments.txt

# Setup frontend
cd Dashboard
npm install
npm run build
```

#### 3. Create Systemd Services

**Backend Service** (`/etc/systemd/system/aegis-backend.service`):
```ini
[Unit]
Description=Aegis Backend Server
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/Aegis
Environment="PATH=/home/your-username/Aegis/venv/bin"
ExecStart=/home/your-username/Aegis/venv/bin/python Server/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Frontend Service** (`/etc/systemd/system/aegis-dashboard.service`):
```ini
[Unit]
Description=Aegis Dashboard
After=network.target aegis-backend.service

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/Aegis/Dashboard
ExecStart=/usr/bin/npm start
Restart=always
Environment=NODE_ENV=production
Environment=PORT=3000

[Install]
WantedBy=multi-user.target
```

#### 4. Enable and Start Services

```bash
sudo systemctl daemon-reload
sudo systemctl enable aegis-backend aegis-dashboard
sudo systemctl start aegis-backend aegis-dashboard
sudo systemctl status aegis-backend aegis-dashboard
```

#### 5. Configure Nginx (Optional but Recommended)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

#### 6. Configure Firewall

```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

## Troubleshooting

### Backend Issues

**Backend not starting?**
```bash
# Check Python version
python3 --version  # Should be 3.9+

# Reinstall dependencies
pip install -r requirments.txt --force-reinstall

# Check logs
python Server/app.py
```

### Frontend Issues

**Frontend not starting?**
```bash
# Check Node version
node --version  # Should be 18+

# Clear cache
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
- Review the Quick Start guide above
