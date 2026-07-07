# Pre-Deploy Checklist

## P0 — Blocks Deploy
- [ ] CLAUDE.md under 200 lines, tested ("run tests" works first try)
- [ ] System prompt with explicit CAN/CANNOT rules per agent
- [ ] Approval gates in orchestrator code (not just in prompt)
- [ ] Schema validation at every agent boundary (Pydantic)
- [ ] Action logging with business context in DB
- [ ] Idempotency: re-executing never duplicates effects
- [ ] Credentials in env vars, never in code/prompts/logs
- [ ] Test suite with real anonymized data (min 20 cases)
- [ ] Timeouts on all external API calls
- [ ] Error handling: retry with backoff + human escalation

## P1 — First Week
- [ ] Circuit breaker for external APIs
- [ ] Rate limiting (tokens + actions per cycle)
- [ ] Prompts versioned with changelog
- [ ] Per-client config separated from code
- [ ] Parking lot for uncertain/edge cases
- [ ] Memory/rehydration functional
- [ ] Basic alerts (error rate, budget, inactivity)
- [ ] Per-client state documented

## P2 — First Month
- [ ] Monitoring dashboard
- [ ] Dry-run mode (log without executing)
- [ ] Docker + CI/CD pipeline
- [ ] Automated health checks
- [ ] Quality metrics (categorization accuracy, etc.)
- [ ] Cross-model review integrated in workflow
