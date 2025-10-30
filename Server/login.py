# token.py

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

# --- Project-specific Imports for a flat structure ---
import auth
import schemas

router = APIRouter(
    prefix="/token",
    tags=["Authentication"],
)

# This is a placeholder for a real database user lookup.
# In a real app, you would create a User model and query your database.
FAKE_USERS_DB = {
    "admin": {
        "username": "admin",
        "hashed_password": auth.hash_password("password123"), # Store a hashed password
        "email": "admin@example.com",
        "full_name": "Admin User",
        "disabled": False,
    }
}

def get_user_from_db(username: str):
    """ A helper function to find a user in our fake database. """
    if username in FAKE_USERS_DB:
        user_dict = FAKE_USERS_DB[username]
        return user_dict
    return None


@router.post("", response_model=schemas.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    """
    Handles user login.
    Accepts form data (username, password), verifies credentials,
    and returns a JWT access token. This is the endpoint a frontend dashboard would call.
    """
    user = get_user_from_db(form_data.username)
    if not user or not auth.verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # The 'sub' (subject) of the token is typically the user's unique identifier.
    access_token = auth.create_jwt_token(
        data={"sub": user["username"]}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}