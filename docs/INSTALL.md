# Installation Guide

## Quick Install

```bash
pip install circuitbreaker

Development Install
git clone https://github.com/CirkuitbreakerSwitch/Circuitbreaker.git
cd Circuitbreaker
pip install -r requirements.txt

Configuration
Create a .env file:
# Required for production
DATABASE_URL=postgresql://...
REDIS_URL=redis://...

# Optional notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
SMTP_SERVER=smtp.gmail.com
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_TO=admin@company.com

# Optional webhook
WEBHOOK_URL=https://your-company.com/webhook

Docker Install
docker-compose up -d

Verify Installation
python -m circuitbreaker.cli status


---

### **Step 3: Create API.md**

**New File** → `API.md`:

```markdown
# API Reference

## CircuitBreaker Class

### Constructor

```python
CircuitBreaker(
    redis_url=None,      # Redis connection URL
    database_url=None,   # PostgreSQL connection URL
    slack_webhook=None,  # Slack webhook URL
    policies_path=None   # Path to policies.yaml
)


Methods
evaluate()
Evaluate a tool call and return decision.

result = cb.evaluate(
    tool="file.delete",
    params={"path": "/file.txt"},
    context=ExecutionContext(environment="production")
)

# Returns: CircuitBreakerResult
# - allowed: bool
# - action: "allow" | "block" | "escalate"
# - reason: str
# - risk_level: "low" | "medium" | "high" | "critical"
# - request_id: str
# - execution_time_ms: float

protect()
Decorator to protect functions.
@cb.protect(tool="file.delete")
def delete_file(path):
    # Your code here
    pass


get_health()
Get system health status.
health = cb.get_health()
# Returns: {"status": "healthy", "metrics": {...}}
get_metrics_stats()
Get detailed metrics.
stats = cb.get_metrics_stats()
# Returns: {"total_evaluations": 100, "blocked": 5, ...}

ExecutionContext
context = ExecutionContext(
    environment="production",  # "development" | "staging" | "production"
    user="username",           # Optional user ID
    agent_type="cursor"        # Optional agent identifier
)

CLI Commands
cb status          # Show system status
cb metrics         # Show metrics
cb health          # Show health (JSON)
cb test            # Run test evaluation
cb config          # Show configuration


---

**Save both files and commit:**

```bash
git add docs/
git commit -m "Add comprehensive documentation: installation and API reference"
git push origin master



