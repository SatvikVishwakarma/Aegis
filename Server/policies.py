# policies.py (Fully Updated)

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

# --- Project-specific Imports for a flat structure ---
import models
import schemas
from db import get_db

router = APIRouter(
    prefix="/policies",
    tags=["Policies"],
)


# --- Local Schema for Assignment ---
class PolicyAssignmentRequest(BaseModel):
    node_id: int
    policy_id: int


@router.post(
    "",
    response_model=schemas.PolicyResponse,
    status_code=status.HTTP_2_CREATED,
    summary="Create a New Policy",
)
async def create_policy(
    policy_in: schemas.PolicyRequest,
    db: AsyncSession = Depends(get_db),
):
    """ Creates a new policy in the database. """
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

    # Corrected: Explicitly validate the response to prevent errors
    return schemas.PolicyResponse.model_validate(new_policy)


@router.get(
    "",
    response_model=List[schemas.PolicyResponse],
    summary="List All Policies",
)
async def list_policies(db: AsyncSession = Depends(get_db)):
    """ Fetches all policies, preloading assigned nodes for efficiency. """
    stmt = select(models.Policy).options(selectinload(models.Policy.assigned_nodes))
    result = await db.execute(stmt)
    policies = result.scalars().unique().all()
    # Corrected: Validate each object in the list
    return [schemas.PolicyResponse.model_validate(p) for p in policies]


@router.get(
    "/{node_id}",
    response_model=List[schemas.PolicyResponse],
    summary="Get Policies for a Specific Node",
)
async def get_policies_for_node(node_id: int, db: AsyncSession = Depends(get_db)):
    """ Fetches a specific node and returns its list of assigned policies. """
    stmt = (
        select(models.Node)
        .where(models.Node.id == node_id)
        .options(selectinload(models.Node.policies).selectinload(models.Policy.assigned_nodes))
    )
    result = await db.execute(stmt)
    node = result.scalar_one_or_none()

    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node with ID {node_id} not found.",
        )
    # Corrected: Validate each policy object related to the node
    return [schemas.PolicyResponse.model_validate(p) for p in node.policies]


@router.post(
    "/assign",
    status_code=status.HTTP_200_OK,
    summary="Assign a Policy to a Node",
    response_model=schemas.NodeResponse,
)
async def assign_policy_to_node(
    assignment: PolicyAssignmentRequest,
    db: AsyncSession = Depends(get_db),
):
    """ Creates an association between a node and a policy. """
    node_stmt = (
        select(models.Node)
        .where(models.Node.id == assignment.node_id)
        .options(selectinload(models.Node.policies))
    )
    node_result = await db.execute(node_stmt)
    node = node_result.scalar_one_or_none()
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node with ID {assignment.node_id} not found.",
        )

    policy = await db.get(models.Policy, assignment.policy_id)
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Policy with ID {assignment.policy_id} not found.",
        )

    if policy not in node.policies:
        node.policies.append(policy)
        await db.commit()
        await db.refresh(node)

    # Corrected: Validate the returned Node object
    return schemas.NodeResponse.model_validate(node)


# --- THIS IS THE NEWLY ADDED ENDPOINT ---
@router.delete(
    "/{policy_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a Policy by ID",
    response_model=dict,
)
async def delete_policy(policy_id: int, db: AsyncSession = Depends(get_db)):
    """ Finds a policy by its unique ID and deletes it from the database. """
    policy_to_delete = await db.get(models.Policy, policy_id)

    if not policy_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Policy with ID {policy_id} not found."
        )

    await db.delete(policy_to_delete)
    await db.commit()

    return {"status": "success", "detail": f"Policy with ID {policy_id} deleted successfully"}