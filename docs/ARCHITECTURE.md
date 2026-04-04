# CircuitBreaker Architecture

## Overview

CircuitBreaker uses a layered architecture for maximum flexibility and performance.

## Components

### 1. SDK Layer (`circuitbreaker/sdk.py`)
Main interface. Handles:
- Request validation
- Component orchestration
- Result formatting

### 2. Policy Engine (`circuitbreaker/policy.py`)
Evaluates policies:
- Tool matching
- Content pattern matching
- Rate limiting
- Rule evaluation

### 3. Risk Evaluator (`circuitbreaker/evaluator.py`)
Assesses risk:
- Heuristic analysis (fast)
- LLM Judge (novel patterns)
- Risk scoring

### 4. Cache Layer (`circuitbreaker/cache.py`)
Redis caching:
- Sub-millisecond lookups
- Automatic TTL
- Cache invalidation

### 5. Audit Layer (`circuitbreaker/audit.py`)
Persistent logging:
- PostgreSQL storage
- Queryable logs
- Export formats (CSV, JSON)

### 6. Notification Layer
Multiple channels:
- Slack (instant)
- Email (SMTP)
- Webhooks (custom)
- Console (fallback)

### 7. Metrics Layer (`circuitbreaker/metrics.py`)
Observability:
- Request counts
- Latency tracking
- Health checks
- Performance stats

## Data Flow

Request → Cache Check → Policy Check → Risk Eval → Decision
↓               ↓              ↓           ↓
Cache Hit      Rule Match    Risk Score   Action
↓               ↓              ↓           ↓
Return      Audit Log    Notify      Execute


## Extension Points

- Custom policies (`policies.yaml`)
- Custom risk evaluators
- Custom notification channels
- Custom cache backends

