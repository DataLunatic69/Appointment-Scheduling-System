"""
Pydantic models for API request and response schemas.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ChatMessage(BaseModel):
    """Individual chat message model."""
    role: str = Field(..., description="Role of the message sender (user, assistant, system)")
    content: str = Field(..., description="Content of the message")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now, description="Message timestamp")


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., description="User message to process", min_length=1, max_length=2000)
    thread_id: Optional[str] = Field(None, description="Conversation thread ID for context")
    include_metadata: bool = Field(False, description="Whether to include metadata in response")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="Assistant's response")
    thread_id: str = Field(..., description="Conversation thread ID")
    agent_used: Optional[str] = Field(None, description="Agent that processed the request")
    processing_time: float = Field(..., description="Processing time in seconds")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata if requested")


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Health check timestamp")
    version: str = Field(..., description="API version")
    agents_available: List[str] = Field(..., description="List of available agents")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class AgentInfo(BaseModel):
    """Agent information model."""
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    tools: List[str] = Field(..., description="List of tools available to the agent")
    status: str = Field(..., description="Agent status (active, inactive, error)")


class SystemStatusResponse(BaseModel):
    """System status response model."""
    status: str = Field(..., description="Overall system status")
    agents: List[AgentInfo] = Field(..., description="List of agent information")
    uptime: float = Field(..., description="System uptime in seconds")
    memory_usage: Optional[Dict[str, Any]] = Field(None, description="Memory usage information")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
