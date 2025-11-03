# policies.py (With Password Confirmation for Deletions)

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
import schemas
import auth
from db import get_db

router = APIRouter(
    prefix="/policies",
    tags=["Policies"],
)


class PolicyAssignmentRequest(BaseModel):
    node_id: int
    policy_id: int


@router.post(
    "",
    response_model=schemas.PolicyResponse,
    status_code=status.HTTP_201_CREATED,
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
    # Get the ID to re-fetch the object with relationships loaded
    new_policy_id = new_policy.id

    # Eagerly load the object to prevent MissingGreenlet error
    stmt = (
        select(models.Policy)
        .where(models.Policy.id == new_policy_id)
        .options(selectinload(models.Policy.assigned_nodes))
    )
    result = await db.execute(stmt)
    final_policy = result.scalar_one()

    return schemas.PolicyResponse.model_validate(final_policy)


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
    
    # Re-fetch node to ensure all relationships are fresh for validation
    final_node_stmt = (
        select(models.Node)
        .where(models.Node.id == assignment.node_id)
        .options(selectinload(models.Node.policies))
    )
    final_result = await db.execute(final_node_stmt)
    final_node = final_result.scalar_one()

    return schemas.NodeResponse.model_validate(final_node)


@router.delete(
    "/{policy_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a Policy by ID",
    response_model=dict,
)
async def delete_policy(
    policy_id: int,
    delete_request: schemas.DeleteConfirmation,
    db: AsyncSession = Depends(get_db)
):
    """ 
    Deletes a policy by its unique ID.
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
    
    # Find and delete the policy
    policy_to_delete = await db.get(models.Policy, policy_id)

    if not policy_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Policy with ID {policy_id} not found."
        )

    await db.delete(policy_to_delete)
    await db.commit()

    return {"status": "success", "detail": f"Policy with ID {policy_id} deleted successfully"}