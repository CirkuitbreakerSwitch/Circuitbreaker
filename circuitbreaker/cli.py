"""
CircuitBreaker CLI - Command line interface for management
"""

import argparse
import sys
import json
from typing import Optional

from . import CircuitBreaker, ExecutionContext, Config
from .metrics import get_metrics


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="CircuitBreaker - Kill Switch for AI Agents",
        prog="cb"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Check CircuitBreaker status")
    
    # Metrics command
    metrics_parser = subparsers.add_parser("metrics", help="Show metrics and statistics")
    
    # Health command
    health_parser = subparsers.add_parser("health", help="Check health status")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Run a test evaluation")
    test_parser.add_argument("--tool", default="file.read", help="Tool to test")
    test_parser.add_argument("--env", default="development", help="Environment")
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Show configuration")
    
    args = parser.parse_args()
    
    if args.command == "status":
        cmd_status()
    elif args.command == "metrics":
        cmd_metrics()
    elif args.command == "health":
        cmd_health()
    elif args.command == "test":
        cmd_test(args.tool, args.env)
    elif args.command == "config":
        cmd_config()
    else:
        parser.print_help()


def cmd_status():
    """Show CircuitBreaker status"""
    print("=" * 60)
    print("CIRCUITBREAKER STATUS")
    print("=" * 60)
    
    cb = CircuitBreaker()
    
    print(f"\nVersion: 0.1.0")
    print(f"Environment: {Config.ENVIRONMENT}")
    print(f"Database: {'✅ Connected' if Config.has_database() else '❌ Not configured'}")
    print(f"Redis Cache: {'✅ Enabled' if Config.has_redis() else '❌ Not configured'}")
    print(f"Slack: {'✅ Configured' if Config.SLACK_WEBHOOK_URL else '❌ Not configured'}")
    
    health = cb.get_health()
    print(f"\nHealth Status: {health['status'].upper()}")
    print(f"Message: {health['message']}")
    print(f"Uptime: {health['metrics']['uptime_seconds']:.1f}s")
    print(f"Total Evaluations: {health['metrics']['total_evaluations']}")
    
    print("\n" + "=" * 60)


def cmd_metrics():
    """Show detailed metrics"""
    print("=" * 60)
    print("CIRCUITBREAKER METRICS")
    print("=" * 60)
    
    cb = CircuitBreaker()
    stats = cb.get_metrics_stats()
    
    print(f"\nPerformance:")
    print(f"  Total Evaluations: {stats['total_evaluations']}")
    print(f"  Average Time: {stats['avg_execution_time_ms']:.2f}ms")
    print(f"  Uptime: {stats['uptime_seconds']:.1f}s")
    
    print(f"\nActions:")
    print(f"  Allowed: {stats['allowed']}")
    print(f"  Blocked: {stats['blocked']} ({stats['block_rate']}%)")
    print(f"  Escalated: {stats['escalated']}")
    
    print(f"\nCache:")
    print(f"  Hits: {stats['cache_hits']}")
    print(f"  Misses: {stats['cache_misses']}")
    print(f"  Hit Rate: {stats['cache_hit_rate']}%")
    
    print("\n" + "=" * 60)


def cmd_health():
    """Show health status"""
    cb = CircuitBreaker()
    health = cb.get_health()
    
    print(json.dumps(health, indent=2))


def cmd_test(tool: str, env: str):
    """Run a test evaluation"""
    print(f"Testing: {tool} in {env} environment")
    print("-" * 60)
    
    cb = CircuitBreaker()
    result = cb.evaluate(
        tool=tool,
        params={"path": "/test/file.txt"},
        context=ExecutionContext(environment=env)
    )
    
    print(f"Action: {result.action}")
    print(f"Allowed: {result.allowed}")
    print(f"Risk Level: {result.risk_level}")
    print(f"Reason: {result.reason}")
    print(f"Request ID: {result.request_id}")
    print(f"Time: {result.execution_time_ms:.2f}ms")


def cmd_config():
    """Show configuration (without secrets)"""
    print("=" * 60)
    print("CIRCUITBREAKER CONFIGURATION")
    print("=" * 60)
    
    print(f"\nEnvironment: {Config.ENVIRONMENT}")
    print(f"Database Configured: {Config.has_database()}")
    print(f"Redis Configured: {Config.has_redis()}")
    print(f"Slack Configured: {bool(Config.SLACK_WEBHOOK_URL)}")
    
    print(f"\nSecret Key: {'✅ Set' if Config.SECRET_KEY != 'default-secret-key-change-in-production' else '❌ Using default'}")
    
    print("\n" + "=" * 60)
    print("Note: Use .env file to configure these settings")
    print("=" * 60)


if __name__ == "__main__":
    main()