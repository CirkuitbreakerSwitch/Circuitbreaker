"""
Policy Engine - Loads and evaluates policies
"""

import re
import yaml
import os
from typing import Dict, Any, Optional

from .rate_limiter import RateLimiter, RateLimit


class PolicyEngine:
    """
    Loads policies from YAML and evaluates tool calls against them
    """
    
    def __init__(self, policies_path: Optional[str] = None):
        self.policies = []
        self.policies_path = policies_path or self._default_policies_path()
        self._load_policies()
        
        # Initialize rate limiter
        self.rate_limiter = RateLimiter()
        self.default_rate_limit = RateLimit(max_requests=100, window_seconds=60)
    
    def _default_policies_path(self) -> str:
        """Get default policies file path"""
        # Look for policies.yaml in project root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        return os.path.join(project_root, "policies.yaml")
    
    def _load_policies(self):
        """Load policies from YAML file"""
        if os.path.exists(self.policies_path):
            with open(self.policies_path, 'r') as f:
                data = yaml.safe_load(f)
                self.policies = data.get('policies', [])
        else:
            # Load default policies
            self.policies = self._default_policies()
    
    def _default_policies(self) -> list:
        """Default built-in policies"""
        return [
            {
                "id": "no_prod_delete",
                "name": "No File Deletion in Production",
                "enabled": True,
                "rule": {"type": "tool_match", "tool": "file.delete"},
                "action": "block",
                "severity": "critical"
            },
            {
                "id": "no_drop_table",
                "name": "No DROP TABLE Statements",
                "enabled": True,
                "rule": {"type": "content_match", "tool": "db.query", "pattern": "(?i)DROP\\s+TABLE"},
                "action": "block",
                "severity": "critical"
            }
        ]
    
    def check(self, context: Dict[str, Any], risk_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if tool call matches any policy
        
        Returns:
            Dict with 'action' (allow/block/escalate) and 'reason'
        """
        # Check rate limits first
        rate_result = self.rate_limiter.check(context, self.default_rate_limit)
        if not rate_result["allowed"]:
            return {
                "action": "block",
                "reason": f"Rate limit exceeded. Retry after {rate_result['retry_after']}s",
                "policy_id": "rate_limit",
                "severity": "high"
            }
        
        tool = context.get("tool", "")
        params = context.get("params", {})
        environment = context.get("environment", "development")
        
        for policy in self.policies:
            if not policy.get("enabled", True):
                continue
            
            if self._matches_policy(policy, tool, params, environment):
                return {
                    "action": policy.get("action", "allow"),
                    "reason": f"Policy '{policy['name']}' matched",
                    "policy_id": policy["id"],
                    "severity": policy.get("severity", "medium")
                }
        
        # No policy matched - allow by default
        return {
            "action": "allow",
            "reason": "No matching policy",
            "policy_id": None,
            "severity": "low"
        }
    
    def _matches_policy(self, policy: Dict, tool: str, params: Dict, environment: str) -> bool:
        """Check if a specific policy matches the context"""
        rule = policy.get("rule", {})
        rule_type = rule.get("type")
        
        if rule_type == "tool_match":
            # Match specific tool
            target_tool = rule.get("tool")
            if target_tool and target_tool != tool:
                return False
            
            # Check condition if present
            condition = rule.get("condition", {})
            if condition:
                field = condition.get("field", "")
                operator = condition.get("operator", "")
                value = condition.get("value")
                
                # Simple field check
                if field == "context.environment":
                    if operator == "equals" and environment != value:
                        return False
        
        elif rule_type == "content_match":
            # Match content pattern
            target_tool = rule.get("tool", "*")
            if target_tool != "*" and target_tool != tool:
                return False
            
            pattern = rule.get("pattern", "")
            if pattern:
                # Check in params
                param_str = str(params)
                if not re.search(pattern, param_str):
                    return False
        
        return True