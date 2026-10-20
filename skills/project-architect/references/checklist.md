# Pre-Deploy Checklist

## P0 — Blocks Deploy
- [ ] CLAUDE.md under 200 lines, tested ("run tests" works first try)
- [ ] System prompt with explicit CAN/CANNOT rules per agent
- [ ] Approval gates in orchestrator code (not just in prompt)
- [ ] Schema validation at every agent boundary (Pydantic)
- [ ] Action logging with business context in DB
- [ ] Idempotency: re-executing never duplicates effects
- [ ] Credentials in env vars, never in code/prompts/logs
- [ ] `/security-review` clean on every merged feature; critical zones listed in CLAUDE.md
- [ ] DeepSec projects: full capped scan + `revalidate` before first deploy, no open P0 finding, `.deepsec/data/` + findings gitignored
- [ ] Test suite with real anonymized data (min 20 cases)
- [ ] Timeouts on all external API calls
- [ ] Error handling: retry with backoff + human escalation
- [ ] Every Must-Not-Trade-Off rule in CLAUDE.md has a committed, passing check
- [ ] `/direction` run since the last feature batch; drift adopted or reverted

## P1 — First Week
- [ ] Circuit breaker for external APIs
- [ ] Rate limiting (tokens + actions per cycle)
- [ ] DeepSec projects: `deepsec process --diff origin/main` as a CI gate (exit 1 fails the job), key from CI secrets, cost-capped
- [ ] Prompts versioned with changelog
- [ ] Per-client config separated from code
- [ ] Parking lot for uncertain/edge cases
- [ ] Memory/rehydration functional
- [ ] Basic alerts (error rate, budget, inactivity)
- [ ] Per-client state documented
- [ ] `breaker` run on an isolated copy; every confirmed break has a regression test
- [ ] Journey suite green (`tests/e2e/journeys.json`), `first-user` findings triaged (UI projects)

## P2 — First Month
- [ ] Monitoring dashboard
- [ ] Dry-run mode (log without executing)
- [ ] Docker + CI/CD pipeline
- [ ] Automated health checks
- [ ] Quality metrics (categorization accuracy, etc.)
- [ ] Cross-model review integrated in workflow
- [ ] Feedback loop once real users exist: Sentry + support inbox via MCP, clear breakage fixed fast, judgment calls escalated, time-to-resolution tracked
