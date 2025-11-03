# Aegis Security Architecture

## Overview

Aegis implements multiple layers of security to protect your monitoring infrastructure from unauthorized access. This document explains all security measures in place.

---

## Security Layers

### 1. **Localhost-Only Binding** 🔒

**What it does:**
- API server binds to `127.0.0.1` instead of `0.0.0.0`
- Server is **only accessible from the same machine**
- External network access is completely blocked at the network layer

**How it works:**
```bash
# Secure (current configuration)
uvicorn app:app --host 127.0.0.1 --port 8000

# Insecure (what we DON'T use)
# uvicorn app:app --host 0.0.0.0 --port 8000
```

**Protection:**
- ✅ Blocks all external network access
- ✅ Only localhost can connect
- ✅ Dashboard and API must be on same machine
- ✅ No firewall rules needed

**Impact:**
- API cannot be accessed from other devices on network
- API cannot be accessed from internet
- Only the dashboard (running on same machine) can communicate with API

---

### 2. **Origin/Referer Validation** 🌐

**What it does:**
- Validates that requests come from the dashboard
- Checks HTTP Referer and Origin headers
- Blocks direct browser access and curl commands

**Implementation:**
Located in `Server/security.py`:
```python
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

origin_valid = any(allowed_origin in (referer or origin) 
                   for allowed_origin in allowed_origins)
```

**Protection:**
- ✅ Blocks direct browser access (e.g., typing http://localhost:8000/api/v1/nodes)
- ✅ Blocks curl/wget/Postman without proper headers
- ✅ Allows only dashboard requests
- ✅ Logs all blocked attempts

**Bypass attempts blocked:**
```bash
# These will be BLOCKED:
curl http://localhost:8000/api/v1/nodes
firefox http://localhost:8000/api/v1/policies
wget http://localhost:8000/api/v1/events

# Only the dashboard can access the API
```

---

### 3. **Optional API Key Authentication** 🔑

**What it does:**
- Additional authentication layer for dashboard
- Requires `X-Dashboard-Key` header on all requests
- Key is auto-generated during setup

**Configuration:**
Enabled automatically in `.env`:
```bash
DASHBOARD_API_KEY=<64-character-random-string>
```

**How it works:**
1. Server generates random API key during setup
2. Dashboard reads key from environment variable
3. All dashboard requests include `X-Dashboard-Key` header
4. Server validates key on every request

**Protection:**
- ✅ Extra layer beyond origin checking
- ✅ Prevents header spoofing attacks
- ✅ Unique per installation
- ✅ Can be rotated if compromised

---

### 4. **JWT Token Authentication** 🎫

**What it does:**
- User must login to get access token
- Token required for all API operations
- Token expires after 30 minutes

**How it works:**
```typescript
// 1. User logs in
const token = await login(username, password)

// 2. Token stored in localStorage
localStorage.setItem('aegis_token', token.access_token)

// 3. Token sent with every request
headers: { Authorization: `Bearer ${token}` }

// 4. Server validates token
# Token contains: username, user_id, email, expiration
```

**Protection:**
- ✅ Prevents unauthorized API access
- ✅ Stateless authentication (no server-side sessions)
- ✅ Time-limited (30-minute expiration)
- ✅ Cryptographically signed (HS256)

---

### 5. **Password Confirmation for Deletions** ⚠️

**What it does:**
- Requires admin password before deleting nodes/policies
- Prevents accidental deletions
- Adds human-in-the-loop verification

**User Experience:**
```
User clicks "Delete Node" 
    ↓
Password prompt appears
    ↓
User enters admin password
    ↓
Backend verifies password
    ↓
If valid → Deletion proceeds
If invalid → 401 Unauthorized error
```

**Protection:**
- ✅ Prevents accidental deletions
- ✅ Confirms user intent
- ✅ Re-verifies authentication
- ✅ Audit trail of who deleted what

---

### 6. **CORS (Cross-Origin Resource Sharing)** 🚧

**What it does:**
- Restricts which domains can access the API
- Prevents cross-site request forgery (CSRF)
- Allows only specific origins

**Configuration:**
```python
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Protection:**
- ✅ Blocks requests from unauthorized websites
- ✅ Prevents CSRF attacks
- ✅ Allows only dashboard domain

---

### 7. **Bcrypt Password Hashing** 🔐

**What it does:**
- Passwords never stored in plaintext
- Uses bcrypt with 12 rounds (4,096 iterations)
- Each password has unique salt

**Implementation:**
```python
# Hashing (during setup)
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))

# Verification (during login/deletion)
valid = bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
```

**Protection:**
- ✅ Database compromise doesn't expose passwords
- ✅ Resistant to rainbow table attacks
- ✅ Slow hashing prevents brute force
- ✅ Industry-standard algorithm

---

## Security Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      EXTERNAL NETWORK                        │
│                                                               │
│  ❌ BLOCKED - Server binds to 127.0.0.1 only                │
└─────────────────────────────────────────────────────────────┘
                            ↑
                            │ Network layer blocks
                            │
┌───────────────────────────┴─────────────────────────────────┐
│                      LOCALHOST (127.0.0.1)                   │
│                                                               │
│  ┌──────────────────┐              ┌────────────────────┐   │
│  │   Dashboard      │              │   API Server       │   │
│  │  (Port 3000)     │◄────────────►│  (Port 8000)       │   │
│  │                  │              │                    │   │
│  │  - Sends         │              │  Security Checks:  │   │
│  │    Origin header │              │  1. Origin check ✓ │   │
│  │  - Sends API key │              │  2. API key ✓      │   │
│  │  - Sends JWT     │              │  3. JWT token ✓    │   │
│  └──────────────────┘              │  4. Password ✓     │   │
│                                     └────────────────────┘   │
│                                                               │
│  ❌ Direct browser access blocked:                          │
│     - No origin header from localhost:3000                   │
│     - Missing API key                                        │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## Attack Vectors & Mitigations

### Attack: Direct API Access via Browser
**Scenario:** User tries to access `http://localhost:8000/api/v1/nodes` directly

**Mitigation:**
1. Origin/Referer check fails (not from localhost:3000)
2. Request blocked with 403 Forbidden
3. Logged as security event

### Attack: curl/Postman Request
**Scenario:** Attacker tries to use curl from the same machine

```bash
curl http://localhost:8000/api/v1/nodes
```

**Mitigation:**
1. Missing Origin/Referer header → 403 Forbidden
2. Missing API key → 403 Forbidden
3. Missing JWT token → 401 Unauthorized

### Attack: External Network Access
**Scenario:** Attacker on same network tries to access API

```bash
curl http://192.168.1.100:8000/api/v1/nodes
```

**Mitigation:**
1. Server only listens on 127.0.0.1
2. Connection refused at network layer
3. Never reaches application

### Attack: Stolen JWT Token
**Scenario:** Attacker obtains valid JWT token

**Mitigation:**
1. Token expires after 30 minutes
2. Still needs API key in header
3. Still needs correct origin
4. Deletions require password re-verification

### Attack: Database Compromise
**Scenario:** Attacker gains access to `aegis.db` file

**Mitigation:**
1. Passwords are bcrypt hashed (can't be reversed)
2. Would need to brute force (very slow due to bcrypt)
3. File permissions prevent unauthorized access (chmod 664)

---

## Security Best Practices

### For Deployment

#### 1. **File Permissions**
```bash
# Restrict database access
chmod 600 aegis.db

# Protect environment file
chmod 600 .env

# Secure directories
chmod 700 Server/
```

#### 2. **Environment Variables**
```bash
# Never commit .env to git
echo ".env" >> .gitignore

# Rotate keys periodically
# Edit .env and restart server
```

#### 3. **Firewall Rules**
```bash
# Although localhost-only binding is sufficient,
# you can add extra firewall rules for defense-in-depth

# Ubuntu/Debian (ufw)
sudo ufw deny 8000
sudo ufw allow from 127.0.0.1 to any port 8000

# CentOS/RHEL (firewalld)
sudo firewall-cmd --zone=trusted --add-source=127.0.0.1/8
sudo firewall-cmd --zone=public --remove-port=8000/tcp
```

#### 4. **Monitoring & Logging**
```bash
# Server logs all security events
# Check logs regularly for blocked attempts

# Example log entries:
# WARNING - Blocked request from unauthorized origin
# WARNING - Blocked request with invalid API key
```

#### 5. **Regular Updates**
```bash
# Keep dependencies updated
cd Server
source aegis/bin/activate
pip install --upgrade pip
pip install -r requirments.txt --upgrade

# Keep Node.js packages updated
cd Dashboard
npm update
```

---

## Configuration Options

### Enable/Disable API Key Check

**To disable API key validation** (not recommended):
```bash
# Edit Server/.env
# Comment out or remove:
# DASHBOARD_API_KEY=...

# Server will only use Origin/Referer checking
```

### Change Allowed Origins

**To add additional dashboard URLs:**
```python
# Edit Server/security.py
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://yourdomain.com",  # Add custom domain
]
```

### Adjust Token Expiration

**To change JWT expiration time:**
```bash
# Edit Server/.env
ACCESS_TOKEN_EXPIRE_MINUTES=60  # Change from 30 to 60 minutes
```

---

## Testing Security

### Test 1: Verify Localhost-Only Binding
```bash
# From same machine - should fail
curl http://localhost:8000/api/v1/nodes
# Expected: 403 Forbidden (origin check failed)

# From another machine - should fail
curl http://192.168.1.X:8000/api/v1/nodes
# Expected: Connection refused (not listening on external interface)
```

### Test 2: Verify Origin Check
```bash
# Request without origin header
curl -X GET http://localhost:8000/api/v1/nodes
# Expected: 403 Forbidden

# Request with wrong origin
curl -X GET http://localhost:8000/api/v1/nodes \
  -H "Origin: http://evil.com"
# Expected: 403 Forbidden
```

### Test 3: Verify API Key
```bash
# Request without API key
curl -X GET http://localhost:8000/api/v1/nodes \
  -H "Origin: http://localhost:3000"
# Expected: 403 Forbidden (if API key is configured)
```

### Test 4: Verify JWT Authentication
```bash
# Request without JWT token
curl -X GET http://localhost:8000/api/v1/nodes \
  -H "Origin: http://localhost:3000" \
  -H "X-Dashboard-Key: YOUR_KEY_HERE"
# Expected: 401 Unauthorized
```

---

## Security Checklist

Before deploying to production:

- [ ] Server binds to `127.0.0.1` only (check `setup_and_start.sh`)
- [ ] `.env` file has secure random keys
- [ ] `.env` file is not committed to git
- [ ] Database file has restrictive permissions (600)
- [ ] Admin password is saved in password manager
- [ ] API key is configured in `.env`
- [ ] CORS origins are correctly configured
- [ ] All dependencies are up to date
- [ ] Firewall rules are in place (optional but recommended)
- [ ] Security logging is enabled
- [ ] Regular backups are configured

---

## FAQ

### Q: Can I access the API from a mobile app?
**A:** Not with the current configuration. The API is localhost-only. You would need to:
1. Change binding from `127.0.0.1` to `0.0.0.0`
2. Configure HTTPS/TLS
3. Add mobile app origin to CORS
4. Implement additional security (rate limiting, IP whitelist)

### Q: Can I use the API from a different machine?
**A:** No, by design. This is a security feature. If you need remote access:
1. Use SSH tunneling: `ssh -L 8000:localhost:8000 user@server`
2. Or use VPN to access the machine
3. Dashboard and API should remain on same machine

### Q: What if someone gets access to my machine?
**A:** If someone has local access to your machine, they can:
- Access the dashboard (if logged in)
- Read the database file (if file permissions not set)
- They still need admin password for deletions

**Defense:**
- Use full-disk encryption
- Require login for OS
- Set restrictive file permissions
- Use screen lock

### Q: Is HTTPS required?
**A:** For localhost-only deployment, HTTPS is not strictly necessary because traffic never leaves the machine. However, for production deployments where API might be accessed remotely, HTTPS is **mandatory**.

### Q: How do I rotate the API keys?
**A:**
```bash
# 1. Generate new keys
cd Server
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('DASHBOARD_API_KEY=' + secrets.token_urlsafe(32))"

# 2. Update .env file with new keys

# 3. Restart server
# All users will need to login again (JWT secret changed)
```

---

## Conclusion

Aegis implements **defense-in-depth** security:
1. **Network isolation** (localhost-only)
2. **Origin validation** (referer/origin checks)
3. **API key authentication** (dashboard key)
4. **User authentication** (JWT tokens)
5. **Password hashing** (bcrypt)
6. **Deletion confirmation** (password re-verification)

This multi-layered approach ensures that even if one layer is bypassed, others remain in place to protect your infrastructure.

For questions or security concerns, please open an issue on GitHub.
