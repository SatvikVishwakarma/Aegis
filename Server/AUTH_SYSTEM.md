# Aegis Authentication System

## Overview

The Aegis authentication system has been completely rebuilt from scratch to ensure robust, secure, and reliable user authentication.

## Components

### 1. Password Hashing (`auth.py`)
- Uses **bcrypt** with 12 rounds for secure password hashing
- Each password gets a unique salt automatically
- Passwords are never stored in plain text
- Verification includes comprehensive error handling

### 2. Login Endpoint (`login.py`)
- OAuth2-compatible token endpoint
- Detailed logging for debugging
- Validates user exists, is enabled, and password is correct
- Returns JWT token on successful authentication

### 3. User Management (`manage_users.py`)
- Interactive CLI tool for managing users
- Features:
  - Create new users with validation
  - List all users
  - Change passwords
  - Enable/disable accounts
  - Delete users
- All operations include comprehensive error handling

### 4. Database Initialization (`init_db.py`)
- Creates database tables
- **No default users** - you must create your own
- Ensures fresh start with correct permissions

## Setup Process

### First-Time Setup

1. **Run the setup script:**
   ```bash
   cd Server
   chmod +x setup_and_start.sh
   ./setup_and_start.sh
   ```

2. **The script will:**
   - Create `.env` with secure random keys
   - Create virtual environment
   - Install dependencies
   - Initialize database (removes old one if exists)
   - Set correct database permissions
   - Prompt you to create your first user
   - Start the server

3. **Create your user account:**
   - Username (min 3 characters)
   - Email (must contain @)
   - Full Name (optional)
   - Password (min 6 characters)
   - Confirm password

4. **Login to dashboard:**
   - Go to http://your-server:3000
   - Use the credentials you just created

## Testing Authentication

Use the test script to verify everything works:

```bash
cd Server
source aegis/bin/activate
python test_auth.py
```

This will:
- Test password hashing
- Test password verification
- List all users in database
- Allow you to test password verification for each user

## Troubleshooting

### "Invalid credentials" error

**Run the diagnostic:**
```bash
cd Server
source aegis/bin/activate
python test_auth.py
```

When prompted, enter the password you think should work. The script will tell you if it's correct.

### Database permission errors

```bash
cd Server

# Fix ownership
sudo chown $USER:$USER aegis.db

# Fix permissions
chmod 664 aegis.db
```

### Can't create users

```bash
cd Server

# Remove old database and start fresh
rm -f aegis.db

# Activate environment
source aegis/bin/activate

# Reinitialize
python init_db.py

# Create user
python manage_users.py
```

### Password not working after creation

**Most common causes:**
1. Typo when creating password
2. Database permissions changed after user creation
3. Multiple database files exist

**Solution:**
1. List users: `python manage_users.py` → option 2
2. Change password: option 3
3. Test login again

## Security Best Practices

✅ **Implemented:**
- Bcrypt with 12 rounds (strong hashing)
- Unique salt per password
- No hardcoded credentials
- Environment variables for secrets
- JWT token-based authentication
- Password confirmation during creation

⚠️ **Recommended:**
- Use passwords of at least 12 characters
- Include uppercase, lowercase, numbers, and symbols
- Don't reuse passwords
- Change default generated API keys in production
- Use HTTPS in production

## Manual User Management

### Create a user
```bash
cd Server
source aegis/bin/activate
python manage_users.py
# Select option 1
```

### List users
```bash
python manage_users.py
# Select option 2
```

### Change password
```bash
python manage_users.py
# Select option 3
```

### Disable/Enable user
```bash
python manage_users.py
# Select option 4
```

### Delete user
```bash
python manage_users.py
# Select option 5
```

## Login Flow

1. **User enters credentials** in dashboard (username + password)
2. **Dashboard sends POST request** to `/api/v1/token` with form data
3. **Backend (`login.py`):**
   - Queries database for username
   - Checks if user exists and is enabled
   - Verifies password using bcrypt
   - Generates JWT token if valid
4. **Dashboard receives token** and stores in localStorage
5. **Subsequent requests** include token in Authorization header

## Files

- `auth.py` - Password hashing and JWT functions
- `login.py` - Login endpoint
- `manage_users.py` - User management CLI
- `init_db.py` - Database initialization
- `test_auth.py` - Authentication testing tool
- `models.py` - User database model
- `db.py` - Database configuration

## Environment Variables

Required in `.env` file:
- `SECRET_KEY` - For JWT signing (auto-generated)
- `AGENT_API_KEY` - For node authentication (auto-generated)
- `ALGORITHM` - JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token lifetime (default: 30)
- `DATABASE_URL` - Database connection string

## Support

If you continue to have issues:

1. Run `python test_auth.py` and share output
2. Check server logs when attempting login
3. Verify database file exists and has correct permissions
4. Ensure virtual environment is activated
5. Check `.env` file exists and has valid keys
