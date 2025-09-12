# nodes.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Assuming a project structure where db, models, and schemas are accessible
# Example:
# /app
#  ├── api
#  │   └── nodes.py
#  ├── db.py
#  ├── models.py
#  └── schemas.py
from .. import models, schemas
from .db import get_db

router = APIRouter(
    prefix="/nodes",
    tags=["Nodes"],
)


@router.get(
    "",
    response_model=List[schemas.NodeResponse],
    summary="List All Nodes",
    description="Retrieves a list of all registered nodes and their current status.",
)
async def list_nodes(db: AsyncSession = Depends(get_db)):
    """
    Fetches all nodes from the database.
    """
    stmt = select(models.Node).order_by(models.Node.hostname)
    result = await db.execute(stmt)
    nodes = result.scalars().all()
    return nodes


@router.post(
    "/register",
    response_model=schemas.NodeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a New Node",
    description="Registers a new node or re-registers an existing one based on its hostname.",
)
async def register_node(
    node_in: schemas.NodeRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Handles node registration.

    - If the node (by hostname) does not exist, it is created.
    - If the node already exists, its IP address and last_seen time are updated.
    This handles agent re-registration gracefully (e.g., after a restart).
    """
    # Check if a node with the same hostname already exists
    stmt = select(models.Node).where(models.Node.hostname == node_in.hostname)
    result = await db.execute(stmt)
    existing_node = result.scalar_one_or_none()

    if existing_node:
        # Node exists, update it (re-registration)
        existing_node.ip_address = node_in.ip_address
        existing_node.status = "online"
        # The `last_seen` timestamp will be updated automatically by the model's
        # `onupdate` setting, but we can set it explicitly for clarity.
        # existing_node.last_seen = datetime.now(timezone.utc)
        
        await db.commit()
        await db.refresh(existing_node)
        # Return 200 OK for an update, FastAPI will handle this if not specified
        # in the decorator, but we'll return the object.
        return existing_node

    # Node does not exist, create a new one
    new_node = models.Node(
        hostname=node_in.hostname,
        ip_address=node_in.ip_address,
        status="online",
    )
    db.add(new_node)
    await db.commit()
    await db.refresh(new_node)
    
    return new_node


@router.post(
    "/heartbeat",
    response_model=schemas.NodeResponse,
    summary="Receive a Heartbeat from a Node",
    description="Updates a node's status to 'online' and refreshes its 'last_seen' timestamp.",
)
async def node_heartbeat(
    heartbeat_in: schemas.NodeHeartbeatRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Receives a heartbeat from an agent to indicate it is still active.
    """
    stmt = select(models.Node).where(models.Node.hostname == heartbeat_in.hostname)
    result = await db.execute(stmt)
    node = result.scalar_one_or_none()

    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node with hostname '{heartbeat_in.hostname}' not found. Please register the node first.",
        )

    # Update status and last_seen
    node.status = "online"
    # The onupdate=func.now() in the model handles this automatically,
    # but an explicit update is also fine.
    # node.last_seen = datetime.now(timezone.utc)
    
    await db.commit()
    await db.refresh(node)

    return node