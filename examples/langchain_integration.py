"""
LangChain Integration for CircuitBreaker
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from circuitbreaker import CircuitBreaker, ExecutionContext


class ProtectedLangChainTools:
    """Wrapper for LangChain tools with CircuitBreaker protection"""
    
    def __init__(self, environment="development"):
        self.cb = CircuitBreaker()
        self.context = ExecutionContext(environment=environment)
    
    def delete_file(self, path: str) -> str:
        """Protected file deletion"""
        result = self.cb.evaluate(
            tool="file.delete",
            params={"path": path},
            context=self.context
        )
        
        if not result.allowed:
            return f"🚫 BLOCKED: {result.reason}"
        
        return f"✅ Deleted {path}"


def demo():
    """Demonstrate LangChain integration"""
    print("=" * 60)
    print("LANGCHAIN INTEGRATION DEMO")
    print("=" * 60)
    
    tools = ProtectedLangChainTools(environment="production")
    
    print("\n🤖 Agent: 'I'll delete that old file...'")
    print(tools.delete_file("/production/data.txt"))
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    demo()