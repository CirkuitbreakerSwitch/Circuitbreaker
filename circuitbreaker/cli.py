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
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export audit logs")
    export_parser.add_argument("--format", choices=["csv", "json", "summary"], 
                              default="summary", help="Export format")
    export_parser.add_argument("--days", type=int, default=30, 
                              help="Number of days to export")
    export_parser.add_argument("--output", "-o", help="Output file")
    
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
    elif args.command == "export":
        cmd_export(args.format, args.days, args.output)
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


def cmd_export(format_type: str, days: int, output: Optional[str]):
    """Export audit logs"""
    print("=" * 60)
    print("AUDIT EXPORT")
    print("=" * 60)
    
    from .audit_export import AuditExporter
    from .config import Config
    
    exporter = AuditExporter(Config.DATABASE_URL)
    
    if format_type == "summary":
        summary = exporter.export_summary(days=days)
        print(f"\nCompliance Summary (last {days} days):")
        print(f"  Total evaluations: {summary['total_evaluations']}")
        print(f"  Blocked: {summary['blocked_actions']}")
        print(f"  Escalated: {summary['escalated_actions']}")
        print(f"  Block rate: {summary['block_rate']}%")
        
        if output:
            import json
            with open(output, 'w') as f:
                json.dump(summary, f, indent=2)
            print(f"\nSaved to: {output}")
    
    elif format_type == "csv":
        csv_data = exporter.export_csv()
        if output:
            with open(output, 'w') as f:
                f.write(csv_data)
            print(f"CSV exported to: {output}")
        else:
            print("\nCSV Data:")
            print(csv_data[:500] + "..." if len(csv_data) > 500 else csv_data)
    
    elif format_type == "json":
        events = exporter.export_json()
        print(f"\nExported {len(events)} events")
        if output:
            import json
            with open(output, 'w') as f:
                json.dump(events, f, indent=2, default=str)
            print(f"Saved to: {output}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()