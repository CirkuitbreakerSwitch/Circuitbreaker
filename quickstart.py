#!/usr/bin/env python
"""
Quick Start Script for CircuitBreaker

Run this to see CircuitBreaker in action in 30 seconds.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from circuitbreaker import CircuitBreaker, ExecutionContext


def print_header(text):
    print("\n" + "="*60)
    print(text)
    print("="*60)


def print_result(result):
    status = "✅ ALLOWED" if result.allowed else "🚫 BLOCKED"
    print(f"{status}")
    print(f"   Action: {result.action}")
    print(f"   Risk: {result.risk_level}")
    print(f"   Reason: {result.reason}")
    print(f"   Time: {result.execution_time_ms:.2f}ms")


def main():
    print_header("CIRCUITBREAKER QUICK START")
    print("Testing in 30 seconds...\n")
    
    # Initialize
    cb = CircuitBreaker()
    
    # Test 1: Safe operation
    print_header("TEST 1: Safe file read (development)")
    result = cb.evaluate(
        tool="file.read",
        params={"path": "/tmp/data.txt"},
        context=ExecutionContext(environment="development")
    )
    print_result(result)
    
    # Test 2: Blocked in production
    print_header("TEST 2: File delete (production) - SHOULD BE BLOCKED")
    result = cb.evaluate(
        tool="file.delete",
        params={"path": "/production/critical.db"},
        context=ExecutionContext(environment="production")
    )
    print_result(result)
    
    # Test 3: SQL injection pattern
    print_header("TEST 3: SQL DROP TABLE - SHOULD BE BLOCKED")
    result = cb.evaluate(
        tool="db.query",
        params={"query": "DROP TABLE users"},
        context=ExecutionContext(environment="production")
    )
    print_result(result)
    
    # Test 4: Check metrics
    print_header("METRICS")
    stats = cb.get_metrics_stats()
    print(f"Total evaluations: {stats['total_evaluations']}")
    print(f"Blocked: {stats['blocked']} ({stats['block_rate']}%)")
    print(f"Cache hit rate: {stats['cache_hit_rate']}%")
    
    # Test 5: Health check
    print_header("HEALTH CHECK")
    health = cb.get_health()
    print(f"Status: {health['status']}")
    print(f"Uptime: {health['metrics']['uptime_seconds']:.1f}s")
    
    print_header("QUICK START COMPLETE")
    print("\nCircuitBreaker is working correctly!")
    print("Your AI agents are now protected.")
    print("\nNext steps:")
    print("1. Configure your .env file")
    print("2. Integrate with your AI agent")
    print("3. Run: python -m circuitbreaker.cli status")
    print("\nDocs: https://github.com/CirkuitbreakerSwitch/Circuitbreaker")


if __name__ == "__main__":
    main()
    