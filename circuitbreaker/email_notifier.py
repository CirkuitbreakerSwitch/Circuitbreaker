"""
Email Notifications - Send alerts via email
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
import time


class EmailNotifier:
    """
    Send email notifications for CircuitBreaker events
    
    Supports SMTP servers (Gmail, Outlook, corporate servers)
    """
    
    def __init__(
        self,
        smtp_server: Optional[str] = None,
        smtp_port: int = 587,
        username: Optional[str] = None,
        password: Optional[str] = None,
        from_addr: Optional[str] = None,
        to_addrs: Optional[list] = None,
        use_tls: bool = True
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_addr = from_addr or username
        self.to_addrs = to_addrs or []
        self.use_tls = use_tls
        self.enabled = all([smtp_server, username, password, self.to_addrs])
    
    def send(self, event: Dict[str, Any]):
        """
        Send email notification
        
        Args:
            event: CircuitBreaker event data
        """
        if not self.enabled:
            return
        
        try:
            result = event.get("result", {})
            tool = event.get("tool", "unknown")
            action = result.get("action", "unknown")
            
            subject = f"🛡️ CircuitBreaker Alert: {action.upper()} - {tool}"
            
            body = self._format_email(event)
            
            msg = MIMEMultipart()
            msg["From"] = self.from_addr
            msg["To"] = ", ".join(self.to_addrs)
            msg["Subject"] = subject
            
            msg.attach(MIMEText(body, "plain"))
            
            # Send email
            context = ssl.create_default_context() if self.use_tls else None
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls(context=context)
                server.login(self.username, self.password)
                server.send_message(msg)
            
            print(f"✅ Email sent to {', '.join(self.to_addrs)}")
            
        except Exception as e:
            print(f"⚠️ Email failed: {e}")
    
    def _format_email(self, event: Dict[str, Any]) -> str:
        """Format event data as email body"""
        result = event.get("result", {})
        
        body = f"""
CircuitBreaker Alert

Action: {result.get('action', 'unknown').upper()}
Tool: {event.get('tool', 'unknown')}
Risk Level: {result.get('risk_level', 'unknown')}
Reason: {result.get('reason', 'No reason provided')}
Request ID: {event.get('request_id', 'unknown')}
Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(event.get('timestamp', time.time())))}

Context:
- Environment: {event.get('context', {}).get('environment', 'unknown')}
- User: {event.get('context', {}).get('user', 'unknown')}
- Session: {event.get('context', {}).get('session_id', 'unknown')}

---
This is an automated message from CircuitBreaker.
        """
        return body.strip()
    
    def test_connection(self) -> bool:
        """Test SMTP connection"""
        if not self.enabled:
            print("Email not configured")
            return False
        
        try:
            context = ssl.create_default_context() if self.use_tls else None
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls(context=context)
                server.login(self.username, self.password)
                print("✅ SMTP connection successful")
                return True
                
        except Exception as e:
            print(f"❌ SMTP connection failed: {e}")
            return False