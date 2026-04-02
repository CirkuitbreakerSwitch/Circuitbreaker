"""
CircuitBreaker - Kill Switch for AI Agents
Real-time intervention layer to prevent catastrophic AI agent actions
"""

__version__ = "0.1.0"
__author__ = "Cirkuitbreaker"

from .config import Config
from .context import ExecutionContext
from .sdk import CircuitBreaker

__all__ = ["CircuitBreaker", "ExecutionContext"]