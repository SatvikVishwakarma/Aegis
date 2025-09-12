# app.py

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- Corrected Project-specific Imports ---
# These imports are now direct, matching your flat project structure
# where all .py files are in the same directory.

import logs
import nodes
import policies
from db import engine  # Correctly import 'engine' from db.py
from models import Base # Correctly import 'Base' from models.py

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Handles application startup and shutdown events.
    - On startup: Creates all database tables based on SQLAlchemy models.
    - On shutdown: The engine connection pool is automatically managed.
    """
    logger.info("Application startup...")
    logger.info("Initializing database and creating tables...")
    # This block was correct, but now relies on the corrected imports above
    async with engine.begin() as conn:
        try:
            # The `run_sync` method allows running synchronous SQLAlchemy
            # functions (like metadata creation) within an async context.
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully.")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            raise

    yield  # The application runs while the lifespan context is active

    logger.info("Application shutdown...")
    await engine.dispose()
    logger.info("Shutdown complete.")


# Initialize the FastAPI application with the lifespan manager
app = FastAPI(
    title="Security Monitoring Backend",
    description="API for monitoring security nodes, logs, and policies.",
    version="1.0.0",
    lifespan=lifespan,
)

# --- Middleware Configuration ---

# Define allowed origins for Cross-Origin Resource Sharing (CORS)
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8080",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- API Routers ---
# Include routers from the directly imported modules.
# A versioned API prefix is used as a best practice.
API_V1_PREFIX = "/api/v1"

app.include_router(nodes.router, prefix=API_V1_PREFIX)
app.include_router(logs.router, prefix=API_V1_PREFIX)
app.include_router(policies.router, prefix=API_V1_PREFIX)


# --- Health Check Endpoint ---

class HealthStatus(BaseModel):
    """Response model for the health check endpoint."""
    status: str = "ok"


@app.get(
    "/health",
    tags=["Health"],
    summary="Perform a health check",
    response_description="Returns the operational status of the API.",
    response_model=HealthStatus,
)
async def health_check() -> HealthStatus:
    """
    Endpoint to verify that the API is running and responsive.
    """
    return HealthStatus(status="ok")


# To run this application:
# 1. Make sure you have the required packages:
#    pip install fastapi "uvicorn[standard]" sqlalchemy pydantic aiosqlite
# 2. Ensure all your files (app.py, nodes.py, db.py, etc.) are in the same directory.
# 3. Run the server from your terminal in that directory:
#    uvicorn app:app --reload