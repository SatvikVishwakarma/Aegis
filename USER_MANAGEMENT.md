# User Management Guide

## Overview

Aegis now includes a complete user management system with database-backed authentication. No more hardcoded credentials!

## Database Schema

Users are stored in the `users` table with the following fields:
- **id** - Unique user identifier
- **username** - Unique username (100 chars max)
- **email** - Unique email address (255 chars max)
- **full_name** - User's full name (optional)
- **hashed_password** - Bcrypt hashed password
- **disabled** - Account status (active/disabled)
- **created_at** - Account creation timestamp

## Initial Setup

### 1. Initialize Database

When you first run the server setup script, it will automatically create the database tables and a default admin user:

```bash
cd Server
chmod +x setup_and_start.sh
./setup_and_start.sh
```

The script will create:
- **Username:** admin
- **Password:** password123
- **Email:** admin@aegis.local

**⚠️ IMPORTANT:** Change the default password immediately after first login!

### 2. Manual Database Initialization

If you need to reinitialize the database:

```bash
cd Server
source aegis/bin/activate
python init_db.py
```

## Managing Users

### Using the CLI Tool

Aegis includes an interactive CLI tool for user management:

```bash
cd Server
source aegis/bin/activate
python manage_users.py
```

**Menu Options:**
1. **Create User** - Add a new user account
2. **List Users** - View all users in the system
3. **Change Password** - Update a user's password
4. **Enable/Disable User** - Activate or deactivate accounts
5. **Delete User** - Remove a user (cannot delete admin)

### Using the API

You can also manage users via the REST API:

#### Create User
```bash
POST /api/v1/users
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "password": "securepassword123"
}
```

#### List All Users
```bash
GET /api/v1/users
```

#### Get Specific User
```bash
GET /api/v1/users/{user_id}
```

#### Update User
```bash
PUT /api/v1/users/{user_id}
Content-Type: application/json

{
  "email": "newemail@example.com",
  "full_name": "John M. Doe",
  "password": "newpassword123",
  "disabled": false
}
```

#### Delete User
```bash
DELETE /api/v1/users/{user_id}
```

## Security Features

### Password Hashing
- All passwords are hashed using bcrypt
- Passwords are never stored in plain text
- Minimum password length: 8 characters

### JWT Authentication
- Login endpoint: `POST /api/v1/token`
- Returns JWT access token
- Token includes username in the 'sub' claim
- Protected endpoints require valid token

### Account Protection
- The default 'admin' user cannot be deleted
- Disabled accounts cannot log in
- Username and email must be unique

## Common Tasks

### Change Default Admin Password

**Option 1: Using CLI**
```bash
python manage_users.py
# Select: 3. Change Password
# Enter username: admin
# Enter new password
```

**Option 2: Using API**
```bash
PUT /api/v1/users/1
Content-Type: application/json

{
  "password": "new_secure_password"
}
```

### Create Additional Admin Users

```bash
python manage_users.py
# Select: 1. Create User
# Enter details for new admin account
```

### Disable User Account

```bash
python manage_users.py
# Select: 4. Enable/Disable User
# Enter username
# Confirm action
```

### Reset Forgotten Password

As an administrator, you can reset any user's password:

```bash
python manage_users.py
# Select: 3. Change Password
# Enter the username
# Set new password
```

## Database Location

The user data is stored in the SQLite database at:
```
Server/security_monitor.db
```

**Backup recommendation:** Regularly backup this file to prevent data loss.

## Migration from Hardcoded Users

If you're upgrading from the old hardcoded system:

1. Run `python init_db.py` to create the users table
2. The default admin user will be created automatically
3. Create additional users as needed using the CLI or API
4. The old `FAKE_USERS_DB` in `login.py` has been removed

## API Documentation

Full API documentation is available at:
```
http://localhost:8000/docs
```

Navigate to the "Users" section to see all user management endpoints with interactive testing.

## Troubleshooting

### "User already exists" Error
The username or email is already registered. Choose a different one.

### Cannot Login After Password Change
Ensure you're using the new password and that the account is not disabled.

### Database Locked Error
Only one process can write to SQLite at a time. Close other connections or use a production database like PostgreSQL.

### Lost Admin Password
1. Stop the server
2. Delete or rename `security_monitor.db`
3. Run `python init_db.py` to recreate with default credentials
4. **Note:** This will delete all data!

## Production Recommendations

### 1. Change Default Credentials Immediately
```bash
python manage_users.py
# Option 3: Change Password for admin
```

### 2. Use Strong Passwords
- Minimum 12 characters
- Mix of uppercase, lowercase, numbers, and symbols
- Avoid common words or patterns

### 3. Regular Backups
```bash
# Backup database
cp security_monitor.db security_monitor.db.backup

# Restore if needed
cp security_monitor.db.backup security_monitor.db
```

### 4. Consider PostgreSQL for Production
For multi-user production environments, migrate from SQLite to PostgreSQL:

```python
# In db.py, change:
SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/aegis"
```

### 5. Implement Password Expiry
Add a password expiry policy for enhanced security (requires custom implementation).

## Support

For issues or questions about user management:
- Check the API documentation at `/docs`
- Review the error messages in the terminal
- Check server logs for detailed error information
