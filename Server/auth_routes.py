"""
auth_routes.py - Fresh Authentication Routes
Clean, simple login endpoint.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from models import User
from schemas import Token
from authentication import verify_password, create_access_token, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db)
):
    """
    Login endpoint - authenticate and return JWT token.
    
    Args:
        form_data: Username and password from form
        db: Database session
        
    Returns:
        Access token and token type
        
    Raises:
        HTTPException: If credentials are invalid
    """
    logger.info(f"Login attempt: username={form_data.username}")
    
    # Get user from database
    result = await db.execute(
        select(User).where(User.username == form_data.username)
    )
    user = result.scalar_one_or_none()
    
    # Validate user exists
    if not user:
        logger.warning(f"Login failed: user not found - {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if account is disabled
    if user.disabled:
        logger.warning(f"Login failed: account disabled - {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Login failed: invalid password - {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "email": user.email
        }
    )
    
    logger.info(f"Login successful: {form_data.username}")
    
    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/verify")
async def verify_token(current_user: dict = Depends(get_current_user)):
    """
    Verify if the current token is valid.
    
    Returns:
        User information
    """
    return {"status": "valid", "user": current_user}
