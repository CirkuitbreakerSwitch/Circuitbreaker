"""
Test notifications for blocks and escalations
"""

from circuitbreaker import CircuitBreaker, ExecutionContext

cb = CircuitBreaker()

print("=" * 60)
print("NOTIFICATION TEST")
print("=" * 60)

# This should trigger a block notification
print("\n1. Testing BLOCK notification...")
try:
    result = cb.evaluate(
        tool="file.delete",
        params={"path": "/production/data.txt"},
        context=ExecutionContext(environment="production")
    )
    print(f"Result: {result.action}")
except Exception as e:
    print(f"Error: {e}")

# This should trigger an escalate notification  
print("\n2. Testing ESCALATE notification...")
try:
    result = cb.evaluate(
        tool="deploy.execute",
        params={"version": "v1.0.0"},
        context=ExecutionContext(environment="production")
    )
    print(f"Result: {result.action}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("Check above for notification banners")
print("=" * 60)