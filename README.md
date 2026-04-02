# CircuitBreaker ⛔

**The seatbelt for AI agents**

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.11+-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

CircuitBreaker is a real-time intervention layer that prevents AI agents from causing catastrophic damage. It sits between your AI agents and their tools, evaluating every action in milliseconds.

&gt; "33% of organizations deployed AI agents. 97% admit they lack proper controls."

## 🚨 The Problem

- Replit's AI deleted live production databases
- Tea app exposed private data due to unverified AI-generated security
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
- **Agent-agnostic** - Works with Cursor, Claude Code, LangChain, OpenAI
- **5 default guardrails** - Production-ready out of the box
- **Rate limiting** - DDoS protection from runaway agents
- **Full audit trail** - Every decision logged to PostgreSQL
- **Real-time metrics** - Health checks and performance monitoring
- **Multiple notifications** - Slack, Email, Webhooks
- **CLI tool** - Easy management and monitoring
- **Docker support** - Production deployment ready
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
| `rate_limit`          | Block    | 100 requests/minute per user       |

📊 Architecture
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  AI Agent   │────▶│ CircuitBreaker│────▶│   Tool      │
│  (Any)      │     │    SDK        │     │ Execution   │
└─────────────┘     └──────┬───────┘     └─────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐       ┌────▼────┐       ┌────▼────┐
   │  Redis  │       │ Policy  │       │PostgreSQL│
   │  Cache  │       │ Engine  │       │  Audit   │
   └─────────┘       └────┬────┘       └─────────┘
                          │
              ┌───────────┼───────────┐
              │           │           │
         ┌────▼───┐  ┌───▼────┐  ┌───▼────┐
         │ Metrics│  │ Slack  │  │ Email  │
         │        │  │        │  │        │
         └────────┘  └────────┘  └────────┘


🔧 Integrations
Cursor - examples/cursor_integration.py
LangChain - examples/langchain_integration.py
OpenAI Functions - examples/openai_integration.py

🐳 Docker
docker-compose up -d

📟 CLI
cb status      # System status
cb metrics     # Performance metrics
cb health      # Health check (JSON)
cb test        # Test evaluation
cb config      # Show configuration

📚 Documentation
Installation Guide
API Reference

🧪 Testing
python -m pytest tests/ -v

## 🔌 Community Integrations

Built an integration? Submit a PR!

| Integration | Author | Status |
|-------------|--------|--------|
| Cursor | Official | ✅ |
| LangChain | Official | ✅ |
| OpenAI Functions | Official | ✅ |
| Your Integration | You | 🔄 [Submit PR](https://github.com/CirkuitbreakerSwitch/Circuitbreaker/pulls) |

See `examples/` folder for integration patterns.

🤝 Contributing
PRs welcome! See GitHub issues for ideas.

📄 License
    MIT

Ready to protect your AI agents? Get started →

---

**Save and commit:**

```bash
git add README.md
git commit -m "Update README with all new features: rate limiting, metrics, CLI, Docker, webhooks, email"
git push origin master


