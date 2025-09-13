# logs.py

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# --- Corrected Project-specific Imports for a flat structure ---
import models
import rules
import schemas
from auth import get_current_user, verify_api_key
from db import get_db

router = APIRouter(
    prefix="/logs",
    tags=["Logs"],
)


# --- Response Schema for the Ingest Endpoint ---
# This custom schema returns the created event and any triggered rules.
class EventIngestResponse(BaseModel):
    created_event: schemas.EventResponse
    triggered_rules: List[str]


@router.post(
    "/ingest",
    response_model=EventIngestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest a Security Event from an Agent",
    description="Receives a single event from a node, evaluates it against detection rules, and stores it.",
)
async def ingest_log(
    event_in: schemas.EventIngestRequest,
    db: AsyncSession = Depends(get_db),
    # This endpoint is protected. Only agents with a valid API key can submit logs.
    is_valid_key: bool = Depends(verify_api_key),
):
    """
    Ingests, analyzes, and stores a security event.

    1.  Validates that the source node exists.
    2.  Converts the incoming Pydantic schema to a dictionary for rule evaluation.
    3.  Passes the event to the `evaluate_event` function.
    4.  Creates a new Event record in the database.
    5.  Returns the created event and a list of any triggered rule names.
    """
    # 1. Validate that the node exists before ingesting its event
    node_exists = await db.get(models.Node, event_in.node_id)
    if not node_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node with ID {event_in.node_id} not found. Cannot ingest event.",
        )

    # 2. Evaluate the event against detection rules
    # Convert Pydantic model to a dict for the rule engine
    event_dict = event_in.model_dump()
    triggered_rules = rules.evaluate_event(event_dict)

    # 3. Create and store the new event record
    new_event = models.Event(
        node_id=event_in.node_id,
        event_type=event_in.event_type,
        severity=event_in.severity,
        details=event_in.details,
    )
    db.add(new_event)
    await db.commit()
    await db.refresh(new_event)

    # 4. Return the comprehensive response
    return EventIngestResponse(
        created_event=new_event,
        triggered_rules=triggered_rules
    )


@router.get(
    "",
    response_model=List[schemas.EventResponse],
    summary="Query Stored Events",
    description="Retrieves a list of events with powerful filtering options.",
)
async def get_logs(
    db: AsyncSession = Depends(get_db),
    # This endpoint is protected. Only authenticated dashboard users can view logs.
    current_user: dict = Depends(get_current_user),
    # --- Filtering Query Parameters ---
    node_id: Optional[int] = Query(None, description="Filter events by a specific Node ID."),
    severity: Optional[str] = Query(None, description="Filter events by severity (e.g., 'high', 'medium')."),
    event_type: Optional[str] = Query(None, description="Filter by a specific event type."),
    start_time: Optional[datetime] = Query(None, description="The start of the time range to query (ISO 8601 format)."),
    end_time: Optional[datetime] = Query(None, description="The end of the time range to query (ISO 8601 format)."),
    limit: int = Query(100, ge=1, le=1000, description="The maximum number of events to return."),
):
    """
    Queries the database for events, allowing for flexible filtering.
    """
    stmt = select(models.Event)

    # Dynamically build the WHERE clause based on provided filters
    if node_id is not None:
        stmt = stmt.where(models.Event.node_id == node_id)
    if severity is not None:
        stmt = stmt.where(models.Event.severity == severity)
    if event_type is not None:
        stmt = stmt.where(models.Event.event_type == event_type)
    if start_time is not None:
        stmt = stmt.where(models.Event.timestamp >= start_time)
    if end_time is not None:
        stmt = stmt.where(models.Event.timestamp <= end_time)

    # Order by most recent events first and apply the limit
    stmt = stmt.order_by(models.Event.timestamp.desc()).limit(limit)

    result = await db.execute(stmt)
    events = result.scalars().all()

    return events