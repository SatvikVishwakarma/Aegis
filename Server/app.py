# app.py (Fully Updated with fix)

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- Corrected Project-specific Imports ---
import logs
import nodes
import policies
import login # <-- 1. IMPORT THE RENAMED FILE
from db import engine
from models import Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """ Handles application startup and shutdown events. """
    logger.info("Application startup...")
    logger.info("Initializing database and creating tables...")
    async with engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully.")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            raise

    yield

    logger.info("Application shutdown...")
    await engine.dispose()
    logger.info("Shutdown complete.")


app = FastAPI(
    title="Security Monitoring Backend",
    description="API for monitoring security nodes, logs, and policies.",
    version="1.0.0",
    lifespan=lifespan,
)

# --- Middleware Configuration ---
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
API_V1_PREFIX = "/api/v1"

app.include_router(nodes.router, prefix=API_V1_PREFIX)
app.include_router(logs.router, prefix=API_V1_PREFIX)
app.include_router(policies.router, prefix=API_V1_PREFIX)
app.include_router(login.router, prefix=API_V1_PREFIX) # <-- 2. INCLUDE THE ROUTER FROM THE RENAMED FILE


# --- Health Check Endpoint ---
class HealthStatus(BaseModel):
    status: str = "ok"

@app.get(
    "/health",
    tags=["Health"],
    response_model=HealthStatus,
)
async def health_check() -> HealthStatus:
    return HealthStatus(status="ok")