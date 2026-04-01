"""
Execution Context - Holds runtime context for evaluations
"""

import os
import uuid
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class ExecutionContext:
    """
    Context for a tool execution request
    
    Contains environment info, user identity, session tracking, etc.
    """
    
    # Environment
    environment: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    
    # Identity
    user: Optional[str] = None
    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    
    # Request metadata
    request_id: Optional[str] = None
    timestamp: Optional[float] = None
    
    # Agent info
    agent_type: Optional[str] = None  # 'cursor', 'claude', 'langchain', etc.
    agent_version: Optional[str] = None
    
    # Custom context
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for evaluation"""
        return {
            "environment": self.environment,
            "user": self.user,
            "session_id": self.session_id,
            "request_id": self.request_id,
            "timestamp": self.timestamp,
            "agent_type": self.agent_type,
            "agent_version": self.agent_version,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionContext":
        """Create context from dictionary"""
        return cls(
            environment=data.get("environment", "development"),
            user=data.get("user"),
            session_id=data.get("session_id", str(uuid.uuid4())[:8]),
            request_id=data.get("request_id"),
            timestamp=data.get("timestamp"),
            agent_type=data.get("agent_type"),
            agent_version=data.get("agent_version"),
            metadata=data.get("metadata", {})
        )
    
    def with_user(self, user: str) -> "ExecutionContext":
        """Return new context with user set"""
        new_ctx = self.__class__.from_dict(self.to_dict())
        new_ctx.user = user
        return new_ctx
    
    def with_environment(self, environment: str) -> "ExecutionContext":
        """Return new context with environment set"""
        new_ctx = self.__class__.from_dict(self.to_dict())
        new_ctx.environment = environment
        return new_ctx