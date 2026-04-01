"""
Audit Logger - Logs all CircuitBreaker decisions to PostgreSQL
"""

import json
import uuid
from typing import Dict, Any, Optional
from datetime import datetime


class AuditLogger:
    """
    Logs every CircuitBreaker evaluation for forensics and compliance
    
    If database is not available, logs to console/file as fallback
    """
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url
        self.db_session = None
        
        if database_url:
            try:
                self._init_db()
            except Exception as e:
                print(f"Warning: Could not connect to database: {e}")
                print("Falling back to console logging")
    
    def _init_db(self):
        """Initialize database connection"""
        # Lazy import to avoid dependency if not using DB
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from .models import Base, init_database
        
        self.engine = init_database(self.database_url)
        Session = sessionmaker(bind=self.engine)
        self.db_session = Session()
    
    def log(self, event_data: Dict[str, Any]):
        """
        Log an audit event
        
        Args:
            event_data: Dictionary with event details
        """
        if self.db_session:
            self._log_to_db(event_data)
        else:
            self._log_to_console(event_data)
    
    def _log_to_db(self, event_data: Dict[str, Any]):
        """Log to PostgreSQL database"""
        from .models import AuditEvent
        
        result = event_data.get("result")
        context = event_data.get("context", {})
        
        event = AuditEvent(
            id=str(uuid.uuid4()),
            request_id=event_data.get("request_id"),
            tool=event_data.get("tool", "unknown"),
            tool_params=event_data.get("params"),
            environment=context.get("environment"),
            user_id=context.get("user"),
            session_id=context.get("session_id"),
            agent_type=context.get("agent_type"),
            action=result.action if result else "unknown",
            risk_level=result.risk_level if result else "unknown",
            reason=result.reason if result else None,
            execution_time_ms=result.execution_time_ms if result else None,
            full_context=context
        )
        
        try:
            self.db_session.add(event)
            self.db_session.commit()
        except Exception as e:
            self.db_session.rollback()
            print(f"Error writing to database: {e}")
            # Fallback to console
            self._log_to_console(event_data)
    
    def _log_to_console(self, event_data: Dict[str, Any]):
        """Fallback: Log to console"""
        timestamp = datetime.utcnow().isoformat()
        result = event_data.get("result")
        
        log_line = {
            "timestamp": timestamp,
            "request_id": event_data.get("request_id"),
            "tool": event_data.get("tool"),
            "action": result.action if result else "unknown",
            "risk_level": result.risk_level if result else "unknown",
            "reason": result.reason if result else None,
        }
        
        print(f"[CIRCUITBREAKER AUDIT] {json.dumps(log_line)}")
    
    def get_recent_events(self, limit: int = 100):
        """Get recent audit events (for dashboard)"""
        if not self.db_session:
            return []
        
        from .models import AuditEvent
        
        return self.db_session.query(AuditEvent)\
            .order_by(AuditEvent.timestamp.desc())\
            .limit(limit)\
            .all()
    
    def get_events_by_tool(self, tool: str, limit: int = 100):
        """Get events filtered by tool name"""
        if not self.db_session:
            return []
        
        from .models import AuditEvent
        
        return self.db_session.query(AuditEvent)\
            .filter(AuditEvent.tool == tool)\
            .order_by(AuditEvent.timestamp.desc())\
            .limit(limit)\
            .all()