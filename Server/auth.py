# auth.py - Authentication and Password Management

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from jose import JWTError, jwt

# --- Configuration Loading ---
load_dotenv()

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Static API Key for Agents/Nodes
AGENT_API_KEY = os.getenv("AGENT_API_KEY")

# --- Security Checks ---
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable not set. JWT authentication will fail.")
if not AGENT_API_KEY:
    raise ValueError("AGENT_API_KEY environment variable not set. Agent authentication will fail.")

# ==============================================================================
# Password Hashing (Using bcrypt)
# ==============================================================================

def hash_password(password: str) -> str:
    """
    Hashes a plain-text password using bcrypt.
    Always generates a new salt for each password.
    Returns a string that can be stored in the database.
    """
    # Convert password to bytes
    password_bytes = password.encode('utf-8')
    
    # Generate salt and hash (bcrypt handles salt automatically)
    salt = bcrypt.gensalt(rounds=12)  # 12 rounds is a good balance of security and speed
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Return as string for database storage
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against a bcrypt hashed password.
    Returns True if password matches, False otherwise.
    
    Args:
        plain_password: The password provided by the user (plain text)
        hashed_password: The hashed password from the database
    
    Returns:
        bool: True if password is correct, False otherwise
    """
    try:
        # Convert both to bytes
        plain_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        
        # Use bcrypt to check password
        result = bcrypt.checkpw(plain_bytes, hashed_bytes)
        
        return result
    except Exception as e:
        # If any error occurs during verification, treat as invalid password
        print(f"Password verification error: {e}")
        return False

# ==============================================================================
# API Key Authentication (for Agents/Nodes)
# ==============================================================================
api_key_header_scheme = APIKeyHeader(name="X-API-Key", auto_error=True)

def verify_api_key(api_key: str = Security(api_key_header_scheme)):
    """FastAPI dependency to verify the agent's API key."""
    if api_key != AGENT_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API Key",
        )
    return True

# ==============================================================================
# JWT Authentication (for Dashboard Users)
# ==============================================================================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/token")

def create_jwt_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Creates a JSON Web Token (JWT)."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_jwt_token(token: str) -> Optional[dict]:
    """Decodes and verifies a JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise credentials_exception

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """FastAPI dependency to get the current user from a JWT."""
    payload = verify_jwt_token(token)
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: user identifier not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"id": user_id, **payload}