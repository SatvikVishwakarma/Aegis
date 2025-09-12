# schemas.py

from __future__ import annotations

import datetime
from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field


# ==============================================================================
# Node Schemas
# ==============================================================================

class NodeBase(BaseModel):
    """Base schema for a Node, containing common attributes."""
    hostname: str = Field(..., max_length=255, description="The unique hostname of the node.")
    ip_address: str = Field(..., max_length=45, description="The IP address of the node.")


class NodeRegisterRequest(NodeBase):
    """Schema for registering a new node. Inherits all fields from NodeBase."""
    pass


class NodeResponse(NodeBase):
    """
    Schema for representing a Node in API responses.
    Includes database-generated fields like ID and timestamps.
    """
    id: int
    status: str = Field(description="The current operational status of the node (e.g., 'online', 'offline').")
    last_seen: datetime.datetime

    # Pydantic v2 configuration to enable ORM mode (from_attributes=True).
    # This allows the model to be created from an SQLAlchemy model instance.
    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# Event Schemas
# ==============================================================================

class EventBase(BaseModel):
    """Base schema for an Event, containing common attributes."""
    event_type: str = Field(..., max_length=100, description="The type of event (e.g., 'failed_login', 'file_modified').")
    severity: str = Field(..., max_length=50, description="Severity level of the event (e.g., 'low', 'medium', 'high').")
    details: Dict[str, Any] = Field(..., description="A JSON object containing event-specific details.")


class EventIngestRequest(EventBase):
    """Schema for ingesting a new event from a node."""
    node_id: int = Field(..., description="The ID of the node that generated the event.")


class EventResponse(EventBase):
    """Schema for representing an Event in API responses."""
    id: int
    node_id: int
    timestamp: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# Policy Schemas
# ==============================================================================

class PolicyBase(BaseModel):
    """Base schema for a Policy, containing common attributes."""
    name: str = Field(..., max_length=255, description="The unique name of the policy.")
    type: str = Field(..., max_length=100, description="The type of policy (e.g., 'firewall', 'ids').")
    rules_json: Dict[str, Any] = Field(..., description="A JSON object defining the policy rules.")


class PolicyRequest(PolicyBase):
    """Schema for creating or updating a policy."""
    pass


class PolicyResponse(PolicyBase):
    """
    Schema for representing a Policy in API responses.
    Includes the list of nodes assigned to this policy.
    """
    id: int
    # The response will include a list of nodes that this policy is assigned to.
    # We use the NodeResponse schema to structure this data.
    assigned_nodes: List[NodeResponse] = []

    model_config = ConfigDict(from_attributes=True)