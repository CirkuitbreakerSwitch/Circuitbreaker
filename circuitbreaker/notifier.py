"""
Notifier - Send notifications for escalations and blocks
"""

from typing import Dict, Any, Optional
import json
import time


class NotificationDispatcher:
    """
    Dispatches notifications to various channels (Slack, email, etc.)
    """
    
    def __init__(self, slack_webhook: Optional[str] = None, slack_token: Optional[str] = None):
        self.slack_webhook = slack_webhook
        self.slack_token = slack_token
        self.enabled = bool(slack_webhook or slack_token)
    
    def send(self, event: Dict[str, Any], channels: list = None):
        """
        Send notification about a CircuitBreaker event
        
        Args:
            event: The audit event data
            channels: List of channels to notify (default: ['slack'])
        """
        if not channels:
            channels = ["slack"]
        
        for channel in channels:
            if channel == "slack" and self.enabled:
                self._send_slack(event)
            elif channel == "console":
                self._send_console(event)
    
    def _send_slack(self, event: Dict[str, Any]):
        """Send Slack notification"""
        try:
            import httpx
            
            result = event.get("result", {})
            tool = event.get("tool", "unknown")
            action = result.get("action", "unknown")
            risk = result.get("risk_level", "unknown")
            reason = result.get("reason", "No reason provided")
            request_id = event.get("request_id", "unknown")
            
            # Color based on action
            color = {
                "block": "#FF0000",      # Red
                "escalate": "#FFA500",   # Orange
                "allow": "#00FF00"       # Green
            }.get(action, "#808080")
            
            message = {
                "text": f"🛡️ CircuitBreaker Alert: {action.upper()}",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"🛡️ CircuitBreaker: {action.upper()}"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {"type": "mrkdwn", "text": f"*Tool:*\n{tool}"},
                            {"type": "mrkdwn", "text": f"*Action:*\n{action}"},
                            {"type": "mrkdwn", "text": f"*Risk Level:*\n{risk}"},
                            {"type": "mrkdwn", "text": f"*Request ID:*\n{request_id}"}
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Reason:*\n{reason}"
                        }
                    }
                ]
            }
            
            if action == "escalate":
                # Add approval buttons for escalations
                message["blocks"].append({
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "✅ Approve"},
                            "style": "primary",
                            "value": f"approve_{request_id}",
                            "action_id": "approve_action"
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "❌ Deny"},
                            "style": "danger",
                            "value": f"deny_{request_id}",
                            "action_id": "deny_action"
                        }
                    ]
                })
            
            if self.slack_webhook:
                response = httpx.post(self.slack_webhook, json=message)
                if response.status_code == 200:
                    print(f"✅ Slack notification sent for {request_id}")
                else:
                    print(f"⚠️ Slack error: {response.status_code}")
                    
        except Exception as e:
            print(f"⚠️ Could not send Slack notification: {e}")
            # Fallback to console
            self._send_console(event)
    
    def _send_console(self, event: Dict[str, Any]):
        """Fallback: print to console"""
        result = event.get("result", {})
        print(f"\n{'='*50}")
        print(f"NOTIFICATION: {result.get('action', 'unknown').upper()}")
        print(f"Tool: {event.get('tool')}")
        print(f"Reason: {result.get('reason')}")
        print(f"Request ID: {event.get('request_id')}")
        print(f"{'='*50}\n")