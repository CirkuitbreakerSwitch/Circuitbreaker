"""
CircuitBreaker SDK - Main entry point
"""

import time
import uuid
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass

from .context import ExecutionContext
from .policy import PolicyEngine
from .evaluator import RiskEvaluator
from .audit import AuditLogger


@dataclass
class CircuitBreakerResult:
    """Result of a CircuitBreaker evaluation"""
    allowed: bool
    action: str
    reason: str
    risk_level: str
    request_id: str
    execution_time_ms: float


class CircuitBreaker:
    """
    Main CircuitBreaker class - the seatbelt for AI agents
    """
    
    def __init__(
        self,
        redis_url: Optional[str] = None,
        database_url: Optional[str] = None,
        slack_webhook: Optional[str] = None,
        policies_path: Optional[str] = None
    ):
        self.request_id = str(uuid.uuid4())[:8]
        
        # Initialize components
        self.policy_engine = PolicyEngine(policies_path)
        self.evaluator = RiskEvaluator()
        self.audit = AuditLogger(database_url)
        
        self.config = {
            "redis_url": redis_url,
            "database_url": database_url,
            "slack_webhook": slack_webhook,
        }
        
    def evaluate(
        self,
        tool: str,
        params: Dict[str, Any],
        context: Optional[ExecutionContext] = None
    ):
        """Evaluate a tool call and decide: allow, block, or escalate"""
        start_time = time.time()
        request_id = str(uuid.uuid4())[:8]
        
        # Create context if not provided
        if context is None:
            context = ExecutionContext()
        
        # Build evaluation context
        eval_context = {
            "tool": tool,
            "params": params,
            "environment": context.environment,
            "user": context.user,
            "session_id": context.session_id,
        }
        
        # Evaluate risk
        risk_result = self.evaluator.evaluate(eval_context)
        
        # Check policies
        policy_result = self.policy_engine.check(eval_context, risk_result)
        
        # Determine action
        if policy_result["action"] == "block":
            allowed = False
            action = "block"
        elif policy_result["action"] == "escalate":
            allowed = False
            action = "escalate"
        else:
            allowed = True
            action = "allow"
        
        # Calculate execution time
        execution_time_ms = (time.time() - start_time) * 1000
        
        # Build result
        result = CircuitBreakerResult(
            allowed=allowed,
            action=action,
            reason=policy_result["reason"],
            risk_level=risk_result["level"],
            request_id=request_id,
            execution_time_ms=execution_time_ms
        )
        
        # Audit log
        self.audit.log({
            "request_id": request_id,
            "tool": tool,
            "params": params,
            "context": eval_context,
            "result": result,
            "timestamp": time.time()
        })
        
        return result


class CircuitBreakerBlocked(Exception):
    """Exception raised when CircuitBreaker blocks an action"""
    pass