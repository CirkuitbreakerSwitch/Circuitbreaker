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
from .cache import PolicyCache, NullCache
from .config import Config
from .notifier import NotificationDispatcher
from .metrics import get_metrics


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
        
        # Use config values if not provided
        self.redis_url = redis_url or Config.REDIS_URL
        self.database_url = database_url or Config.DATABASE_URL
        self.slack_webhook = slack_webhook or Config.SLACK_WEBHOOK_URL
        
        # Initialize components
        self.policy_engine = PolicyEngine(policies_path)
        self.evaluator = RiskEvaluator()
        self.audit = AuditLogger(self.database_url)
        self.cache = PolicyCache(self.redis_url, Config.REDIS_TOKEN) if self.redis_url else NullCache()
        self.notifier = NotificationDispatcher(self.slack_webhook, Config.SLACK_BOT_TOKEN)
        
        self.config = {
            "redis_url": self.redis_url,
            "database_url": self.database_url,
            "slack_webhook": self.slack_webhook,
        }
        
    def evaluate(
        self,
        tool: str,
        params: Dict[str, Any],
        context: Optional[ExecutionContext] = None
    ) -> CircuitBreakerResult:
        """
        Evaluate a tool call and decide: allow, block, or escalate
        """
        start_time = time.time()
        request_id = str(uuid.uuid4())[:8]
        
        # Create context if not provided
        if context is None:
            context = ExecutionContext()
        
        # Check cache first
        cached = self.cache.get(tool, params, context.environment)
        if cached:
            cached['execution_time_ms'] = (time.time() - start_time) * 1000
            cached['request_id'] = request_id
            
            # Record metrics for cache hit
            result = CircuitBreakerResult(**cached)
            metrics = get_metrics()
            metrics.record_evaluation(
                result=result,
                execution_time_ms=result.execution_time_ms,
                cache_hit=True
            )
            return result
        
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
        
        # Record metrics
        metrics = get_metrics()
        metrics.record_evaluation(
            result=result,
            execution_time_ms=execution_time_ms,
            cache_hit=False
        )
        
        # Cache the result (don't cache escalations)
        if action != "escalate":
            self.cache.set(
                tool=tool,
                params=params,
                environment=context.environment,
                result={
                    "allowed": allowed,
                    "action": action,
                    "reason": policy_result["reason"],
                    "risk_level": risk_result["level"]
                }
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
        
        # Send notification for blocks and escalations
        if action in ["block", "escalate"]:
            self.notifier.send(
                event={
                    "request_id": request_id,
                    "tool": tool,
                    "params": params,
                    "context": eval_context,
                    "result": {
                        "action": action,
                        "reason": policy_result["reason"],
                        "risk_level": risk_result["level"]
                    },
                    "timestamp": time.time()
                },
                channels=["slack", "console"]
            )
        
        return result
    
    def protect(self, tool: str):
        """
        Decorator to protect a function with CircuitBreaker
        """
        def decorator(func: Callable):
            def wrapper(*args, **kwargs):
                import inspect
                sig = inspect.signature(func)
                bound = sig.bind(*args, **kwargs)
                bound.apply_defaults()
                
                result = self.evaluate(
                    tool=tool,
                    params=dict(bound.arguments)
                )
                
                if not result.allowed:
                    raise CircuitBreakerBlocked(
                        f"Action blocked: {result.reason} "
                        f"(risk: {result.risk_level})"
                    )
                
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def get_health(self) -> Dict[str, Any]:
        """Get health status and metrics"""
        return get_metrics().health_check()
    
    def get_metrics_stats(self) -> Dict[str, Any]:
        """Get detailed metrics"""
        return get_metrics().get_stats()


class CircuitBreakerBlocked(Exception):
    """Exception raised when CircuitBreaker blocks an action"""
    pass