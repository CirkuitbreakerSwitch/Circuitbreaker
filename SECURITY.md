# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

Please report security vulnerabilities to cirkuitbreaker@gmail.com.

We will respond within 48 hours.

## Data Handling

CircuitBreaker is designed with security-first principles:

### What We Store
- **Audit logs**: Tool calls, decisions, timestamps
- **No sensitive data**: We don't store API keys, passwords, or file contents
- **No PII**: We don't store personal information by default

### Data Protection
- All data encrypted at rest (PostgreSQL)
- Redis cache uses TLS
- Audit logs are immutable (append-only)

### Compliance Roadmap
- [ ] SOC 2 Type II (Q3 2026)
- [ ] ISO 27001 (Q4 2026)
- [ ] GDPR compliance (Q2 2026)

## Security Features

- Rate limiting (DDoS protection)
- Input validation
- SQL injection prevention
- API key pattern detection
- Production environment protection