# login.py - User Authentication Endpoint

from typing import Annotated
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Project imports
import auth
import schemas
import models
from db import get_db

# Setup logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/token",
    tags=["Authentication"],
)


async def authenticate_user(username: str, password: str, db: AsyncSession):
    """
    Authenticate a user by username and password.
    
    Args:
        username: Username to authenticate
        password: Plain text password to verify
        db: Database session
    
    Returns:
        User object if authentication successful, None otherwise
    """
    try:
        # Query user from database
        result = await db.execute(
            select(models.User).where(models.User.username == username)
        )
        user = result.scalar_one_or_none()
        
        # User not found
        if not user:
            logger.warning(f"Login attempt for non-existent user: {username}")
            return None
        
        # User is disabled
        if user.disabled:
            logger.warning(f"Login attempt for disabled user: {username}")
            return None
        
        # Verify password
        password_valid = auth.verify_password(password, user.hashed_password)
        
        if not password_valid:
            logger.warning(f"Invalid password for user: {username}")
            return None
        
        logger.info(f"Successful authentication for user: {username}")
        return user
        
    except Exception as e:
        logger.error(f"Authentication error for user {username}: {e}")
        return None


@router.post("", response_model=schemas.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db)
):
    """
    OAuth2 compatible token login endpoint.
    
    Accepts form data with username and password.
    Returns JWT access token if credentials are valid.
    """
    # Authenticate user
    user = await authenticate_user(form_data.username, form_data.password, db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = auth.create_jwt_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "email": user.email
        }
    )
    
    logger.info(f"Token issued for user: {user.username}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }