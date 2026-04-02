"""
OpenAI Functions Integration for CircuitBreaker

Shows how to protect OpenAI function calls with CircuitBreaker
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from circuitbreaker import CircuitBreaker, ExecutionContext


class ProtectedOpenAIFunctions:
    """
    Wrapper for OpenAI function calls with CircuitBreaker protection
    
    Usage with OpenAI API:
        functions = ProtectedOpenAIFunctions(environment="production")
        
        # In your OpenAI function handler
        response = functions.handle_function_call(
            function_name="delete_file",
            arguments={"path": "/file.txt"}
        )
    """
    
    def __init__(self, environment="development"):
        self.cb = CircuitBreaker()
        self.context = ExecutionContext(environment=environment)
    
    def handle_function_call(self, function_name: str, arguments: dict) -> dict:
        """
        Handle an OpenAI function call with protection
        
        Returns:
            dict with result or error message
        """
        # Map OpenAI function names to CircuitBreaker tools
        tool_mapping = {
            "delete_file": "file.delete",
            "execute_sql": "db.query",
            "deploy": "deploy.execute",
            "write_file": "file.write",
            "read_file": "file.read"
        }
        
        tool = tool_mapping.get(function_name, function_name)
        
        result = self.cb.evaluate(
            tool=tool,
            params=arguments,
            context=self.context
        )
        
        if not result.allowed:
            return {
                "status": "blocked",
                "reason": result.reason,
                "risk_level": result.risk_level,
                "request_id": result.request_id,
                "message": f"Action blocked by CircuitBreaker: {result.reason}"
            }
        
        if result.action == "escalate":
            return {
                "status": "escalated",
                "reason": result.reason,
                "risk_level": result.risk_level,
                "request_id": result.request_id,
                "message": f"Action escalated for approval: {result.reason}"
            }
        
        # In real usage, execute the actual function here
        return {
            "status": "allowed",
            "action": result.action,
            "message": f"Action allowed: {function_name}",
            "request_id": result.request_id
        }


def demo():
    """Demonstrate OpenAI Functions integration"""
    print("=" * 60)
    print("OPENAI FUNCTIONS INTEGRATION DEMO")
    print("=" * 60)
    
    functions = ProtectedOpenAIFunctions(environment="production")
    
    # Simulate OpenAI function calls
    scenarios = [
        ("read_file", {"path": "/tmp/data.txt"}),
        ("delete_file", {"path": "/production/critical.db"}),
        ("execute_sql", {"query": "DROP TABLE users"}),
        ("deploy", {"version": "v2.0.0", "target": "production"})
    ]
    
    for func_name, args in scenarios:
        print(f"\n🤖 OpenAI calls: {func_name}({args})")
        result = functions.handle_function_call(func_name, args)
        print(f"   Result: {result['status'].upper()}")
        print(f"   Message: {result['message']}")
    
    print("\n" + "=" * 60)
    print("All function calls evaluated and protected")
    print("=" * 60)


if __name__ == "__main__":
    demo()