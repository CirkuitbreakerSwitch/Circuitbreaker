"""
Basic test of CircuitBreaker SDK
"""

import sys
sys.path.insert(0, '.')

from circuitbreaker import CircuitBreaker, ExecutionContext

def test_basic():
    """Test basic CircuitBreaker functionality"""
    print("=" * 50)
    print("CIRCUITBREAKER BASIC TEST")
    print("=" * 50)
    
    # Create CircuitBreaker instance
    cb = CircuitBreaker()
    print("\n✓ CircuitBreaker initialized")
    
    # Test 1: Safe operation (should allow)
    print("\n--- Test 1: Safe file read ---")
    result = cb.evaluate(
        tool="file.read",
        params={"path": "/tmp/test.txt"},
        context=ExecutionContext(environment="development")
    )
    print(f"Tool: file.read")
    print(f"Action: {result.action}")
    print(f"Risk: {result.risk_level}")
    print(f"Allowed: {result.allowed}")
    print(f"Time: {result.execution_time_ms:.2f}ms")
    
    # Test 2: Dangerous operation in dev (should allow but warn)
    print("\n--- Test 2: File delete in development ---")
    result = cb.evaluate(
        tool="file.delete",
        params={"path": "/tmp/old.txt"},
        context=ExecutionContext(environment="development")
    )
    print(f"Tool: file.delete")
    print(f"Action: {result.action}")
    print(f"Risk: {result.risk_level}")
    print(f"Allowed: {result.allowed}")
    print(f"Reason: {result.reason}")
    
    # Test 3: Dangerous operation in production (should BLOCK)
    print("\n--- Test 3: File delete in production ---")
    result = cb.evaluate(
        tool="file.delete",
        params={"path": "/important/data.txt"},
        context=ExecutionContext(environment="production")
    )
    print(f"Tool: file.delete")
    print(f"Action: {result.action}")
    print(f"Risk: {result.risk_level}")
    print(f"Allowed: {result.allowed}")
    print(f"Reason: {result.reason}")
    
    # Test 4: SQL with DROP TABLE (should BLOCK)
    print("\n--- Test 4: SQL DROP TABLE ---")
    result = cb.evaluate(
        tool="db.query",
        params={"query": "DROP TABLE users"},
        context=ExecutionContext(environment="production")
    )
    print(f"Tool: db.query")
    print(f"Action: {result.action}")
    print(f"Risk: {result.risk_level}")
    print(f"Allowed: {result.allowed}")
    print(f"Reason: {result.reason}")
    
    print("\n" + "=" * 50)
    print("TEST COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    test_basic()