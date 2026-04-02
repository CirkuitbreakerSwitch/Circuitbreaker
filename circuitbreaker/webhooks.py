"""
Webhook Support - Send events to external HTTP endpoints
"""

import json
import time
from typing import Dict, Any, Optional, List
import httpx


class WebhookDispatcher:
    """
    Dispatch CircuitBreaker events to external webhooks
    
    Supports multiple endpoints, retries, and custom headers.
    Perfect for integrating with:
    - PagerDuty
    - Custom dashboards
    - SIEM systems
    - Internal alerting
    """
    
    def __init__(self, endpoints: Optional[List[str]] = None):
        self.endpoints = endpoints or []
        self.timeout = 5.0  # seconds
    
    def add_endpoint(self, url: str, headers: Optional[Dict[str, str]] = None, 
                     secret: Optional[str] = None):
        """
        Add a webhook endpoint
        
        Args:
            url: Webhook URL
            headers: Custom headers
            secret: Secret for HMAC signature
        """
        self.endpoints.append({
            "url": url,
            "headers": headers or {},
            "secret": secret
        })
    
    def dispatch(self, event: Dict[str, Any], event_type: str = "evaluation"):
        """
        Dispatch event to all configured webhooks
        
        Args:
            event: The event data
            event_type: Type of event (evaluation, block, escalate, etc.)
        """
        if not self.endpoints:
            return
        
        payload = {
            "event_type": event_type,
            "timestamp": time.time(),
            "data": event
        }
        
        for endpoint in self.endpoints:
            self._send_webhook(endpoint, payload)
    
    def _send_webhook(self, endpoint: Dict[str, Any], payload: Dict[str, Any]):
        """Send webhook to single endpoint"""
        try:
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "CircuitBreaker-Webhook/1.0",
                **endpoint.get("headers", {})
            }
            
            # Add signature if secret configured
            if endpoint.get("secret"):
                import hmac
                import hashlib
                signature = hmac.new(
                    endpoint["secret"].encode(),
                    json.dumps(payload).encode(),
                    hashlib.sha256
                ).hexdigest()
                headers["X-CircuitBreaker-Signature"] = f"sha256={signature}"
            
            response = httpx.post(
                endpoint["url"],
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code >= 400:
                print(f"Webhook error {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"Webhook failed: {e}")
    
    def test_endpoint(self, url: str) -> bool:
        """Test if webhook endpoint is reachable"""
        try:
            response = httpx.post(
                url,
                json={"test": True, "timestamp": time.time()},
                timeout=self.timeout
            )
            return response.status_code < 400
        except Exception as e:
            print(f"Webhook test failed: {e}")
            return False


class WebhookNotifier:
    """
    Convenience class for common webhook notifications
    """
    
    def __init__(self, webhook_url: Optional[str] = None):
        self.dispatcher = WebhookDispatcher()
        if webhook_url:
            self.dispatcher.add_endpoint(webhook_url)
    
    def notify_block(self, event: Dict[str, Any]):
        """Send block notification"""
        self.dispatcher.dispatch(event, "block")
    
    def notify_escalate(self, event: Dict[str, Any]):
        """Send escalation notification"""
        self.dispatcher.dispatch(event, "escalate")
    
    def notify_allow(self, event: Dict[str, Any]):
        """Send allow notification (optional)"""
        self.dispatcher.dispatch(event, "allow")