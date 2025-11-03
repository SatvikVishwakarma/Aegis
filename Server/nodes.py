# nodes.py (With Password Confirmation for Deletions)

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import models
import schemas
import auth
from db import get_db
from websocket import manager

router = APIRouter(
    prefix="/nodes",
    tags=["Nodes"],
)

@router.get(
    "",
    response_model=List[schemas.NodeResponse],
    summary="List All Nodes",
)
async def list_nodes(db: AsyncSession = Depends(get_db)):
    """ Fetches all nodes from the database. """
    stmt = select(models.Node).order_by(models.Node.hostname)
    result = await db.execute(stmt)
    nodes = result.scalars().all()
    return [schemas.NodeResponse.model_validate(node) for node in nodes]

@router.post(
    "/register",
    response_model=schemas.NodeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a New Node",
)
async def register_node(
    node_in: schemas.NodeRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """ Handles node registration. """
    stmt = select(models.Node).where(models.Node.hostname == node_in.hostname)
    result = await db.execute(stmt)
    existing_node = result.scalar_one_or_none()

    if existing_node:
        existing_node.ip_address = node_in.ip_address
        existing_node.status = "online"
        await db.commit()
        await db.refresh(existing_node)
        
        # Broadcast update via WebSocket
        await manager.broadcast({
            "type": "node_updated",
            "data": schemas.NodeResponse.model_validate(existing_node).model_dump()
        })
        
        return schemas.NodeResponse.model_validate(existing_node)

    new_node = models.Node(
        hostname=node_in.hostname,
        ip_address=node_in.ip_address,
        status="online",
    )
    db.add(new_node)
    await db.commit()
    await db.refresh(new_node)
    
    # Broadcast new node via WebSocket
    await manager.broadcast({
        "type": "node_created",
        "data": schemas.NodeResponse.model_validate(new_node).model_dump()
    })
    
    return schemas.NodeResponse.model_validate(new_node)

@router.post(
    "/heartbeat",
    response_model=schemas.NodeResponse,
    summary="Receive a Heartbeat from a Node",
)
async def node_heartbeat(
    heartbeat_in: schemas.NodeHeartbeatRequest,
    db: AsyncSession = Depends(get_db),
):
    """ Receives a heartbeat from an agent to indicate it is still active. """
    stmt = select(models.Node).where(models.Node.hostname == heartbeat_in.hostname)
    result = await db.execute(stmt)
    node = result.scalar_one_or_none()

    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node with hostname '{heartbeat_in.hostname}' not found.",
        )

    node.status = "online"
    await db.commit()
    await db.refresh(node)
    return schemas.NodeResponse.model_validate(node)


# --- NEW ENDPOINT: UPDATE A NODE ---
@router.put(
    "/{node_id}",
    response_model=schemas.NodeResponse,
    summary="Update a Node's Details",
)
async def update_node(
    node_id: int,
    node_update: schemas.NodeUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """ Updates a node's editable fields (hostname, ip_address). """
    db_node = await db.get(models.Node, node_id)
    if not db_node:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")

    # Check for hostname conflict if hostname is being changed to a new value
    if node_update.hostname and node_update.hostname != db_node.hostname:
        stmt = select(models.Node).where(models.Node.hostname == node_update.hostname)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Hostname already registered by another node")
        db_node.hostname = node_update.hostname

    # Update IP address if a new one is provided
    if node_update.ip_address:
        db_node.ip_address = node_update.ip_address
    
    await db.commit()
    await db.refresh(db_node)
    return schemas.NodeResponse.model_validate(db_node)


# --- NEW ENDPOINT: DELETE A NODE ---
@router.delete(
    "/{node_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a Node by ID",
    response_model=dict,
)
async def delete_node(
    node_id: int,
    delete_request: schemas.DeleteConfirmation,
    db: AsyncSession = Depends(get_db)
):
    """ 
    Deletes a node by its unique ID.
    Requires admin password confirmation to prevent accidental deletions.
    """
    # Verify admin password
    result = await db.execute(
        select(models.User).where(models.User.username == "admin")
    )
    admin_user = result.scalar_one_or_none()
    
    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Admin user not found"
        )
    
    if not auth.verify_password(delete_request.password, admin_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin password"
        )
    
    # Find and delete the node
    db_node = await db.get(models.Node, node_id)
    if not db_node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found"
        )
    
    await db.delete(db_node)
    await db.commit()
    
    # Broadcast deletion via WebSocket
    await manager.broadcast({
        "type": "node_deleted",
        "data": {"id": node_id}
    })
    
    return {"status": "success", "detail": f"Node with ID {node_id} has been deleted"}