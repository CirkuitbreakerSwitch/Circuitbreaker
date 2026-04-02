"""
Redis Cache - Sub-millisecond policy caching
"""

import json
import hashlib
from typing import Optional, Dict, Any
import time


class PolicyCache:
    """
    Redis-based cache for policy evaluations
    
    Caches evaluation results to achieve <1ms response times
    for repeated similar requests.
    """
    
    def __init__(self, redis_url: Optional[str] = None, redis_token: Optional[str] = None):
        self.redis = None
        self.enabled = False
        
        if redis_url and redis_token:
            try:
                from redis import Redis
                self.redis = Redis.from_url(
                    redis_url,
                    password=redis_token if not redis_url.startswith('https') else None,
                    decode_responses=True
                )
                self.enabled = True
            except Exception as e:
                print(f"Warning: Could not connect to Redis: {e}")
                print("Running without cache (evaluations will be slower)")
    
    def _make_key(self, tool: str, params: Dict[str, Any], environment: str) -> str:
        """Create cache key from request details"""
        # Hash the params to create a consistent key
        params_str = json.dumps(params, sort_keys=True)
        key_data = f"{tool}:{params_str}:{environment}"
        return f"cb:eval:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    def get(self, tool: str, params: Dict[str, Any], environment: str) -> Optional[Dict[str, Any]]:
        """
        Get cached evaluation result
        
        Returns None if not in cache or cache disabled
        """
        if not self.enabled:
            return None
        
        key = self._make_key(tool, params, environment)
        
        try:
            start = time.time()
            data = self.redis.get(key)
            elapsed = (time.time() - start) * 1000
            
            if data:
                result = json.loads(data)
                # Return only fields that CircuitBreakerResult expects
                return {
                    "allowed": result.get("allowed"),
                    "action": result.get("action"),
                    "reason": result.get("reason"),
                    "risk_level": result.get("risk_level")
                }
            
            return None
            
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    def set(self, tool: str, params: Dict[str, Any], environment: str, 
            result: Dict[str, Any], ttl: int = 300) -> bool:
        """
        Cache evaluation result
        
        Args:
            ttl: Time to live in seconds (default 5 minutes)
        """
        if not self.enabled:
            return False
        
        key = self._make_key(tool, params, environment)
        
        try:
            # Don't cache escalate actions (they need fresh evaluation)
            if result.get("action") == "escalate":
                return False
            
            data = json.dumps(result)
            self.redis.setex(key, ttl, data)
            return True
            
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def invalidate(self, tool: Optional[str] = None) -> bool:
        """
        Invalidate cache entries
        
        If tool specified, only invalidate that tool's entries
        """
        if not self.enabled:
            return False
        
        try:
            if tool:
                # Pattern delete for specific tool
                pattern = f"cb:eval:*"
                keys = self.redis.keys(pattern)
                if keys:
                    self.redis.delete(*keys)
            else:
                # Clear all CircuitBreaker cache
                pattern = "cb:eval:*"
                keys = self.redis.keys(pattern)
                if keys:
                    self.redis.delete(*keys)
            return True
            
        except Exception as e:
            print(f"Cache invalidate error: {e}")
            return False
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.enabled:
            return {"enabled": False}
        
        try:
            info = self.redis.info()
            return {
                "enabled": True,
                "used_memory": info.get('used_memory_human', 'unknown'),
                "connected_clients": info.get('connected_clients', 0),
                "total_keys": self.redis.dbsize()
            }
        except Exception as e:
            return {"enabled": True, "error": str(e)}


class NullCache:
    """
    Fallback cache when Redis is not available
    """
    
    def get(self, *args, **kwargs):
        return None
    
    def set(self, *args, **kwargs):
        return False
    
    def invalidate(self, *args, **kwargs):
        return False
    
    def stats(self):
        return {"enabled": False, "mode": "null"}