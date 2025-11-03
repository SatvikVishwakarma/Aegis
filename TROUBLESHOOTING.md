# Authentication Troubleshooting Guide

## Quick Diagnosis

If you can't login to the dashboard, run the diagnostic tool:

```bash
# 1. Navigate to Server directory
cd Server

# 2. Activate virtual environment
source aegis/bin/activate  # Linux/Mac
# OR
aegis\Scripts\activate     # Windows

# 3. Run diagnostic tool
python diagnose_auth.py
```

## What the Diagnostic Tool Tests

The `diagnose_auth.py` script performs comprehensive checks:

### ✅ Test 1: Database Connection
- Checks if `aegis.db` file exists
- Verifies database connection works
- Shows database file size

### ✅ Test 2: Environment Variables
- Validates `.env` file exists
- Checks all required variables are set:
  - `SECRET_KEY` (JWT signing)
  - `ALGORITHM` (JWT algorithm)
  - `ACCESS_TOKEN_EXPIRE_MINUTES` (token lifetime)
  - `AGENT_API_KEY` (agent authentication)

### ✅ Test 3: User Table Schema
- Verifies `users` table exists
- Shows number of users in database
- Lists table columns

### ✅ Test 4: Admin User
- Checks if admin user exists
- Shows admin account details
- Verifies account is not disabled
- Displays password hash preview

### ✅ Test 5: Password Hashing Functions
- Tests `hash_password()` function
- Tests `verify_password()` function
- Verifies bcrypt is working correctly

### ✅ Test 6: Admin Password Verification (Interactive)
- Allows you to test specific passwords
- Tells you if password is correct
- Interactive - test multiple passwords

### ✅ Test 7: JWT Token Creation
- Tests JWT token generation
- Verifies token structure
- Shows token preview

### ✅ Test 8: Login Endpoint Simulation (Interactive)
- Simulates complete login flow
- Prompts for username and password
- Shows exactly what would happen during login
- Creates actual JWT token if successful

### ✅ Test 9: List All Users
- Shows all users in database
- Displays full details for each user
- Helps identify multiple accounts

### ✅ Test 10: Dashboard Configuration
- Checks Dashboard directory exists
- Verifies `.env.local` configuration
- Checks API URL configuration
- Validates login endpoint setup

---

## Common Issues & Solutions

### Issue 1: "Admin user does NOT exist"

**Cause:** Database not initialized or admin user wasn't created

**Solution:**
```bash
cd Server
source aegis/bin/activate
python init_db.py
```

This will create the admin user and display the password.

---

### Issue 2: "Password is INCORRECT"

**Cause:** You're using the wrong password

**Solutions:**

1. **Check if you saved the password from setup:**
   - Password was displayed during `./setup_and_start.sh`
   - Should be saved in password manager

2. **Use the diagnostic tool to test passwords:**
   ```bash
   python diagnose_auth.py
   ```
   - Test 6 lets you verify passwords interactively

3. **Reset the admin password:**
   ```bash
   # Option A: Delete database and re-initialize (loses all data)
   rm aegis.db .env
   ./setup_and_start.sh
   
   # Option B: Manually set new password
   python
   ```
   
   Then in Python:
   ```python
   import asyncio
   from sqlalchemy import select
   from db import AsyncSessionLocal
   from models import User
   from auth import hash_password
   
   async def reset():
       new_password = "YourNewPassword123"
       hashed = hash_password(new_password)
       
       async with AsyncSessionLocal() as session:
           result = await session.execute(
               select(User).filter(User.username == "admin")
           )
           admin = result.scalar_one()
           admin.hashed_password = hashed
           await session.commit()
       
       print(f"Password reset to: {new_password}")
   
   asyncio.run(reset())
   ```

---

### Issue 3: "User account is disabled"

**Cause:** Admin account was disabled

**Solution:**
```python
# In Python with virtual environment active:
import asyncio
from sqlalchemy import select
from db import AsyncSessionLocal
from models import User

async def enable():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).filter(User.username == "admin")
        )
        admin = result.scalar_one()
        admin.disabled = False
        await session.commit()
    print("Admin account enabled")

asyncio.run(enable())
```

---

### Issue 4: "Database file not found"

**Cause:** Database hasn't been initialized

**Solution:**
```bash
cd Server
source aegis/bin/activate
python init_db.py
```

---

### Issue 5: ".env file not found"

**Cause:** Environment variables not set up

**Solution:**
```bash
cd Server
./setup_and_start.sh
```

Or manually create `.env`:
```bash
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('AGENT_API_KEY=' + secrets.token_urlsafe(32))"

# Copy the output to .env file
```

---

### Issue 6: "Import Error" when running diagnostic

**Cause:** Virtual environment not activated or dependencies not installed

**Solution:**
```bash
# Activate virtual environment
cd Server
source aegis/bin/activate  # Linux/Mac
# OR
aegis\Scripts\activate     # Windows

# Install dependencies if needed
pip install -r requirments.txt
```

---

### Issue 7: Server returns 401 Unauthorized

**Possible causes:**
1. Wrong password
2. User doesn't exist
3. Account is disabled
4. JWT token expired

**Solution:**
Run diagnostic tool to identify exact cause:
```bash
python diagnose_auth.py
```

Use Test 8 (Login Simulation) to see exactly what's failing.

---

### Issue 8: Dashboard can't reach server

**Symptoms:**
- "Network Error" in browser console
- "Failed to fetch" errors
- Connection timeout

**Checks:**
1. Server is running on port 8000:
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status":"ok"}
   ```

2. Dashboard is configured correctly:
   ```bash
   # Check Dashboard/.env.local
   cat ../Dashboard/.env.local
   # Should have: NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
   ```

3. CORS is allowing dashboard:
   - Server should allow `http://localhost:3000`
   - Check server logs for CORS errors

---

### Issue 9: "Access denied" error

**Cause:** New security middleware blocking requests

**Check:**
1. Origin header is set correctly (automatic in browser)
2. API key is configured (if enabled)
3. Request is coming from localhost:3000

**Temporary disable for testing:**
```python
# In Server/app.py, comment out:
# app.add_middleware(BaseHTTPMiddleware, dispatch=security_middleware)
```

Then restart server and test login.

---

## Step-by-Step Login Troubleshooting

### Step 1: Verify Server is Running
```bash
# Check server is listening
curl http://localhost:8000/health

# Expected response:
{"status":"ok"}
```

### Step 2: Verify Dashboard is Running
```bash
# Dashboard should be on port 3000
# Open browser: http://localhost:3000
```

### Step 3: Run Full Diagnostic
```bash
cd Server
source aegis/bin/activate
python diagnose_auth.py
```

### Step 4: Test Login with Known Password
Use Test 8 in diagnostic tool:
- Enter username: `admin`
- Enter password: (your saved password)
- See if login would succeed

### Step 5: Check Browser Console
1. Open browser DevTools (F12)
2. Go to Console tab
3. Try to login
4. Look for errors:
   - Network errors → Server not running
   - 401 errors → Wrong credentials
   - 403 errors → Security middleware blocking
   - CORS errors → Origin not allowed

### Step 6: Check Server Logs
Look at server terminal output:
- `WARNING - Blocked request` → Security middleware
- `Login attempt for non-existent user` → Username wrong
- `Invalid password for user` → Password wrong
- `Successful authentication` → Login working!

---

## Testing Authentication Manually

### Test with curl (bypassing security):

**1. Get token:**
```bash
curl -X POST http://localhost:8000/api/v1/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=YourPasswordHere"
```

**Expected response (success):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Expected response (failure):**
```json
{
  "detail": "Incorrect username or password"
}
```

**2. Use token to access API:**
```bash
curl http://localhost:8000/api/v1/nodes \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## Emergency Password Reset

If you've lost the password and diagnostic confirms password is wrong:

```bash
# Complete reset (deletes all data):
cd Server
rm aegis.db .env
./setup_and_start.sh
# Save the new password shown!

# OR keep data, just reset password:
cd Server
source aegis/bin/activate
python

# Then in Python:
import asyncio
from sqlalchemy import select
from db import AsyncSessionLocal
from models import User
from auth import hash_password

async def reset():
    new_password = input("Enter new password: ")
    hashed = hash_password(new_password)
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).filter(User.username == "admin")
        )
        admin = result.scalar_one()
        admin.hashed_password = hashed
        await session.commit()
    
    print(f"✓ Password updated successfully!")
    print(f"New password: {new_password}")
    print("Save this password now!")

asyncio.run(reset())
```

---

## Need More Help?

1. **Run diagnostic tool first:** `python diagnose_auth.py`
2. **Check all tests pass**
3. **Use interactive password test** (Test 6)
4. **Try login simulation** (Test 8)
5. **Check browser console** for JavaScript errors
6. **Check server logs** for authentication errors

If diagnostic shows all tests passing but you still can't login:
- There might be a dashboard issue
- Check browser network tab for failed requests
- Verify dashboard environment variables
- Try different browser (clear cache)

---

## Quick Reference Commands

```bash
# Run diagnostic
cd Server && source aegis/bin/activate && python diagnose_auth.py

# Re-initialize database
cd Server && source aegis/bin/activate && python init_db.py

# Complete fresh start
cd Server && rm aegis.db .env && ./setup_and_start.sh

# Check server health
curl http://localhost:8000/health

# Test login endpoint
curl -X POST http://localhost:8000/api/v1/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=YOUR_PASSWORD"
```
