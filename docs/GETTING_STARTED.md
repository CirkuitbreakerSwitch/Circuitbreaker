# Getting Started with CircuitBreaker

## Installation

### Option 1: pip (Recommended)
```bash
pip install circuitbreaker

Option 2: Docker
docker-compose up -d

Option 3: From Source
git clone https://github.com/CirkuitbreakerSwitch/Circuitbreaker.git
cd Circuitbreaker
pip install -r requirements.txt

Quick Test
Run the quickstart:
python quickstart.py

Basic Usage
from circuitbreaker import CircuitBreaker, ExecutionContext

cb = CircuitBreaker()

# Simple evaluation
result = cb.evaluate(
    tool="file.read",
    params={"path": "/tmp/data.txt"},
    context=ExecutionContext(environment="development")
)

print(result.action)  # "allow"

Configuration
Create .env file:
# Optional: Redis for caching
REDIS_URL=redis://...
REDIS_TOKEN=...

# Optional: PostgreSQL for audit logs
DATABASE_URL=postgresql://...

# Optional: Slack notifications
SLACK_WEBHOOK_URL=https://...

# Optional: Email notifications
SMTP_SERVER=smtp.gmail.com
SMTP_USERNAME=...
SMTP_PASSWORD=...
EMAIL_TO=admin@company.com







