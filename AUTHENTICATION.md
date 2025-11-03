# Aegis Authentication System

## Overview

Aegis uses a **single admin account** authentication system designed for simplicity and security. This document explains how authentication works, how passwords are generated, and how to manage your admin account.

---

## Architecture

### Single Admin Account Model

Unlike traditional multi-user systems, Aegis implements a single admin account approach:
- **One account per installation**
- **Auto-generated secure password**
- **No user registration or account creation**
- **Password confirmation for destructive operations**

**Why this approach?**
- Aegis is designed for single-administrator deployments
- Reduces complexity and potential security vulnerabilities
- Eliminates the need for user management UI
- Focuses on what matters: monitoring and policy management

### Authentication Flow

```
Setup → Auto-generate password → Display once → User saves → Login → JWT token
```

1. **Setup Phase:**
   - `init_db.py` creates admin account
   - Password generated using Python's `secrets` module
   - Password hashed with bcrypt (12 rounds)
   - Stored in SQLite database

2. **Login Phase:**
   - User enters username (`admin`) and password
   - Backend verifies password using bcrypt
   - JWT token issued (expires in 30 minutes)
   - Token used for subsequent API calls

3. **Deletion Confirmation:**
   - User attempts to delete node/policy
   - Dashboard prompts for password
   - Backend re-verifies password
   - Operation proceeds if valid, returns 401 if invalid

---

## Password Generation

### Implementation Details

**Location:** `Server/init_db.py`

**Function:**
```python
def generate_secure_password(length=10):
    characters = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password
```

**Characteristics:**
- **Length:** 10 characters
- **Character Set:** `A-Z`, `a-z`, `0-9` (62 possible characters)
- **Entropy:** ~59.5 bits (62^10 ≈ 8.4 × 10^17 combinations)
- **Module:** Python's `secrets` (cryptographically strong random)
- **No Special Characters:** Avoids copy/paste issues

**Example passwords:**
- `aB3xK9mL2n`
- `7QwErTy8Ui`
- `pL9mNbV2cX`

### Why No Special Characters?

We deliberately exclude special characters (`!@#$%^&*`) because:
1. **Easier to type manually** when needed
2. **No shell escaping issues** in terminal contexts
3. **Universal compatibility** across all systems
4. **Still very secure** with 10 alphanumeric characters

### Security Analysis

**Is 10 characters enough?**

Yes! Here's why:
- **62^10 combinations** = 839,299,365,868,340,224 possible passwords
- **Time to crack (1 billion attempts/sec):** ~26,000 years
- **bcrypt slows down** brute force attacks significantly
- **Account lockout** can be added for additional protection

---

## Password Storage

### Hashing with bcrypt

**Location:** `Server/auth.py`

**Implementation:**
```python
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')
```

**Parameters:**
- **Algorithm:** bcrypt
- **Rounds:** 12 (4,096 iterations)
- **Salt:** Randomly generated per password
- **Encoding:** UTF-8

**Database Storage:**
- Plaintext password: **NEVER stored**
- Hashed password: Stored in `users.hashed_password` column
- Hash length: 60 characters (bcrypt standard)

### Verification Process

**Function:**
```python
def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        print(f"Password verification error: {e}")
        return False
```

**Used in:**
1. **Login endpoint** (`Server/login.py`)
2. **Delete node endpoint** (`Server/nodes.py`)
3. **Delete policy endpoint** (`Server/policies.py`)

---

## Setup Process

### Step-by-Step Flow

**1. Run Setup Script:**
```bash
cd Server
./setup_and_start.sh
```

**2. Script Execution:**
```bash
# Creates .env with SECRET_KEY and AGENT_API_KEY
# Creates virtual environment
# Installs dependencies
# Runs init_db.py → Creates admin account
```

**3. Password Display:**
```
================================================================================
                      IMPORTANT: ADMIN ACCOUNT CREATED
================================================================================

Your admin account has been created with the following credentials:

  Username: admin
  Password: aB3xK9mL2n

⚠️  CRITICAL: Save this password NOW! ⚠️

This password will NOT be shown again. If you lose it, you will need to
reset the database and lose all your data.

Press Enter once you have saved the password to continue...
================================================================================
```

**4. User Action:**
- **Copy password** to password manager or secure note
- **Press Enter** to continue
- Server starts on port 8000

**5. Dashboard Login:**
- Navigate to `http://localhost:3000`
- Username: `admin`
- Password: (the saved password)

### Environment Variables

**Generated in `.env`:**
```bash
SECRET_KEY=<64-character hex string>
AGENT_API_KEY=<64-character hex string>
```

**Used for:**
- `SECRET_KEY`: JWT token signing
- `AGENT_API_KEY`: Agent authentication (future use)

---

## Deletion Protection

### Why Password Confirmation?

Prevents accidental deletions by requiring authentication for destructive operations:
- **User intent verification:** Ensures deliberate action
- **Security layer:** Prevents unauthorized deletions
- **Audit trail:** Confirms admin performed the action

### Implementation

**Backend (Server/nodes.py):**
```python
@router.delete("/{node_id}")
async def delete_node(
    node_id: int,
    confirmation: schemas.DeleteConfirmation,
    db: AsyncSession = Depends(get_db)
):
    # Get admin user
    result = await db.execute(select(User).filter(User.username == "admin"))
    admin_user = result.scalar_one_or_none()
    
    if not admin_user:
        raise HTTPException(status_code=500, detail="Admin user not found")
    
    # Verify password
    if not auth.verify_password(confirmation.password, admin_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid password")
    
    # Proceed with deletion...
```

**Frontend (Dashboard/src/app/dashboard/nodes/page.tsx):**
```typescript
const handleDelete = (id: number) => {
  const password = prompt('Enter admin password to confirm deletion:');
  
  if (!password) {
    return; // User cancelled
  }
  
  deleteMutation.mutate({ id, password });
};
```

**User Experience:**
1. User clicks "Delete" button
2. Browser prompts for password
3. User enters password
4. Backend verifies password
5. If valid → deletion proceeds
6. If invalid → 401 error shown

### Error Handling

**Backend Responses:**
- `401 Unauthorized`: Invalid password
- `404 Not Found`: Node/policy doesn't exist
- `500 Internal Server Error`: Admin user not found (database issue)

**Frontend Display:**
```typescript
onError: (error: any) => {
  const message = error.response?.data?.detail || 'Failed to delete node';
  alert(message); // Shows specific error
}
```

---

## Lost Password Recovery

### Option 1: Database Reset (Recommended)

**⚠️ Warning:** This deletes ALL data (nodes, policies, events)

**Steps:**
```bash
# 1. Stop the server (Ctrl+C)

# 2. Delete database and environment
cd Server
rm aegis.db .env

# 3. Re-run setup
./setup_and_start.sh

# 4. Save new password
```

**What happens:**
- New database created
- New admin account with new password
- Fresh start with no data

### Option 2: Manual Password Reset (Advanced)

**⚠️ Requires database access**

**Steps:**
```bash
# 1. Activate virtual environment
cd Server
source aegis/bin/activate  # Linux/Mac
# OR
aegis\Scripts\activate     # Windows

# 2. Run user management tool
python manage_users.py

# 3. Select "Update User Password"
# 4. Username: admin
# 5. Enter new password
```

**What happens:**
- Password updated in database
- All data preserved
- You choose the new password

### Option 3: Direct Database Manipulation

**⚠️ For experts only**

**Steps:**
```python
# 1. Open Python with virtual environment active
python

# 2. Run this script:
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from db import AsyncSessionLocal, engine
from models import User
from auth import hash_password

async def reset_password():
    new_password = "your-new-password"  # Choose a password
    hashed = hash_password(new_password)
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).filter(User.username == "admin")
        )
        admin = result.scalar_one()
        admin.hashed_password = hashed
        await session.commit()
    
    print(f"Password updated to: {new_password}")

asyncio.run(reset_password())
```

---

## Security Best Practices

### 1. Password Storage

**✅ DO:**
- Use a password manager (1Password, Bitwarden, LastPass)
- Store in encrypted notes
- Keep offline backup in secure location

**❌ DON'T:**
- Store in plaintext files
- Email to yourself
- Save in browser (can be extracted)
- Write on sticky notes

### 2. Access Control

**✅ DO:**
- Use HTTPS in production (TLS/SSL)
- Implement IP whitelisting if possible
- Enable firewall rules for port 8000
- Use VPN for remote access

**❌ DON'T:**
- Expose to public internet without HTTPS
- Use default ports without firewall
- Share password via unsecured channels

### 3. JWT Tokens

**Current Settings:**
- Token expiration: 30 minutes
- Algorithm: HS256 (HMAC with SHA-256)
- Secret: Random 64-character hex

**Recommendations:**
- Keep SECRET_KEY secure
- Don't commit `.env` to version control
- Rotate SECRET_KEY periodically (requires re-login)

### 4. Database Security

**✅ DO:**
- Regular backups of `aegis.db`
- Set proper file permissions (chmod 600)
- Keep database in secure directory

**❌ DON'T:**
- Expose database file to web server
- Share database file (contains hashed passwords)

---

## API Reference

### Login Endpoint

**POST** `/api/login/token`

**Request:**
```json
{
  "username": "admin",
  "password": "aB3xK9mL2n"
}
```

**Response (Success):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Response (Error):**
```json
{
  "detail": "Incorrect username or password"
}
```

### Delete Node (with Password)

**DELETE** `/api/nodes/{node_id}`

**Request:**
```json
{
  "password": "aB3xK9mL2n"
}
```

**Response (Success):**
```json
{
  "message": "Node deleted successfully"
}
```

**Response (Invalid Password):**
```json
{
  "detail": "Invalid password"
}
```

### Delete Policy (with Password)

**DELETE** `/api/policies/{policy_id}`

**Request:**
```json
{
  "password": "aB3xK9mL2n"
}
```

**Response (Success):**
```json
{
  "message": "Policy deleted successfully"
}
```

**Response (Invalid Password):**
```json
{
  "detail": "Invalid password"
}
```

---

## Troubleshooting

### "Invalid username or password"

**Possible Causes:**
1. Wrong password (typo or wrong saved password)
2. Database not initialized
3. Admin user doesn't exist

**Solutions:**
```bash
# Check if admin user exists
cd Server
source aegis/bin/activate
python manage_users.py
# Select "List Users" - should show admin

# If no admin user, reset database
rm aegis.db .env
./setup_and_start.sh
```

### "Admin user not found" (during deletion)

**Cause:** Database corruption or admin user deleted

**Solution:**
```bash
# Reset database
cd Server
rm aegis.db .env
./setup_and_start.sh
```

### Password prompt not appearing

**Cause:** Browser blocking JavaScript prompt

**Solutions:**
1. Check browser console for errors
2. Ensure JavaScript enabled
3. Try different browser
4. Check for browser extensions blocking prompts

### JWT token expired

**Symptoms:** Logged out automatically, API returns 401

**Solution:** This is normal behavior (30-minute expiration)
- Simply log in again
- Token refreshes automatically

### Can't remember if password was saved

**Prevention:**
- Always use password manager
- Test login immediately after setup
- Keep backup in secure location

**Recovery:**
- Database reset (lose all data)
- Manual password reset (preserve data)

---

## Future Enhancements

Potential improvements to consider:

### 1. Password Reset Token
- Email-based password reset
- Temporary reset links
- Requires email configuration

### 2. Two-Factor Authentication (2FA)
- TOTP support (Google Authenticator)
- Backup codes
- Enhanced security for public deployments

### 3. Session Management
- Active session list
- Remote logout
- Session timeout settings

### 4. Audit Logging
- Track login attempts
- Log deletion operations
- IP address logging

### 5. Account Lockout
- Temporary lockout after failed attempts
- Configurable threshold
- Automatic unlock timer

---

## Comparison: Old vs New System

### Old System (Deprecated)

**Setup Flow:**
```
Setup → Prompt user → Create account → Validate → Start server
```

**Issues:**
- User had to create account during setup
- Potential for weak passwords
- Manual password entry errors
- Setup could fail if user input invalid

### New System (Current)

**Setup Flow:**
```
Setup → Auto-generate → Display once → Start server
```

**Advantages:**
- ✅ Always secure password
- ✅ No user input errors
- ✅ Faster setup
- ✅ Single admin account (appropriate for use case)
- ✅ Deletion protection added

---

## Conclusion

The Aegis authentication system is designed for:
- **Simplicity:** One admin account, auto-generated password
- **Security:** Cryptographically strong password, bcrypt hashing, deletion confirmation
- **Reliability:** No user input errors, consistent setup process

**Remember:**
1. **Save your password** during setup (only shown once)
2. **Use a password manager** for secure storage
3. **Test login immediately** after setup
4. **Keep database backups** for disaster recovery

For questions or issues, refer to the troubleshooting section or open an issue on GitHub.
