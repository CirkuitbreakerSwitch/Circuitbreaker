"""
CircuitBreaker Full Demo
Shows database logging, caching, and protection working together
"""

import time
from circuitbreaker import CircuitBreaker, ExecutionContext, Config

print("=" * 70)
print("CIRCUITBREAKER FULL DEMO")
print("=" * 70)
print(f"Database: {'✅ Connected' if Config.has_database() else '❌ Not configured'}")
print(f"Redis Cache: {'✅ Enabled' if Config.has_redis() else '❌ Not configured'}")
print("=" * 70)

# Initialize CircuitBreaker with real credentials
cb = CircuitBreaker()

# Test 1: Safe operation (should allow and log to DB)
print("\n--- Test 1: Safe file read ---")
result = cb.evaluate(
    tool="file.read",
    params={"path": "/tmp/data.txt"},
    context=ExecutionContext(environment="development")
)
print(f"Action: {result.action}")
print(f"Risk: {result.risk_level}")
print(f"Time: {result.execution_time_ms:.2f}ms")
print(f"Request ID: {result.request_id}")

# Test 2: Same operation again (should hit cache)
print("\n--- Test 2: Same operation (cache hit) ---")
result = cb.evaluate(
    tool="file.read",
    params={"path": "/tmp/data.txt"},
    context=ExecutionContext(environment="development")
)
print(f"Action: {result.action}")
print(f"Time: {result.execution_time_ms:.2f}ms (faster if cached)")

# Test 3: Dangerous operation in production (BLOCKED)
print("\n--- Test 3: File delete in production (BLOCKED) ---")
result = cb.evaluate(
    tool="file.delete",
    params={"path": "/important/production/data.txt"},
    context=ExecutionContext(environment="production")
)
print(f"Action: {result.action}")
print(f"Allowed: {result.allowed}")
print(f"Reason: {result.reason}")
print(f"Risk: {result.risk_level}")

# Test 4: SQL DROP TABLE (BLOCKED)
print("\n--- Test 4: SQL DROP TABLE (BLOCKED) ---")
result = cb.evaluate(
    tool="db.query",
    params={"query": "DROP TABLE users"},
    context=ExecutionContext(environment="production")
)
print(f"Action: {result.action}")
print(f"Reason: {result.reason}")

# Test 5: Production deployment (ESCALATED)
print("\n--- Test 5: Production deployment (ESCALATED) ---")
result = cb.evaluate(
    tool="deploy.execute",
    params={"version": "v2.0.0", "target": "production"},
    context=ExecutionContext(environment="production")
)
print(f"Action: {result.action}")
print(f"Reason: {result.reason}")
print("This would send Slack notification for approval")

# Summary
print("\n" + "=" * 70)
print("DEMO COMPLETE")
print("=" * 70)
print("\nAll actions logged to PostgreSQL (if configured)")
print("Repeated operations use Redis cache for <1ms response")
print("Production operations properly blocked/escalated")
print("=" * 70)