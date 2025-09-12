# policies.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

# Assuming a project structure where db, models, and schemas are accessible
# Example:
# /app
#  ├── api
#  │   └── policies.py
#  ├── db.py
#  ├── models.py
#  └── schemas.py
from .. import models, schemas
from .db import get_db

router = APIRouter(
    prefix="/policies",
    tags=["Policies"],
)


# --- Local Schema for Assignment ---
# This schema is specific to the assignment endpoint.
class PolicyAssignmentRequest(BaseModel):
    node_id: int
    policy_id: int


@router.post(
    "",
    response_model=schemas.PolicyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a New Policy",
    description="Creates a new security policy with a unique name.",
)
async def create_policy(
    policy_in: schemas.PolicyRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Creates a new policy in the database.

    Prevents the creation of policies with duplicate names.
    """
    # Check for existing policy with the same name
    stmt = select(models.Policy).where(models.Policy.name == policy_in.name)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Policy with name '{policy_in.name}' already exists.",
        )

    new_policy = models.Policy(**policy_in.model_dump())
    db.add(new_policy)
    await db.commit()
    await db.refresh(new_policy)

    # Note: assigned_nodes will be empty for a new policy
    return new_policy


@router.get(
    "",
    response_model=List[schemas.PolicyResponse],
    summary="List All Policies",
    description="Retrieves a list of all existing policies and the nodes they are assigned to.",
)
async def list_policies(db: AsyncSession = Depends(get_db)):
    """
    Fetches all policies from the database, preloading the assigned nodes
    for an efficient response.
    """
    stmt = select(models.Policy).options(selectinload(models.Policy.assigned_nodes))
    result = await db.execute(stmt)
    policies = result.scalars().unique().all()
    return policies


@router.get(
    "/{node_id}",
    response_model=List[schemas.PolicyResponse],
    summary="Get Policies for a Specific Node",
    description="Retrieves all policies that are currently assigned to a given node ID.",
)
async def get_policies_for_node(node_id: int, db: AsyncSession = Depends(get_db)):
    """
    Fetches a specific node and returns its list of assigned policies.
    """
    # Eagerly load the 'policies' relationship to avoid extra queries
    stmt = (
        select(models.Node)
        .where(models.Node.id == node_id)
        .options(selectinload(models.Node.policies))
    )
    result = await db.execute(stmt)
    node = result.scalar_one_or_none()

    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node with ID {node_id} not found.",
        )

    return node.policies


@router.post(
    "/assign",
    status_code=status.HTTP_200_OK,
    summary="Assign a Policy to a Node",
    description="Assigns an existing policy to an existing node. Idempotent.",
    response_model=schemas.NodeResponse,
)
async def assign_policy_to_node(
    assignment: PolicyAssignmentRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Creates an association between a node and a policy.
    If the association already exists, it does nothing and returns success.
    """
    # Fetch the node and its current policies
    node_stmt = (
        select(models.Node)
        .where(models.Node.id == assignment.node_id)
        .options(selectinload(models.Node.policies)) # Eager load for checking
    )
    node_result = await db.execute(node_stmt)
    node = node_result.scalar_one_or_none()
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node with ID {assignment.node_id} not found.",
        )

    # Fetch the policy
    policy_stmt = select(models.Policy).where(models.Policy.id == assignment.policy_id)
    policy_result = await db.execute(policy_stmt)
    policy = policy_result.scalar_one_or_none()
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Policy with ID {assignment.policy_id} not found.",
        )

    # Check if the policy is already assigned to the node to avoid duplicates
    if policy in node.policies:
        # The assignment already exists, so we can return success
        return node

    # Create the new assignment
    node.policies.append(policy)
    await db.commit()
    await db.refresh(node)

    # Need to reload policies for the response model to be complete
    # Re-querying is one way, but we can also manually construct if needed
    stmt_refresh = (
        select(models.Node)
        .where(models.Node.id == node.id)
        .options(selectinload(models.Node.policies))
    )
    final_result = await db.execute(stmt_refresh)
    updated_node = final_result.scalar_one()

    return updated_node