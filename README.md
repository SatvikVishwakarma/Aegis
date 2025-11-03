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
- [Quick Start](#quick-start)
- [User Management](#user-management)
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

---

## Quick Start

### Prerequisites
- Python 3.9 or higher
- Node.js 18 or higher
- npm or yarn

### Automated Setup (Recommended)

**Step 1: Clone the repository**
```bash
git clone https://github.com/SatvikVishwakarma/Aegis.git
cd Aegis
```

**Step 2: Start the backend**
```bash
cd Server
chmod +x setup_and_start.sh
./setup_and_start.sh
```

This will automatically:
- **Create `.env` file with secure random SECRET_KEY and AGENT_API_KEY**
- Create a virtual environment named `aegis`
- Install all Python dependencies
- Initialize the database
- **Generate a secure 10-character admin password**
- **Display the admin password (SAVE IT IMMEDIATELY!)**
- Start the server on port 8000

**⚠️ CRITICAL:** The setup script generates a single admin account with a random password that will only be shown ONCE. You must save it during setup!

**Step 3: Start the dashboard** (in a new terminal)
```bash
cd Dashboard
chmod +x setup_and_start.sh
./setup_and_start.sh
```

This will:
- Install all Node.js dependencies
- Start the development server on port 3000

**Step 4: Access the dashboard**
- Open http://localhost:3000
- Login with:
  - **Username:** `admin`
  - **Password:** (the 10-character password shown during server setup)

---

## Authentication & Security

Aegis uses a single admin account system with enhanced security measures.

### Admin Account

The system creates **one admin account** during initial setup:
- **Username:** `admin` (fixed)
- **Password:** 10-character secure random alphanumeric string
- **Generated during:** First server setup (`./setup_and_start.sh`)
- **⚠️ Displayed once:** During setup - you MUST save it!

### Password Generation

The admin password is automatically generated using Python's `secrets` module:
- **Length:** 10 characters
- **Character set:** Letters (A-Z, a-z) and digits (0-9)
- **No special characters:** For easier copying and typing
- **Cryptographically secure:** Uses `secrets.choice()` for random generation

### Deletion Protection

To prevent accidental deletions, the system requires password confirmation:
- **When deleting nodes:** You must enter the admin password
- **When deleting policies:** You must enter the admin password
- The backend verifies the password before executing the deletion
- Invalid passwords return a 401 Unauthorized error

This ensures that only authorized users can perform destructive operations.

### Lost Password Recovery

If you lose the admin password:
1. Stop the server (`Ctrl+C`)
2. Delete the database and environment files:
   ```bash
   cd Server
   rm aegis.db .env
   ```
3. Run the setup script again: `./setup_and_start.sh`
4. A new admin account with a new password will be created
5. **Save the new password immediately!**

**⚠️ Warning:** This will delete all your nodes, policies, and events data!

### Advanced User Management

For advanced users who need to manage the admin account manually:

**Step 1: Activate the virtual environment**
```bash
cd Server
source aegis/bin/activate  # Linux/Mac
# OR
aegis\Scripts\activate     # Windows
```

**Step 2: Initialize the database**
```bash
python database_setup.py
```

This will:
1. Create all database tables
2. Generate an admin account with a secure random password
3. Display the admin credentials (save them immediately!)

**Admin Account:**
- Username: `admin`
- Password: Auto-generated 10-character alphanumeric string (displayed once)
- Email: `admin@aegis.local`

**⚠️ Important:** Save the password when displayed - it will not be shown again!

### Password Management

The admin password is used for:
- Dashboard login
- Confirming deletion of nodes and policies

**To reset the admin password:**
1. Delete the database file: `rm aegis.db`
2. Run initialization again: `python database_setup.py`
3. Save the new password

### Authentication Flow

**Login to dashboard:**
1. Navigate to `http://localhost:3000`
2. Enter username: `admin`
3. Enter the auto-generated password
4. Receive JWT token stored in localStorage
5. All subsequent requests include the token

**API authentication:**
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=YourPassword123"

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}

# Use token in subsequent requests
curl -X GET http://localhost:8000/api/v1/nodes \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Delete user:**
```bash
DELETE /api/v1/users/{user_id}
```

### User Database

Users are stored in the SQLite database at `Server/security_monitor.db` with:
- Bcrypt hashed passwords (never stored in plain text)
- Unique usernames and emails
- Account enable/disable status
- Creation timestamps

**Backup Recommendation:**
```bash
cp Server/security_monitor.db Server/security_monitor.db.backup
```

For detailed user management documentation, see [USER_MANAGEMENT.md](USER_MANAGEMENT.md).

---

## Architecture

### Backend Structure

```
Server/
├── app.py              # FastAPI main application & WebSocket endpoint
├── websocket.py        # WebSocket connection manager
├── authentication.py   # Password hashing & JWT token management
├── auth_routes.py      # Authentication endpoints (/auth/login, /auth/verify)
├── database_setup.py   # Database initialization & admin account creation
├── nodes.py            # Node management endpoints
├── logs.py             # Event/log endpoints with broadcasting
├── policies.py         # Policy management endpoints
├── models.py           # SQLAlchemy database models (User, Node, Policy, Event)
├── schemas.py          # Pydantic validation schemas
├── rules.py            # Rule engine for policy evaluation
├── db.py               # Database connection & session management
├── .env.example        # Environment variables template
└── setup_and_start.sh  # Automated setup script
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

**POST** `/api/v1/auth/login` - Login and get JWT token
```json
{
  "username": "admin",
  "password": "your_generated_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**GET** `/api/v1/auth/verify` - Verify current token
```
Authorization: Bearer <token>
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

### WebSocket

**WS** `/ws` - Real-time updates
- Broadcasts: `node_created`, `node_updated`, `node_deleted`, `event_created`

**Interactive API Documentation:** http://localhost:8000/docs

---

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

# Quick setup with automated script (RECOMMENDED)
cd Server
chmod +x setup_and_start.sh
./setup_and_start.sh
# Save the auto-generated admin password!

# OR manual setup:
# Setup backend
python3 -m venv aegis
source aegis/bin/activate
pip install -r requirments.txt

# Initialize database and create admin user
python database_setup.py
# ⚠️ SAVE THE DISPLAYED PASSWORD!

# Setup frontend
cd ../Dashboard
npm install
npm run build
```

**⚠️ CRITICAL: Save the admin password displayed during setup!**

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

### Environment Variable Errors

**Error: `ValueError: SECRET_KEY environment variable not set`**

This error means the required environment variables for JWT authentication are missing.

**Solution 1 (Automatic - Recommended):**
```bash
cd Server
./setup_and_start.sh
```
The script will automatically create a `.env` file with secure random keys.

**Solution 2 (Manual):**
```bash
cd Server

# Generate secure random keys
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))" >> .env
python3 -c "import secrets; print('AGENT_API_KEY=' + secrets.token_urlsafe(32))" >> .env

# Add other required variables
echo "ALGORITHM=HS256" >> .env
echo "ACCESS_TOKEN_EXPIRE_MINUTES=30" >> .env
echo "DATABASE_URL=sqlite+aiosqlite:///./aegis.db" >> .env
```

For detailed setup instructions, see [Server/ENVIRONMENT_SETUP.md](Server/ENVIRONMENT_SETUP.md)

### Backend Issues

**Backend not starting?**
```bash
# Check Python version
python3 --version  # Should be 3.9+

# Reinstall dependencies (from Server directory)
cd Server
pip install -r requirments.txt --force-reinstall

# Check logs
python app.py
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
- Review the [User Management Guide](USER_MANAGEMENT.md)
- See the Quick Start guide above

---

**Enjoy monitoring your infrastructure with Aegis!**
