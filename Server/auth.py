# auth.py

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

# --- Configuration Loading ---
# Load environment variables from a .env file for local development
load_dotenv()

# JWT Configuration
# Use a strong, randomly generated secret key in production.
# Command to generate a key: openssl rand -hex 32
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Static API Key for Agents/Nodes
# This should be a long, secure, randomly generated string.
AGENT_API_KEY = os.getenv("AGENT_API_KEY")

# --- Security Checks ---
# Ensure critical environment variables are set.
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable not set. JWT authentication will fail.")
if not AGENT_API_KEY:
    raise ValueError("AGENT_API_KEY environment variable not set. Agent authentication will fail.")

# --- Password Hashing ---
# Using passlib for secure password hashing. bcrypt is the recommended default.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hashes a plain-text password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


# ==============================================================================
# API Key Authentication (for Agents/Nodes)
# ==============================================================================

# Define the security scheme for the X-API-Key header
api_key_header_scheme = APIKeyHeader(name="X-API-Key", auto_error=True)


def verify_api_key(api_key: str = Security(api_key_header_scheme)):
    """
    FastAPI dependency to verify the agent's API key from the X-API-Key header.

    Raises:
        HTTPException(403): If the API key is invalid.
    """
    if api_key != AGENT_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API Key",
        )
    return True


# ==============================================================================
# JWT Authentication (for Dashboard Users)
# ==============================================================================

# Define the OAuth2 scheme for token retrieval (used by Swagger UI)
# The `tokenUrl` should point to your login/token endpoint.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/users/token")


def create_jwt_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JSON Web Token (JWT).

    Args:
        data: A dictionary to be encoded in the token's payload (e.g., {"sub": user.id}).
        expires_delta: An optional timedelta to specify token lifespan.
                       Defaults to ACCESS_TOKEN_EXPIRE_MINUTES from config.

    Returns:
        The encoded JWT as a string.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_jwt_token(token: str) -> Optional[dict]:
    """
    Decodes and verifies a JWT.

    Args:
        token: The JWT string to verify.

    Returns:
        The decoded payload as a dictionary if the token is valid, otherwise None.
    
    Raises:
        HTTPException(401): If the token is invalid, expired, or has a bad signature.
    """
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
    """
    FastAPI dependency to get the current user from a JWT.

    This function decodes the token, extracts the user identifier, and
    (in a real application) would fetch the full user object from the database.

    Args:
        token: The bearer token provided by the client.

    Returns:
        A dictionary representing the user's data from the token payload.
        In a real app, this would be a database model instance (e.g., User ORM object).
    
    Raises:
        HTTPException(401): If the token is invalid or the user does not exist.
    """
    payload = verify_jwt_token(token)
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: user identifier not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # --- Database Lookup Placeholder ---
    # In a real application, you would use `user_id` to fetch the user
    # from your database here to ensure they still exist and are active.
    # user = await get_user_by_id_from_db(user_id)
    # if user is None:
    #     raise HTTPException(status_code=404, detail="User not found")
    # return user
    # ------------------------------------
    
    # For this example, we return the payload's content directly.
    return {"id": user_id, **payload}


# Example of how to protect an endpoint
# from fastapi import APIRouter
#
# router = APIRouter()
#
# @router.get("/users/me")
# async def read_users_me(current_user: dict = Depends(get_current_user)):
#     return current_user
#
# @router.post("/agent/report")
# async def agent_report(is_valid_key: bool = Depends(verify_api_key)):
#     return {"message": "Agent report received successfully"}