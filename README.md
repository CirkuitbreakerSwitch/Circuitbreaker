# CircuitBreaker

**The seatbelt for AI agents**

CircuitBreaker is a real-time intervention layer that prevents AI agents from causing catastrophic damage. It sits between your AI agents and their tools, evaluating every action for risk before execution.

## Quick Start

```bash
pip install circuitbreaker 

Features
⚡ Millisecond-level intervention - Blocks dangerous actions in real-time
🔧 5-minute setup - Not 5-week procurement
🛡️ Agent-agnostic - Works with Cursor, Claude Code, LangChain, and more
📊 Full audit trail - Every decision logged to PostgreSQL
🔔 Slack integration - Human-in-the-loop for escalations

How It Works
AI Agent Decision → CIRCUITBREAKER → Tool Execution
                         ↓
                   Risk Evaluation
                   (heuristics + LLM judge)
                         ↓
              Block / Escalate / Allow

Default Guardrails
❌ No file deletion in production
❌ No DROP TABLE statements
❌ No API key exposure
⚠️ Production deploys require approval
⚠️ Large SQL operations require approval