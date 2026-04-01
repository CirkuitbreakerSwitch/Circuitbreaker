"""
CircuitBreaker - Kill Switch for AI Agents
Real-time intervention layer to prevent catastrophic AI agent actions
"""

__version__ = "0.1.0"
__author__ = "Cirkuitbreaker"

from .sdk import CircuitBreaker
from .context import ExecutionContext

__all__ = ["CircuitBreaker", "ExecutionContext"]