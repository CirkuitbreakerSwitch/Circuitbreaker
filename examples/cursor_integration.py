"""
Cursor Integration Example for CircuitBreaker

This shows how to wrap Cursor's tool calls with CircuitBreaker protection.
In real usage, this would be imported into Cursor's agent harness.
"""

import sys
sys.path.insert(0, '..')

from circuitbreaker import CircuitBreaker, ExecutionContext


# Initialize CircuitBreaker
cb = CircuitBreaker(
    policies_path="../policies.yaml"  # Use our default guardrails
)


class ProtectedTools:
    """
    Wrapper class that protects dangerous Cursor tools with CircuitBreaker.
    
    Usage in Cursor:
        tools = ProtectedTools()
        tools.delete_file("/path/to/file")  # Will block if in production
    """
    
    def __init__(self, environment="development"):
        self.context = ExecutionContext(environment=environment)
    
    def delete_file(self, path: str):
        """
        Protected file deletion - blocks in production
        """
        # Evaluate with CircuitBreaker
        result = cb.evaluate(
            tool="file.delete",
            params={"path": path},
            context=self.context
        )
        
        if not result.allowed:
            print(f"🚫 BLOCKED: {result.reason}")
            print(f"   Risk level: {result.risk_level}")
            print(f"   Request ID: {result.request_id}")
            raise PermissionError(f"CircuitBreaker blocked: {result.reason}")
        
        # If allowed, proceed with actual deletion
        print(f"✅ ALLOWED: Deleting {path}")
        # Actual file deletion would happen here
        # import os; os.remove(path)
        return f"Deleted {path}"
    
    def execute_sql(self, query: str):
        """
        Protected SQL execution - blocks dangerous queries
        """
        result = cb.evaluate(
            tool="db.query",
            params={"query": query},
            context=self.context
        )
        
        if not result.allowed:
            print(f"🚫 BLOCKED: {result.reason}")
            raise PermissionError(f"CircuitBreaker blocked: {result.reason}")
        
        print(f"✅ ALLOWED: Executing SQL query")
        # Actual SQL execution would happen here
        return f"Executed: {query[:50]}..."
    
    def deploy_to_production(self, version: str):
        """
        Protected deployment - requires approval in production
        """
        result = cb.evaluate(
            tool="deploy.execute",
            params={"version": version, "target": "production"},
            context=self.context
        )
        
        if result.action == "escalate":
            print(f"⏸️ ESCALATED: {result.reason}")
            print(f"   This action requires human approval.")
            print(f"   Request ID: {result.request_id}")
            # In real implementation, send Slack notification
            # and wait for approval
            raise PermissionError("Action escalated for approval")
        
        if not result.allowed:
            print(f"🚫 BLOCKED: {result.reason}")
            raise PermissionError(f"CircuitBreaker blocked: {result.reason}")
        
        print(f"✅ ALLOWED: Deploying {version} to production")
        return f"Deployed {version}"


def demo():
    """Demonstrate CircuitBreaker protection"""
    print("=" * 60)
    print("CIRCUITBREAKER + CURSOR INTEGRATION DEMO")
    print("=" * 60)
    
    # Scenario 1: Development (safe environment)
    print("\n--- Scenario 1: Development Environment ---")
    dev_tools = ProtectedTools(environment="development")
    
    try:
        dev_tools.delete_file("/tmp/test.txt")
    except PermissionError as e:
        print(f"Error: {e}")
    
    # Scenario 2: Production (dangerous operations blocked)
    print("\n--- Scenario 2: Production Environment ---")
    prod_tools = ProtectedTools(environment="production")
    
    try:
        prod_tools.delete_file("/important/data.txt")
    except PermissionError as e:
        print(f"Error: {e}")
    
    # Scenario 3: SQL injection attempt
    print("\n--- Scenario 3: SQL DROP TABLE Attempt ---")
    try:
        prod_tools.execute_sql("DROP TABLE users")
    except PermissionError as e:
        print(f"Error: {e}")
    
    # Scenario 4: Deployment escalation
    print("\n--- Scenario 4: Production Deployment ---")
    try:
        prod_tools.deploy_to_production("v1.2.3")
    except PermissionError as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print("\nIn real usage, these protections would be transparent")
    print("to the AI agent, preventing disasters before they happen.")


if __name__ == "__main__":
    demo()