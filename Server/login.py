# login.py

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# --- Project-specific Imports for a flat structure ---
import auth
import schemas
import models
from db import get_db

router = APIRouter(
    prefix="/token",
    tags=["Authentication"],
)


async def get_user_from_db(username: str, db: AsyncSession):
    """Get a user from the database by username."""
    result = await db.execute(
        select(models.User).where(models.User.username == username)
    )
    return result.scalar_one_or_none()


@router.post("", response_model=schemas.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db)
):
    """
    Handles user login.
    Accepts form data (username, password), verifies credentials,
    and returns a JWT access token.
    """
    user = await get_user_from_db(form_data.username, db)
    if not user or user.disabled or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # The 'sub' (subject) of the token is typically the user's unique identifier.
    access_token = auth.create_jwt_token(
        data={"sub": user.username}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}