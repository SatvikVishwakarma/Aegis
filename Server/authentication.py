"""
authentication.py - Brand New Authentication System
Simple, reliable password hashing and JWT token management.
"""

import os
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from jose import jwt, JWTError
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Header, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

load_dotenv()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
AGENT_API_KEY = os.getenv("AGENT_API_KEY", "")

# OAuth2 scheme for JWT token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def generate_password(length: int = 10) -> str:
    """
    Generate a secure random password.
    
    Args:
        length: Password length (default: 10)
        
    Returns:
        Random alphanumeric password
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to check against
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Optional custom expiration time
        
    Returns:
        JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT token.
    
    Args:
        token: JWT token to decode
        
    Returns:
        Decoded token data or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# ==============================================================================
# FastAPI Dependencies for Authentication
# ==============================================================================

async def get_current_user(
    token: str = Depends(oauth2_scheme)
) -> dict:
    """
    Validate JWT token and return current user data.
    Used as a FastAPI dependency for protected dashboard endpoints.
    
    Args:
        token: JWT token from Authorization header
        
    Returns:
        User data from token
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    return {
        "username": username,
        "user_id": payload.get("user_id"),
        "email": payload.get("email")
    }


async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> bool:
    """
    Verify agent API key for log ingestion endpoints.
    Used as a FastAPI dependency for agent/node authentication.
    
    Args:
        x_api_key: API key from X-API-Key header
        
    Returns:
        True if API key is valid
        
    Raises:
        HTTPException: If API key is missing or invalid
    """
    if not AGENT_API_KEY:
        # If no API key is configured, allow access (development mode)
        return True
    
    if x_api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if x_api_key != AGENT_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    return True
