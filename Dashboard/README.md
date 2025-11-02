# Aegis Security Dashboard

A next-generation security dashboard with an intuitive, high-performance, and visually elegant interface for monitoring security nodes, policies, and events in real-time.

![Aegis Dashboard](https://img.shields.io/badge/Security-Dashboard-blue)
![Next.js](https://img.shields.io/badge/Next.js-14-black)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)

## ✨ Features

### 🎨 Modern UI/UX
- **Fluid Animations**: Powered by Framer Motion with smooth page transitions, staggered data loading, and hover effects
- **Dark Mode**: Seamlessly integrated dark/light theme toggle
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Command Palette**: Quick navigation with `Ctrl+K` / `Cmd+K`
- **Skeleton Loaders**: Better perceived performance than spinners

### ⚡ Performance
- **Real-time Updates**: WebSocket integration for live node and event updates
- **Optimistic UI**: Instant feedback with TanStack Query
- **Client-side Search**: Fuzzy search with Fuse.js
- **Efficient Polling**: Smart refetch strategies

### 📊 Dashboard Features
- **Statistics Cards**: Animated stat cards showing nodes, events, and alerts
- **Live Charts**: Real-time event visualization with Recharts
- **Recent Activity**: Live feed of security events

### 🖥️ Nodes Management
- **Instant Search**: Fuzzy search across hostname, IP, and status
- **Staggered Animations**: Smooth row loading animations
- **Pulsing Indicators**: Visual online/offline status with CSS animations
- **CRUD Operations**: Add, edit, and delete nodes with optimistic updates

### 🛡️ Policy Management
- **JSON Editor**: Monaco Editor integration for rule editing
- **Syntax Highlighting**: Professional code editing experience
- **Policy Cards**: Visual policy overview with assignment tracking

### 📝 Event Viewer
- **Debounced Filtering**: Smooth filtering without excessive API calls
- **Expandable Rows**: Click to view detailed event information
- **Severity Badges**: Color-coded severity indicators
- **Real-time Updates**: Auto-refresh every 5 seconds

## 🚀 Getting Started

### Prerequisites

- **Node.js** 18+ and npm/yarn
- **Python** 3.9+
- **pip** for Python package management

### Backend Setup

1. **Navigate to the Server directory**:
   ```bash
   cd Server
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # Windows
   .\venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r ../requirments.txt
   ```

4. **Run the FastAPI server**:
   ```bash
   uvicorn app:app --reload
   ```

   The API will be available at `http://localhost:8000`
   - API Documentation: `http://localhost:8000/docs`
   - Health Check: `http://localhost:8000/health`

### Frontend Setup

1. **Navigate to the Dashboard directory**:
   ```bash
   cd Dashboard
   ```

2. **Install dependencies**:
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Run the development server**:
   ```bash
   npm run dev
   # or
   yarn dev
   ```

   The dashboard will be available at `http://localhost:3000`

4. **Login with default credentials**:
   - Username: `admin`
   - Password: `password123`

## 🎯 Usage

### Keyboard Shortcuts

- **`Ctrl+K` / `Cmd+K`**: Open command palette
- **`Esc`**: Close modals and command palette

### API Endpoints

#### Authentication
- `POST /api/v1/token` - Login and get JWT token

#### Nodes
- `GET /api/v1/nodes` - List all nodes
- `POST /api/v1/nodes/register` - Register a new node
- `PUT /api/v1/nodes/{id}` - Update node details
- `DELETE /api/v1/nodes/{id}` - Delete a node
- `POST /api/v1/nodes/heartbeat` - Node heartbeat

#### Events/Logs
- `GET /api/v1/logs` - Query events with filters
- `POST /api/v1/logs/ingest` - Ingest new event

#### Policies
- `GET /api/v1/policies` - List all policies
- `POST /api/v1/policies` - Create a policy
- `DELETE /api/v1/policies/{id}` - Delete a policy
- `POST /api/v1/policies/assign` - Assign policy to node

## 🏗️ Technology Stack

### Frontend
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **Icons**: Lucide React
- **Charts**: Recharts
- **Search**: Fuse.js
- **Command Palette**: cmdk
- **Code Editor**: Monaco Editor
- **Notifications**: React Hot Toast

### Backend
- **Framework**: FastAPI
- **Database**: SQLite with SQLAlchemy (async)
- **Authentication**: JWT with python-jose
- **Password Hashing**: Passlib with bcrypt
- **CORS**: Built-in FastAPI middleware

## 🎨 Design System

### Color Palette
- **Primary**: `#3B82F6` (Blue)
- **Success**: `#10B981` (Emerald)
- **Warning**: `#F59E0B` (Amber)
- **Danger**: `#EF4444` (Red)
- **Backgrounds**: `slate-50` to `slate-900`

### Typography
- **Font Family**: Inter
- **Hierarchy**: Clear heading and body text distinction

### Spacing
- Grid-based layout with consistent 4px/8px/16px rhythm
- Generous whitespace for readability

## 📦 Project Structure

```
Aegis/
├── Server/                 # FastAPI Backend
│   ├── app.py             # Main application
│   ├── auth.py            # Authentication logic
│   ├── models.py          # Database models
│   ├── schemas.py         # Pydantic schemas
│   ├── nodes.py           # Nodes endpoints
│   ├── policies.py        # Policies endpoints
│   ├── logs.py            # Events/logs endpoints
│   ├── login.py           # Login endpoint
│   ├── rules.py           # Rule evaluation
│   └── db.py              # Database connection
│
└── Dashboard/             # Next.js Frontend
    ├── src/
    │   ├── app/           # Next.js app router pages
    │   ├── components/    # React components
    │   ├── lib/           # Utilities and API client
    │   ├── store/         # Zustand state stores
    │   └── types/         # TypeScript types
    ├── public/            # Static assets
    └── package.json       # Dependencies
```

## 🔧 Configuration

### Environment Variables

Create a `.env.local` file in the `Dashboard` directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

## 🧪 Testing

### Backend
```bash
cd Server
pytest
```

### Frontend
```bash
cd Dashboard
npm run test
```

## 🚢 Production Build

### Frontend
```bash
cd Dashboard
npm run build
npm run start
```

### Backend
```bash
cd Server
uvicorn app:app --host 0.0.0.0 --port 8000
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- FastAPI for the excellent backend framework
- Next.js team for the amazing React framework
- Vercel for Framer Motion
- All open-source contributors

---

Built with ❤️ by the Aegis Team
