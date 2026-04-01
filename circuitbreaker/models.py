"""
Database Models - SQLAlchemy models for audit logging
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import create_engine, Column, String, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class AuditEvent(Base):
    """
    Audit log entry for every CircuitBreaker evaluation
    """
    __tablename__ = "audit_events"
    
    id = Column(String(36), primary_key=True)
    request_id = Column(String(8), index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Tool info
    tool = Column(String(255), nullable=False, index=True)
    tool_params = Column(JSON, nullable=True)
    
    # Context
    environment = Column(String(50), index=True)
    user_id = Column(String(255), index=True)
    session_id = Column(String(8), index=True)
    agent_type = Column(String(50))
    
    # Decision
    action = Column(String(20), nullable=False)  # allow, block, escalate
    risk_level = Column(String(20), nullable=False)  # low, medium, high, critical
    reason = Column(Text, nullable=True)
    
    # Performance
    execution_time_ms = Column(Float, nullable=True)
    
    # Raw data
    full_context = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<AuditEvent {self.request_id}: {self.tool} -> {self.action}>"


class PolicyRule(Base):
    """
    Policy rules stored in database
    """
    __tablename__ = "policy_rules"
    
    id = Column(String(36), primary_key=True)
    policy_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    enabled = Column(String(10), default="true")
    
    # Rule definition
    rule_type = Column(String(50))  # tool_match, content_match, etc.
    tool_pattern = Column(String(255))
    condition_field = Column(String(100))
    condition_operator = Column(String(20))
    condition_value = Column(String(255))
    content_pattern = Column(Text)
    
    # Action
    action = Column(String(20), default="block")  # block, escalate, allow
    severity = Column(String(20), default="medium")
    notify_channels = Column(JSON, nullable=True)  # ["slack", "email"]
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<PolicyRule {self.policy_id}: {self.name}>"


def init_database(database_url: str):
    """
    Initialize database tables
    
    Args:
        database_url: PostgreSQL connection string
    """
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return engine


def get_session_maker(engine):
    """Get session maker bound to engine"""
    return sessionmaker(bind=engine)