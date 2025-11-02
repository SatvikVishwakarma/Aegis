# schemas.py (Fully Updated)

from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional

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


class NodeHeartbeatRequest(BaseModel):
    """Schema for a node sending a heartbeat."""
    hostname: str = Field(..., description="The unique hostname of the node checking in.")


class NodeUpdateRequest(BaseModel):
    """
    Schema for updating an existing node.
    All fields are optional, so you can update one or both.
    """
    hostname: Optional[str] = Field(None, max_length=255, description="The new unique hostname for the node.")
    ip_address: Optional[str] = Field(None, max_length=45, description="The new IP address for the node.")


class NodeResponse(NodeBase):
    """
    Schema for representing a Node in API responses.
    Includes database-generated fields like ID and timestamps.
    """
    id: int
    status: str = Field(description="The current operational status of the node (e.g., 'online', 'offline').")
    last_seen: datetime.datetime

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
    assigned_nodes: List[NodeResponse] = []

    model_config = ConfigDict(from_attributes=True)
    

# ==============================================================================
# Authentication Schemas
# ==============================================================================

class Token(BaseModel):
    """Schema for the JWT access token response."""
    access_token: str
    token_type: str


class UserBase(BaseModel):
    """Base schema for a User, containing common attributes."""
    username: str = Field(..., max_length=100, description="The unique username.")
    email: str = Field(..., max_length=255, description="The user's email address.")
    full_name: Optional[str] = Field(None, max_length=255, description="The user's full name.")


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, description="The user's password (plain text, will be hashed).")


class UserUpdate(BaseModel):
    """Schema for updating an existing user."""
    email: Optional[str] = Field(None, max_length=255, description="The new email address.")
    full_name: Optional[str] = Field(None, max_length=255, description="The new full name.")
    password: Optional[str] = Field(None, min_length=8, description="The new password (plain text, will be hashed).")
    disabled: Optional[bool] = Field(None, description="Whether the user account is disabled.")


class UserResponse(UserBase):
    """Schema for representing a User in API responses."""
    id: int
    disabled: bool
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)