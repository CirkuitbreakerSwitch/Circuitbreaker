# CircuitBreaker ⛔

**The seatbelt for AI agents**

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.11+-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

CircuitBreaker is a real-time intervention layer that prevents AI agents from causing catastrophic damage. It sits between your AI agents and their tools, evaluating every action in milliseconds.

&gt; "33% of organizations deployed AI agents. 97% admit they lack proper controls."  
&gt; — Recent industry survey

## 🚨 The Problem

- Replit's AI deleted live production databases
- Tea app exposed women's private data due to unverified AI-generated security
- Browser agents operate at "Level 4-5 autonomy" with zero guardrails
- Existing solutions take 5 weeks to procure, not 5 minutes to set up

## ✅ The Solution

AI Agent Decision → CIRCUITBREAKER → Tool Execution
↓
Risk Evaluation
(heuristics + LLM judge)
↓
Block / Escalate / Allow


## ⚡ Features

- **Millisecond-level intervention** - Sub-10ms with Redis cache
- **5-minute setup** - Not 5-week procurement
- **Agent-agnostic** - Works with Cursor, Claude Code, LangChain, custom agents
- **5 default guardrails** - Production-ready out of the box
- **Full audit trail** - Every decision logged to PostgreSQL
- **Slack integration** - Human-in-the-loop for escalations
- **Open source** - MIT licensed, community-driven

## 🚀 Quick Start

```bash
pip install circuitbreaker

from circuitbreaker import CircuitBreaker, ExecutionContext

cb = CircuitBreaker()

# Evaluate a tool call
result = cb.evaluate(
    tool="file.delete",
    params={"path": "/important/data.txt"},
    context=ExecutionContext(environment="production")
)

if not result.allowed:
    print(f"🚫 Blocked: {result.reason}")
else:
    print(f"✅ Allowed")


🛡️ Default Guardrails
| Policy                | Action   | Description                        |
| --------------------- | -------- | ---------------------------------- |
| `no_prod_delete`      | Block    | No file deletion in production     |
| `no_drop_table`       | Block    | No SQL DROP TABLE statements       |
| `no_api_key_exposure` | Block    | Prevents API keys in output        |
| `no_prod_deploy`      | Escalate | Production deploys need approval   |
| `no_large_sql`        | Escalate | Large SQL operations need approval |


📊 Architecture
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  AI Agent   │────▶│ CircuitBreaker│────▶│   Tool      │
│  (Cursor)   │     │    SDK        │     │ Execution   │
└─────────────┘     └──────┬───────┘     └─────────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
         ┌────▼────┐  ┌────▼────┐  ┌────▼────┐
         │  Redis  │  │ Policy  │  │PostgreSQL│
         │  Cache  │  │ Engine  │  │  Audit   │
         └─────────┘  └─────────┘  └─────────┘

🔧 Configuration
## 🔧 Optional Configuration

CircuitBreaker works out of the box with sensible defaults. For production use, configure:

```bash
# Optional: Redis for caching (faster evaluations)
REDIS_URL=redis://your-upstash-url
REDIS_TOKEN=your-token

# Optional: PostgreSQL for audit logging
DATABASE_URL=postgresql://your-neon-url

# Optional: Slack for notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/...

