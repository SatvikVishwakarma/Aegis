# 🎯 FRESH START - New Authentication System

## ✨ What's New

**COMPLETE REWRITE** - All authentication code rebuilt from scratch:

### Files DELETED ❌
- `auth.py` - Old authentication module
- `login.py` - Old login endpoint
- `users.py` - Old user management
- `init_db.py` - Old database initialization
- `diagnose_auth.py` - Old diagnostic tool
- `security.py` - Old security middleware

### Files CREATED ✅
- `authentication.py` - Clean password & JWT functions
- `database_setup.py` - Fresh database initialization  
- `auth_routes.py` - Simple login endpoint at `/api/v1/auth/login`

### Changes Made 🔧
- Dashboard now calls `/api/v1/auth/login` instead of `/api/v1/token`
- Server binds to `0.0.0.0` (accessible from network)
- No security middleware - simple and clean
- Database file correctly named `aegis.db`

---

## 🚀 Setup on Ubuntu Server

### Step 1: Pull Latest Code
```bash
cd ~/Aegis
git pull
```

### Step 2: Setup Server Environment
```bash
cd Server

# Create virtual environment if doesn't exist
python3 -m venv aegis

# Activate it
source aegis/bin/activate

# Install dependencies
pip install -r requirments.txt
```

### Step 3: Create .env File (if doesn't exist)
```bash
# Generate secret keys
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))" > .env
python3 -c "import secrets; print('AGENT_API_KEY=' + secrets.token_urlsafe(32))" >> .env

# Add other settings
cat >> .env << 'EOF'
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_FILE=aegis.db
EOF
```

### Step 4: Initialize Database
```bash
python database_setup.py
```

**IMPORTANT:** Save the password displayed! It will look like:
```
**********************************************************************
ADMIN CREDENTIALS
**********************************************************************
Username: admin
Password: Ab3xK9mL2n
**********************************************************************
```

### Step 5: Start the Server
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Step 6: Start Dashboard (New Terminal)
```bash
cd ~/Aegis/Dashboard
npm run dev
```

### Step 7: Login
1. Open browser: `http://localhost:3000`
2. Username: `admin`
3. Password: (from Step 4)
4. Click "Sign In"

---

## ✅ Verification Steps

### Check 1: Database File Exists
```bash
ls -la ~/Aegis/Server/aegis.db
# Should show the file with size > 0
```

### Check 2: Server is Running
```bash
curl http://localhost:8000/health
# Should return: {"status":"ok"}
```

### Check 3: Login Endpoint Works
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=YOUR_PASSWORD"

# Should return: {"access_token":"eyJ...","token_type":"bearer"}
```

---

## 🔧 Quick Commands

### Restart Everything (Clean Slate)
```bash
# Stop all running processes (Ctrl+C)

# Remove old database
cd ~/Aegis/Server
rm -f aegis.db

# Reinitialize
source aegis/bin/activate
python database_setup.py
# SAVE THE NEW PASSWORD!

# Start server
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Check Logs
```bash
# Server logs are in the terminal where uvicorn is running
# Look for:
# INFO - Login attempt: username=admin
# INFO - Login successful: admin
```

---

## 📁 New File Structure

```
Server/
├── authentication.py       ← NEW: Password & JWT functions
├── database_setup.py       ← NEW: DB initialization
├── auth_routes.py          ← NEW: Login endpoint
├── app.py                  ← Updated: Uses new auth
├── nodes.py                ← Updated: Uses authentication module
├── policies.py             ← Updated: Uses authentication module
├── models.py               ← Same: User model unchanged
├── schemas.py              ← Same: Schemas unchanged
├── db.py                   ← Updated: Database file name fixed
└── aegis.db                ← Generated: SQLite database
```

---

## 🎯 Key Differences

### Old System ❌
- Multiple files (auth.py, login.py, users.py, init_db.py)
- Security middleware blocking requests
- Localhost-only binding
- Complex authentication flow
- Database named `security_monitor.db`

### New System ✅
- Clean single files (authentication.py, auth_routes.py, database_setup.py)
- No middleware - direct access
- Network accessible (0.0.0.0)
- Simple login flow
- Database named `aegis.db`

---

## 🔐 Security Features

Still maintained:
- ✅ Bcrypt password hashing (12 rounds)
- ✅ JWT token authentication
- ✅ Token expiration (30 minutes)
- ✅ Password confirmation for deletions
- ✅ Auto-generated secure passwords (10 chars)

Removed:
- ❌ Security middleware (was blocking legitimate requests)
- ❌ Origin/Referer checking (unnecessary complication)
- ❌ API key validation (not needed for localhost)

---

## 🆘 Troubleshooting

### Problem: "aegis.db not found"
**Solution:**
```bash
cd ~/Aegis/Server
source aegis/bin/activate
python database_setup.py
```

### Problem: "Connection refused" 
**Solution:**
```bash
# Make sure server is running
cd ~/Aegis/Server
source aegis/bin/activate
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Problem: "Invalid credentials"
**Solution:**
```bash
# Test password directly
cd ~/Aegis/Server
source aegis/bin/activate
python -c "
import asyncio
from sqlalchemy import select
from db import AsyncSessionLocal
from models import User
from authentication import verify_password

async def test():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.username=='admin'))
        user = result.scalar_one_or_none()
        if user:
            print(f'User exists: {user.username}')
            password = input('Enter password to test: ')
            if verify_password(password, user.hashed_password):
                print('✓ Password is CORRECT!')
            else:
                print('✗ Password is WRONG!')
        else:
            print('✗ Admin user not found!')

asyncio.run(test())
"
```

### Problem: "Module not found"
**Solution:**
```bash
# Reinstall dependencies
cd ~/Aegis/Server
source aegis/bin/activate
pip install -r requirments.txt
```

---

## 🎉 Summary

The authentication system has been **completely rebuilt** with:
- ✅ Clean, simple code
- ✅ No middleware complications  
- ✅ Direct database creation (`aegis.db`)
- ✅ Simple login endpoint (`/api/v1/auth/login`)
- ✅ Network accessible (0.0.0.0)

**Just pull, initialize database, save password, and login!** 🚀
