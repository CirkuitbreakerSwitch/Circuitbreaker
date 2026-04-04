# CircuitBreaker ⛔

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.11+-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()
[![Docker](https://img.shields.io/badge/docker-ready-blue)]()

**The seatbelt for AI agents** — Real-time intervention layer to prevent catastrophic AI agent actions.

&gt; "33% of organizations deployed AI agents. 97% admit they lack proper controls."
&gt; — Replit's AI deleted production databases. Tea app exposed private data.

## ⚡ 30-Second Demo

```bash
pip install circuitbreaker
python -c "
from circuitbreaker import CircuitBreaker, ExecutionContext
cb = CircuitBreaker()
result = cb.evaluate('file.delete', {'path': '/prod/data'}, ExecutionContext('production'))
print(f'Action: {result.action}')  # Output: Action: block
"

🚀 Quick Start
from circuitbreaker import CircuitBreaker, ExecutionContext

cb = CircuitBreaker()

# This will be BLOCKED in production
result = cb.evaluate(
    tool="file.delete",
    params={"path": "/production/data.txt"},
    context=ExecutionContext(environment="production")
)

print(f"🚫 {result.reason}")  # Policy 'No File Deletion in Production' matched

✨ Features
⚡ <10ms response with Redis cache
🤖 AI-powered analysis (LLM Judge for novel attacks)
🛡️ 5 default guardrails (file delete, SQL injection, API keys, etc.)
📊 SOC 2 ready (audit exports, compliance reports)
🔧 Works with any agent (Cursor, LangChain, OpenAI, custom)
📱 CLI + API (status, metrics, health checks)
🐳 Docker ready (one command deploy)

🛡️ Default Protections
| Action                      | Protection                       |
| --------------------------- | -------------------------------- |
| File deletion in production | ❌ Blocked                        |
| SQL DROP TABLE              | ❌ Blocked                        |
| API key exposure            | ❌ Blocked                        |
| Production deploy           | ⚠️ Escalated (requires approval) |
| Rate limiting               | 🚫 100 req/min                   |

📦 Installation
# Quick install
pip install circuitbreaker

# Or with Docker
docker-compose up -d

🔧 Usage
from circuitbreaker import CircuitBreaker, ExecutionContext

# Initialize
cb = CircuitBreaker()

# Check health
print(cb.get_health())
# {'status': 'healthy', 'metrics': {...}}

# Evaluate action
result = cb.evaluate(
    tool="db.query",
    params={"query": "DROP TABLE users"},
    context=ExecutionContext(environment="production")
)

if result.action == "block":
    print(f"🚫 Blocked: {result.reason}")

📊 Architecture
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  AI Agent   │────▶│ CircuitBreaker│────▶│   Tool      │
└─────────────┘     └──────┬───────┘     └─────────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
         ┌────▼────┐  ┌────▼────┐  ┌────▼────┐
         │  Redis  │  │ Policy  │  │PostgreSQL│
         │  Cache  │  │ Engine  │  │  Audit   │
         └─────────┘  └────┬────┘  └─────────┘
                          │
              ┌───────────┼───────────┐
              │           │           │
         ┌────▼───┐  ┌───▼────┐  ┌───▼────┐
         │ Metrics│  │ Slack  │  │ Email  │
         │        │  │        │  │        │
         └────────┘  └────────┘  └────────┘
              │
         ┌────▼────┐
         │LLM Judge│  ← AI-powered analysis
         └─────────┘

🖥️ CLI Commands
cb status              # System status
cb metrics             # Performance metrics
cb health              # Health check (JSON)
cb export --format csv # Compliance export

🔗 Integrations
Cursor
LangChain
OpenAI Functions

📚 Documentation
Getting Started
Architecture
API Reference

🤝 Contributing
We welcome contributions! See CONTRIBUTING.md.

📄 License
MIT © Cirkuitbreaker

Ready to protect your AI agents? Get Started →


