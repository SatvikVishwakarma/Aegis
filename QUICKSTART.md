# 🚀 Quick Start Guide - Aegis Security Dashboard

## Installation & Setup (5 minutes)

### Step 1: Backend Setup

Open a terminal in the `Server` directory:

```powershell
# Navigate to Server directory
cd Server

# Install Python dependencies
pip install -r ../requirments.txt

# Run the FastAPI server
uvicorn app:app --reload
```

**The backend API is now running at:** `http://localhost:8000`

- 📚 API Docs: http://localhost:8000/docs
- 🏥 Health Check: http://localhost:8000/health

---

### Step 2: Frontend Setup

Open a **new terminal** in the `Dashboard` directory:

```powershell
# Navigate to Dashboard directory
cd Dashboard

# Install Node.js dependencies (this may take a few minutes)
npm install

# Start the development server
npm run dev
```

**The dashboard is now running at:** `http://localhost:3000`

---

### Step 3: Login

1. Open your browser to `http://localhost:3000`
2. Login with default credentials:
   - **Username:** `admin`
   - **Password:** `password123`

---

## 🎯 Features Overview

### ⌨️ Keyboard Shortcuts
- **Ctrl+K** (or **Cmd+K**): Open command palette for quick navigation

### 📊 Dashboard Pages

1. **Dashboard Home** - Overview with stats, charts, and recent events
2. **Nodes** - Manage security monitoring nodes
   - Add new nodes
   - Edit existing nodes
   - Real-time online/offline status
   - Instant fuzzy search
3. **Policies** - Create and manage security policies
   - Visual policy cards
   - JSON rule editor with syntax highlighting
   - View assigned nodes
4. **Events** - Security event viewer
   - Filter by severity and type
   - Expandable event details
   - Real-time updates

### 🌙 Dark Mode
Toggle dark/light theme using the moon/sun icon in the top navigation bar.

---

## 🧪 Testing the Dashboard

### Test 1: Register a Node

```powershell
curl -X POST http://localhost:8000/api/v1/nodes/register ^
  -H "Content-Type: application/json" ^
  -d "{\"hostname\": \"web-server-01\", \"ip_address\": \"192.168.1.100\"}"
```

The dashboard will automatically update with the new node!

### Test 2: Create a Policy

1. Go to the **Policies** page
2. Click "**Create Policy**"
3. Fill in:
   - **Name:** "Firewall Rules"
   - **Type:** Firewall
   - **Rules JSON:**
     ```json
     {
       "rules": [
         {
           "action": "block",
           "port": 22,
           "protocol": "tcp"
         }
       ]
     }
     ```
4. Click "**Create Policy**"

### Test 3: Ingest a Security Event

First, get an auth token:

```powershell
# Login to get token
curl -X POST http://localhost:8000/api/v1/token ^
  -H "Content-Type: application/x-www-form-urlencoded" ^
  -d "username=admin&password=password123"
```

Then ingest an event (you'll need to set the X-API-Key header):

```powershell
curl -X POST http://localhost:8000/api/v1/logs/ingest ^
  -H "Content-Type: application/json" ^
  -H "X-API-Key: your-api-key" ^
  -d "{\"node_id\": 1, \"event_type\": \"failed_login\", \"severity\": \"high\", \"details\": {\"username\": \"admin\", \"ip\": \"203.0.113.0\"}}"
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env.local` file in the `Dashboard` directory if you need to customize:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

---

## 🎨 UI Features

### Animations
- ✨ Smooth page transitions
- 📈 Staggered row animations on data load
- 🎯 Hover effects on buttons and cards
- 💫 Modal scale animations

### Real-time Updates
- 🔄 Auto-refresh every 5 seconds for nodes and events
- 🌐 WebSocket support for instant updates
- ⚡ Optimistic UI updates (changes appear instantly)

### Search & Filtering
- 🔍 Instant fuzzy search on Nodes page
- 🎚️ Debounced filters on Events page (300ms delay)
- 🏷️ Filter by severity, event type, node ID

---

## 📱 Responsive Design

The dashboard is fully responsive and works on:
- 💻 Desktop (1920x1080 and above)
- 📱 Tablet (768px and above)
- 📱 Mobile (320px and above)

---

## 🐛 Troubleshooting

### Backend not starting?
```powershell
# Make sure you're in the Server directory
cd Server

# Check Python version (should be 3.9+)
python --version

# Reinstall dependencies
pip install -r ../requirments.txt --force-reinstall
```

### Frontend not starting?
```powershell
# Make sure you're in the Dashboard directory
cd Dashboard

# Check Node.js version (should be 18+)
node --version

# Clear cache and reinstall
rm -r node_modules
rm package-lock.json
npm install
```

### CORS errors?
Make sure:
1. Backend is running on port 8000
2. Frontend is running on port 3000
3. Both are on `localhost`

---

## 🎓 Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Customize the theme**: Edit `tailwind.config.ts`
3. **Add more nodes**: Use the Nodes page
4. **Create policies**: Use the Policies page
5. **Monitor events**: Use the Events page

---

## 💡 Pro Tips

- Use the **Command Palette** (Ctrl+K) for quick navigation
- The **pulsing green dot** indicates online nodes
- **Click event rows** to expand and see full details
- The **Monaco Editor** in Policies supports full JSON validation
- **Dark mode** is persistent across sessions

---

**Enjoy your Aegis Security Dashboard! 🛡️**

For issues or questions, check the main README.md file.
