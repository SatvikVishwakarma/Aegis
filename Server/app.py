# app.py (Fully Updated with WebSocket and Agent Builder support)

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- Corrected Project-specific Imports ---
import logs
import nodes
import policies
import auth_routes  # NEW authentication
import agent_routes  # Agent package builder
from db import engine
from models import Base
from websocket import manager

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
# Allow all origins for development (use specific origins in production)
origins = ["*"]

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
app.include_router(auth_routes.router, prefix=API_V1_PREFIX)  # NEW authentication
app.include_router(agent_routes.router, prefix=API_V1_PREFIX)  # Agent package builder


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


# --- WebSocket Endpoint ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates.
    Clients connect here to receive live node and event updates.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and receive any client messages
            data = await websocket.receive_text()
            # Echo back or handle client messages if needed
            await manager.send_personal_message(
                {"type": "pong", "message": "Connection alive"}, 
                websocket
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")