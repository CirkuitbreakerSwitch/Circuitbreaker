"""
CircuitBreaker Dashboard API
FastAPI backend for serving dashboard data
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import os
import sys

# Add parent directory to import circuitbreaker
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from circuitbreaker.models import AuditEvent, init_database
from circuitbreaker.config import Config

app = FastAPI(
    title="CircuitBreaker Dashboard API",
    version="1.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
engine = None
SessionLocal = None

if Config.has_database():
    engine = init_database(Config.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)


# Pydantic models for API responses
class EventResponse(BaseModel):
    id: str
    request_id: str
    timestamp: datetime
    tool: str
    action: str
    risk_level: str
    reason: Optional[str]
    environment: Optional[str]
    
    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    total_evaluations: int
    blocked: int
    escalated: int
    allowed: int
    block_rate: float
    period: str


class ToolStat(BaseModel):
    tool: str
    count: int
    blocked: int


@app.get("/")
def root():
    return {"status": "CircuitBreaker Dashboard API", "version": "1.0.0"}


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "database": "connected" if engine else "disconnected",
        "timestamp": datetime.utcnow()
    }


@app.get("/api/events", response_model=List[EventResponse])
def get_events(limit: int = 50, action: Optional[str] = None):
    """Get recent audit events"""
    if not SessionLocal:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    db = SessionLocal()
    try:
        query = db.query(AuditEvent).order_by(AuditEvent.timestamp.desc())
        
        if action:
            query = query.filter(AuditEvent.action == action)
        
        events = query.limit(limit).all()
        return events
    finally:
        db.close()


@app.get("/api/events/recent")
def get_recent_events(seconds: int = 60):
    """Get events from last N seconds (for real-time updates)"""
    if not SessionLocal:
        return []
    
    db = SessionLocal()
    try:
        since = datetime.utcnow() - timedelta(seconds=seconds)
        events = db.query(AuditEvent).filter(
            AuditEvent.timestamp >= since
        ).order_by(AuditEvent.timestamp.desc()).all()
        
        return [{
            "id": e.id,
            "request_id": e.request_id,
            "timestamp": e.timestamp.isoformat() if e.timestamp else None,
            "tool": e.tool,
            "action": e.action,
            "risk_level": e.risk_level,
            "reason": e.reason,
            "environment": e.environment
        } for e in events]
    finally:
        db.close()


@app.get("/api/stats", response_model=StatsResponse)
def get_stats(period: str = "24h"):
    """Get statistics for dashboard"""
    if not SessionLocal:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    db = SessionLocal()
    try:
        # Calculate time range
        if period == "1h":
            since = datetime.utcnow() - timedelta(hours=1)
        elif period == "24h":
            since = datetime.utcnow() - timedelta(hours=24)
        elif period == "7d":
            since = datetime.utcnow() - timedelta(days=7)
        else:
            since = datetime.utcnow() - timedelta(hours=24)
        
        # Query stats
        query = db.query(AuditEvent).filter(AuditEvent.timestamp >= since)
        
        total = query.count()
        blocked = query.filter(AuditEvent.action == "block").count()
        escalated = query.filter(AuditEvent.action == "escalate").count()
        allowed = query.filter(AuditEvent.action == "allow").count()
        
        block_rate = round((blocked / total * 100), 2) if total > 0 else 0
        
        return StatsResponse(
            total_evaluations=total,
            blocked=blocked,
            escalated=escalated,
            allowed=allowed,
            block_rate=block_rate,
            period=period
        )
    finally:
        db.close()


@app.get("/api/stats/tools")
def get_tool_stats(period: str = "24h"):
    """Get statistics grouped by tool"""
    if not SessionLocal:
        return []
    
    db = SessionLocal()
    try:
        if period == "1h":
            since = datetime.utcnow() - timedelta(hours=1)
        elif period == "24h":
            since = datetime.utcnow() - timedelta(hours=24)
        else:
            since = datetime.utcnow() - timedelta(hours=24)
        
        # Get all events in period
        events = db.query(AuditEvent).filter(
            AuditEvent.timestamp >= since
        ).all()
        
        # Group by tool
        tool_stats: Dict[str, Dict] = {}
        for e in events:
            if e.tool not in tool_stats:
                tool_stats[e.tool] = {"count": 0, "blocked": 0}
            tool_stats[e.tool]["count"] += 1
            if e.action == "block":
                tool_stats[e.tool]["blocked"] += 1
        
        return [
            {"tool": tool, "count": data["count"], "blocked": data["blocked"]}
            for tool, data in sorted(
                tool_stats.items(), 
                key=lambda x: x[1]["count"], 
                reverse=True
            )[:10]
        ]
    finally:
        db.close()


@app.get("/api/stats/timeline")
def get_timeline(period: str = "24h"):
    """Get events timeline for charts"""
    if not SessionLocal:
        return []
    
    db = SessionLocal()
    try:
        if period == "1h":
            since = datetime.utcnow() - timedelta(hours=1)
            interval = "minute"
        elif period == "24h":
            since = datetime.utcnow() - timedelta(hours=24)
            interval = "hour"
        else:
            since = datetime.utcnow() - timedelta(hours=24)
            interval = "hour"
        
        events = db.query(AuditEvent).filter(
            AuditEvent.timestamp >= since
        ).order_by(AuditEvent.timestamp).all()
        
        # Group by time bucket
        timeline = {}
        for e in events:
            if interval == "hour":
                bucket = e.timestamp.strftime("%H:00") if e.timestamp else "unknown"
            else:
                bucket = e.timestamp.strftime("%H:%M") if e.timestamp else "unknown"
            
            if bucket not in timeline:
                timeline[bucket] = {"time": bucket, "allowed": 0, "blocked": 0, "escalated": 0}
            
            if e.action in timeline[bucket]:
                timeline[bucket][e.action] += 1
        
        return list(timeline.values())
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)