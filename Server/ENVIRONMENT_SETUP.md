# Environment Variables Setup Guide

## The Error

```
ValueError: SECRET_KEY environment variable not set. JWT authentication will fail.
```

This error occurs because the Aegis server requires environment variables for security (JWT tokens and API keys).

## Quick Solution

### Option 1: Automatic Setup (Recommended)

Run the setup script which will automatically create a `.env` file with secure random keys:

```bash
cd Server
bash setup_and_start.sh
```

The script will:
1. Create `.env` file with secure random SECRET_KEY and AGENT_API_KEY
2. Create virtual environment
3. Install dependencies
4. Initialize database
5. Start the server

### Option 2: Manual Setup

1. **Create `.env` file in the Server directory:**

```bash
cd Server
cp .env.example .env
```

2. **Edit `.env` and replace the placeholder values with secure random strings:**

```env
SECRET_KEY=your-super-secret-key-change-this-in-production
AGENT_API_KEY=your-agent-api-key-change-this-in-production
```

**Generate secure random keys:**

```bash
# Generate SECRET_KEY
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# Generate AGENT_API_KEY
python3 -c "import secrets; print('AGENT_API_KEY=' + secrets.token_urlsafe(32))"
```

3. **Initialize database and start server:**

```bash
source aegis/bin/activate
python init_db.py
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## Environment Variables Explained

| Variable | Purpose | Default |
|----------|---------|---------|
| `SECRET_KEY` | Used to sign JWT tokens for dashboard authentication | **Required** |
| `AGENT_API_KEY` | Used by nodes/agents to authenticate API requests | **Required** |
| `ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | How long JWT tokens are valid | `30` |
| `DATABASE_URL` | Database connection string | `sqlite+aiosqlite:///./aegis.db` |

## Security Notes

⚠️ **IMPORTANT:**
- Never commit `.env` file to git (already in `.gitignore`)
- Use different keys for development and production
- Keep `SECRET_KEY` and `AGENT_API_KEY` secure and secret
- Change default keys before deploying to production

## Troubleshooting

**Problem:** Script fails to create `.env` file

**Solution:** Create it manually using Option 2 above

**Problem:** `python-dotenv` not found

**Solution:** Install it:
```bash
pip install python-dotenv
```

**Problem:** Permission denied when running script

**Solution:** Make script executable:
```bash
chmod +x setup_and_start.sh
```
