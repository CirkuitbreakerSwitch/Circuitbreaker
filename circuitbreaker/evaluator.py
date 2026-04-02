"""
Risk Evaluator - Evaluates risk of tool calls
"""

import re
from typing import Dict, Any

from .llm_judge import LLMJudge


class RiskEvaluator:
    """
    Evaluates the risk level of a tool execution request
    
    Uses heuristics for fast evaluation (90% of cases)
    Optional LLM judge for ambiguous cases
    """
    
    # High-risk tools that warrant extra scrutiny
    HIGH_RISK_TOOLS = [
        "file.delete", "file.write", "file.move",
        "db.drop", "db.delete", "db.query",
        "deploy.execute", "server.restart", "server.stop",
        "user.delete", "permission.grant"
    ]
    
    # Critical patterns that should always block
    CRITICAL_PATTERNS = [
        (r"(?i)DROP\s+TABLE", "SQL table deletion"),
        (r"(?i)DELETE\s+FROM\s+\w+\s+WHERE", "SQL delete operation"),
        (r"(?i)RM\s+-RF", "Force recursive delete"),
        (r"(sk-|pk-|ghp-|AKIA)[a-zA-Z0-9]{16,}", "API key exposure"),
    ]
    
    def __init__(self, use_llm_judge: bool = False):
        self.use_llm_judge = use_llm_judge
        self.llm_judge = LLMJudge() if use_llm_judge else None
    
    def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate risk level of a tool call
        
        Returns:
            Dict with 'level' (low/medium/high/critical) and 'factors'
        """
        tool = context.get("tool", "")
        params = context.get("params", {})
        environment = context.get("environment", "development")
        
        factors = []
        risk_score = 0
        
        # Factor 1: Tool inherent risk
        if any(tool.startswith(rt) or tool == rt for rt in self.HIGH_RISK_TOOLS):
            risk_score += 30
            factors.append(f"High-risk tool: {tool}")
        
        # Factor 2: Production environment
        if environment == "production":
            risk_score += 20
            factors.append("Production environment")
        
        # Factor 3: Critical patterns in params
        param_str = str(params)
        for pattern, description in self.CRITICAL_PATTERNS:
            if re.search(pattern, param_str):
                risk_score += 50
                factors.append(f"Critical pattern detected: {description}")
        
        # Factor 4: Destructive keywords
        destructive_keywords = ["delete", "drop", "remove", "destroy", "wipe"]
        if any(kw in param_str.lower() for kw in destructive_keywords):
            risk_score += 15
            factors.append("Destructive keywords detected")
        
        # Determine risk level
        if risk_score >= 70:
            level = "critical"
        elif risk_score >= 40:
            level = "high"
        elif risk_score >= 20:
            level = "medium"
        else:
            level = "low"
        
        heuristic_result = {
            "level": level,
            "score": risk_score,
            "factors": factors,
            "tool": tool,
            "environment": environment,
            "source": "heuristic"
        }
        
        # Escalate to LLM judge for ambiguous cases
        if self.llm_judge and self.llm_judge.should_escalate_to_llm(heuristic_result):
            llm_result = self.llm_judge.evaluate(context)
            if llm_result:
                # Use LLM result if higher risk
                risk_levels = ["low", "medium", "high", "critical"]
                if risk_levels.index(llm_result["level"]) > risk_levels.index(level):
                    return llm_result
        
        return heuristic_result
    
    def should_escalate_to_llm(self, risk_result: Dict[str, Any]) -> bool:
        """
        Decide if we need LLM judge for ambiguous cases
        
        Heuristics handle 90% of cases - LLM only for edge cases
        """
        if not self.use_llm_judge or not self.llm_judge:
            return False
        
        # Escalate to LLM if:
        # - Medium risk with multiple factors
        # - Uncertain classification
        if risk_result["level"] == "medium" and len(risk_result["factors"]) >= 2:
            return True
        
        return False