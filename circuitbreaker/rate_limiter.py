"""
Rate Limiter - Prevent AI agents from overwhelming systems
"""

import time
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class RateLimit:
    """Rate limit configuration"""
    max_requests: int = 100  # requests per window
    window_seconds: int = 60  # time window
    burst_size: int = 10  # allow short bursts


class RateLimiter:
    """
    Token bucket rate limiter for AI agent requests
    
    Prevents:
    - DDoS attacks from runaway agents
    - Resource exhaustion
    - Accidental infinite loops
    """
    
    def __init__(self):
        self.buckets: Dict[str, Dict[str, Any]] = {}
    
    def _get_key(self, context: Dict[str, Any]) -> str:
        """Create unique key for rate limiting"""
        user = context.get("user", "anonymous")
        session = context.get("session_id", "default")
        tool = context.get("tool", "any")
        return f"{user}:{session}:{tool}"
    
    def check(self, context: Dict[str, Any], limit: Optional[RateLimit] = None) -> Dict[str, Any]:
        """
        Check if request is within rate limit
        
        Returns:
            Dict with 'allowed' (bool) and 'retry_after' (seconds)
        """
        if limit is None:
            limit = RateLimit()
        
        key = self._get_key(context)
        now = time.time()
        
        # Get or create bucket
        bucket = self.buckets.get(key, {
            "tokens": limit.burst_size,
            "last_update": now
        })
        
        # Add tokens based on time passed
        time_passed = now - bucket["last_update"]
        tokens_to_add = time_passed * (limit.max_requests / limit.window_seconds)
        bucket["tokens"] = min(limit.burst_size, bucket["tokens"] + tokens_to_add)
        bucket["last_update"] = now
        
        # Check if we can consume a token
        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            self.buckets[key] = bucket
            return {
                "allowed": True,
                "remaining": int(bucket["tokens"]),
                "limit": limit.max_requests,
                "window": limit.window_seconds
            }
        else:
            # Calculate retry after
            tokens_needed = 1 - bucket["tokens"]
            retry_after = tokens_needed / (limit.max_requests / limit.window_seconds)
            self.buckets[key] = bucket
            
            return {
                "allowed": False,
                "retry_after": round(retry_after, 2),
                "limit": limit.max_requests,
                "window": limit.window_seconds
            }
    
    def get_stats(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get rate limit stats for a context"""
        key = self._get_key(context)
        bucket = self.buckets.get(key, {"tokens": 0, "last_update": 0})
        
        return {
            "current_tokens": round(bucket["tokens"], 2),
            "key": key
        }