"""
Audit Export - Export audit logs for compliance reporting
"""

import json
import csv
import io
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional


class AuditExporter:
    """
    Export audit logs in various formats for compliance
    
    Supports:
    - CSV (for Excel/analysis)
    - JSON (for APIs)
    - PDF (for reports) - requires reportlab
    """
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url
    
    def export_csv(self, start_date: Optional[datetime] = None, 
                   end_date: Optional[datetime] = None) -> str:
        """
        Export audit logs to CSV format
        
        Returns:
            CSV string
        """
        # Get data from database
        events = self._get_events(start_date, end_date)
        
        if not events:
            return "timestamp,request_id,tool,action,risk_level,reason\n"
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "timestamp", "request_id", "tool", "action", 
            "risk_level", "reason", "environment", "user_id"
        ])
        
        # Data
        for event in events:
            writer.writerow([
                event.get("timestamp"),
                event.get("request_id"),
                event.get("tool"),
                event.get("action"),
                event.get("risk_level"),
                event.get("reason"),
                event.get("environment"),
                event.get("user_id")
            ])
        
        return output.getvalue()
    
    def export_json(self, start_date: Optional[datetime] = None,
                    end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Export audit logs to JSON format
        
        Returns:
            List of event dictionaries
        """
        return self._get_events(start_date, end_date)
    
    def export_summary(self, days: int = 30) -> Dict[str, Any]:
        """
        Export compliance summary report
        
        Returns:
            Summary statistics
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        events = self._get_events(start_date)
        
        total = len(events)
        blocked = sum(1 for e in events if e.get("action") == "block")
        escalated = sum(1 for e in events if e.get("action") == "escalate")
        
        # Group by tool
        tools = {}
        for e in events:
            tool = e.get("tool", "unknown")
            tools[tool] = tools.get(tool, 0) + 1
        
        return {
            "period_days": days,
            "generated_at": datetime.utcnow().isoformat(),
            "total_evaluations": total,
            "blocked_actions": blocked,
            "escalated_actions": escalated,
            "block_rate": round(blocked / total * 100, 2) if total > 0 else 0,
            "top_tools": dict(sorted(tools.items(), key=lambda x: x[1], reverse=True)[:10]),
            "compliance_status": "active" if total > 0 else "no_data"
        }
    
    def _get_events(self, start_date: Optional[datetime] = None,
                    end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get events from database"""
        # In production, query PostgreSQL
        # For now, return empty list (implement with actual DB query)
        
        if not self.database_url:
            return []
        
        try:
            from .models import AuditEvent, init_database
            from sqlalchemy.orm import sessionmaker
            
            engine = init_database(self.database_url)
            Session = sessionmaker(bind=engine)
            session = Session()
            
            query = session.query(AuditEvent)
            
            if start_date:
                query = query.filter(AuditEvent.timestamp >= start_date)
            if end_date:
                query = query.filter(AuditEvent.timestamp <= end_date)
            
            events = query.order_by(AuditEvent.timestamp.desc()).all()
            
            return [{
                "timestamp": e.timestamp.isoformat() if e.timestamp else None,
                "request_id": e.request_id,
                "tool": e.tool,
                "action": e.action,
                "risk_level": e.risk_level,
                "reason": e.reason,
                "environment": e.environment,
                "user_id": e.user_id
            } for e in events]
            
        except Exception as e:
            print(f"Export error: {e}")
            return []


def generate_compliance_report(output_file: str = "compliance_report.json"):
    """Generate a compliance report file"""
    from .config import Config
    
    exporter = AuditExporter(Config.DATABASE_URL)
    summary = exporter.export_summary(days=30)
    
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Compliance report saved to {output_file}")
    return summary
    