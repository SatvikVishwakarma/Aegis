# db.py

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# Assuming your SQLAlchemy models are defined in a 'models.py' file
# and inherit from a common 'Base' declarative base class.
from models import Base

# --- Database Configuration ---

# Use an environment variable for the database file, with a sensible default.
DATABASE_FILE = os.getenv("DATABASE_FILE", "security_monitor.db")
SQLALCHEMY_DATABASE_URL = f"sqlite+aiosqlite:///./{DATABASE_FILE}"

# --- SQLAlchemy Engine and Session Setup ---

# Create the asynchronous engine for SQLAlchemy.
# - echo=False is recommended for production to avoid logging every SQL statement.
# - future=True is the default in SQLAlchemy 2.0 and enables the new API style.
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,  # Set to True for debugging SQL queries
)

# Create an async session factory (SessionLocal).
# This factory will be used to create new AsyncSession objects for each request.
# - expire_on_commit=False prevents attributes from being expired after commit,
#   which is useful in async contexts where you might need the object after commit.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db():
    """
    Initializes the database by creating all tables defined in the models.
    This function should be called during application startup (e.g., in a
    FastAPI lifespan event).
    """
    async with engine.begin() as conn:
        # The `run_sync` method allows running synchronous SQLAlchemy
        # functions (like metadata creation) within an async context.
        await conn.run_sync(Base.metadata.create_all)


# --- FastAPI Dependency ---

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides a database session for a single request.

    This is an async generator that creates a new AsyncSession, yields it to
    the endpoint, and ensures it's closed in a finally block, correctly
    returning the connection to the pool.

    Usage in an endpoint:
        @router.post("/")
        async def create_item(item: ItemSchema, db: AsyncSession = Depends(get_db)):
            # ... use `db` session here ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            # If all operations are successful, the transaction is automatically
            # committed by the `async with` block's exit.
        except Exception:
            # On any exception, the transaction is automatically rolled back.
            await session.rollback()
            raise
        finally:
            # The session is automatically closed on exiting the `async with` block.
            await session.close()