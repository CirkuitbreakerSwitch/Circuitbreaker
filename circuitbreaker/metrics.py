"""
Metrics and Monitoring - Track CircuitBreaker performance
"""

import time
from typing import Dict, Any
from dataclasses import dataclass, field


@dataclass
class CircuitBreakerMetrics:
    """
    Real-time metrics for CircuitBreaker
    
    Track evaluations, blocks, cache performance, etc.
    """
    
    # Counters
    total_evaluations: int = 0
    allowed_count: int = 0
    blocked_count: int = 0
    escalated_count: int = 0
    
    # Cache metrics
    cache_hits: int = 0
    cache_misses: int = 0
    
    # Performance
    total_execution_time_ms: float = 0.0
    
    # Start time
    start_time: float = field(default_factory=time.time)
    
    def record_evaluation(self, result: Any, execution_time_ms: float, cache_hit: bool = False):
        """Record an evaluation result"""
        self.total_evaluations += 1
        self.total_execution_time_ms += execution_time_ms
        
        if cache_hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
        
        if result.action == "allow":
            self.allowed_count += 1
        elif result.action == "block":
            self.blocked_count += 1
        elif result.action == "escalate":
            self.escalated_count += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current metrics"""
        uptime = time.time() - self.start_time
        
        avg_execution_time = (
            self.total_execution_time_ms / self.total_evaluations 
            if self.total_evaluations > 0 else 0
        )
        
        cache_hit_rate = (
            self.cache_hits / (self.cache_hits + self.cache_misses) * 100
            if (self.cache_hits + self.cache_misses) > 0 else 0
        )
        
        return {
            "uptime_seconds": round(uptime, 2),
            "total_evaluations": self.total_evaluations,
            "allowed": self.allowed_count,
            "blocked": self.blocked_count,
            "escalated": self.escalated_count,
            "block_rate": round(self.blocked_count / self.total_evaluations * 100, 2) if self.total_evaluations > 0 else 0,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": round(cache_hit_rate, 2),
            "avg_execution_time_ms": round(avg_execution_time, 2),
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for monitoring"""
        stats = self.get_stats()
        
        # Determine health status
        if stats["avg_execution_time_ms"] > 1000:
            status = "degraded"
            message = "High latency detected"
        elif stats["total_evaluations"] > 0 and stats["avg_execution_time_ms"] < 100:
            status = "healthy"
            message = "Operating normally"
        else:
            status = "healthy"
            message = "Ready"
        
        return {
            "status": status,
            "message": message,
            "timestamp": time.time(),
            "metrics": stats
        }


# Global metrics instance
_metrics = CircuitBreakerMetrics()


def get_metrics() -> CircuitBreakerMetrics:
    """Get global metrics instance"""
    return _metrics


def reset_metrics():
    """Reset global metrics (for testing)"""
    global _metrics
    _metrics = CircuitBreakerMetrics()