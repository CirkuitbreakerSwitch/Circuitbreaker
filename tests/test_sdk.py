"""
Test suite for CircuitBreaker SDK
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from circuitbreaker import CircuitBreaker, ExecutionContext, Config


class TestCircuitBreaker(unittest.TestCase):
    """Test core CircuitBreaker functionality"""
    
    def setUp(self):
        """Set up test instance"""
        self.cb = CircuitBreaker()
        self.dev_context = ExecutionContext(environment="development")
        self.prod_context = ExecutionContext(environment="production")
    
    def test_initialization(self):
        """Test CircuitBreaker initializes correctly"""
        self.assertIsNotNone(self.cb)
        self.assertIsNotNone(self.cb.policy_engine)
        self.assertIsNotNone(self.cb.evaluator)
        self.assertIsNotNone(self.cb.audit)
    
    def test_safe_operation_allowed(self):
        """Test safe operations are allowed"""
        result = self.cb.evaluate(
            tool="file.read",
            params={"path": "/tmp/test.txt"},
            context=self.dev_context
        )
        self.assertTrue(result.allowed)
        self.assertEqual(result.action, "allow")
    
    def test_file_delete_blocked_in_production(self):
        """Test file deletion is blocked in production"""
        result = self.cb.evaluate(
            tool="file.delete",
            params={"path": "/important/data.txt"},
            context=self.prod_context
        )
        self.assertFalse(result.allowed)
        self.assertEqual(result.action, "block")
    
    def test_drop_table_blocked(self):
        """Test DROP TABLE is blocked"""
        result = self.cb.evaluate(
            tool="db.query",
            params={"query": "DROP TABLE users"},
            context=self.prod_context
        )
        self.assertFalse(result.allowed)
        self.assertEqual(result.action, "block")


if __name__ == "__main__":
    unittest.main(verbosity=2)