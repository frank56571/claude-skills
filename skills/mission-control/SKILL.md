---
name: mission-control
description: Use ONLY when the user explicitly invokes /mission-control or explicitly asks to run a "mission" — long-running, multi-feature work executed by an orchestrated agent team. Never auto-trigger for regular tasks; normal work uses the normal workflow.
---

# Mission Control

Long-running execution mode (multi-feature builds spanning hours/days) based on the Factory "Missions" architecture: **orchestrator + serial workers + adversarial validators**, held together by a validation contract written before any code, structured handoffs, and file-based state that survives session restarts.

**Core principle: the contract defines "done" before code exists; validators verify against the contract, never against the implementation.**

## Roles

| Seat | Who | Model |
|------|-----|-------|
| Orchestrator | This session — scopes, plans, arbitrates milestones | Session model (Opus/Fable) |
| Worker | One subagent per feature, clean context | `sonnet` |
| Scrutiny validator | Fresh reviewer agents + ONE cross-provider reviewer | `references/model-seats.md` |
| User-testing validator | QA agent driving the live app | any |

Read `references/model-seats.md` before spawning any validator.

## Mission state — all on disk, sessions are disposable

```
mission/
  MISSION.md              # dashboard: goal, milestones, features, active seat, budget, log
  validation-contract.md  # numbered assertions — written BEFORE code, user-approved
  handoffs/<feature>.md   # one structured handoff per feature
```

`mission/MISSION.md` already exists → this is a RESUME: read it + the contract + all handoffs, announce current state, continue from the next incomplete step. Never restart a mission from scratch.

## Phases

### 1. Scope
Read the project's SecondBrain memory (`~/SecondBrain/projects/<slug>/MEMORY.md`) and graphify. Interview the user (AskUserQuestion): goal, constraints, out-of-scope, budget (time/tokens), risk tolerance. Push back on vague scope — the user is supposed to argue with the orchestrator.

### 2. Contract — HARD GATE
Write `mission/validation-contract.md` per `references/validation-contract.md`. Present it. **No code, no scaffolding, no file edits until the user approves the contract.** Approval = an explicit AskUserQuestion answer, logged in MISSION.md — never an assumed or self-written approval.

### 3. Plan
Features grouped into milestones. Every feature maps to ≥1 assertion AND every assertion is covered by ≥1 feature — check both sums. Milestones are 2–5 features each — one giant milestone defers validation to the end and defeats the loop. Write `mission/MISSION.md` (template below). User approves the plan (same AskUserQuestion rule) → execution starts.

### 4. Execute — serial workers
ONE worker active at a time. Per feature:
1. Spawn worker (Agent tool, `model: sonnet`) with: the feature spec, its assertions, MISSION.md, and handoffs of dependency features. NOT: other feature specs or your planning reasoning.
2. Worker may parallelize **read-only** ops internally (search, research). Never two writers at once.
3. Worker implements on a feature branch, commits, and writes `mission/handoffs/<feature>.md` per `references/handoff-schema.md`.
4. Read the handoff. Missing handoff or unresolved issues → progress is BLOCKED: re-dispatch or create a corrective feature; do not start the next feature.
5. Update MISSION.md (status, budget, one log line).

### 5. Validate — at every milestone boundary
ALL validator seats are fresh subagents. Scrutiny validators receive the diff + the assertions, nothing else; the user-testing validator receives the running app + the assertions. None of them ever sees worker reasoning, handoffs, or each other's output.
1. **Scrutiny** (parallel — all read-only): test suite, typecheck, lint + `code-reviewer` + `security-reviewer` agents + the cross-provider reviewer per `references/model-seats.md`.
2. **User-testing**: run the live app and exercise this milestone's assertions end-to-end (use the `verify` skill / `e2e-runner` agent).
3. Any failed assertion → corrective feature(s) appended to this milestone, each mapped to the assertion(s) it fixes — corrective features never escape the contract sums. The milestone closes only when all its assertions pass. Expect failures — first-pass validation almost never succeeds; that loop is the value.

### 6. Report
Summary vs contract, budget spent, corrective-feature count. Durable lessons → the project's SecondBrain vault.

## Iron rules

- **No code before the approved contract.** Not "just scaffolding", not "a quick spike".
- **Workers never touch the contract.** A failing assertion is fixed in code; only the USER amends an assertion.
- **No handoff → feature not done.** "The commit message explains it" is not a handoff.
- **Serial means serial.** Two "independent" features still share architecture; one writer at a time.
- **Validators stay blind.** Feeding them worker reasoning re-creates the bias this design exists to remove.
- **Budget cap is a stop rule.** Spent ≥ cap, or any decision only the user can make (contract amendment, scope change) → PAUSE the mission, log it, report to the user. Never burn past the cap or improvise the user's decision to keep moving.
- **Amendments are user-authored.** When the user amends the contract, record their exact decision (confirmed via AskUserQuestion) — never paraphrase a vague comment into a weaker assertion.

## MISSION.md template

```markdown
# Mission: {goal}
Started: {YYYY-MM-DD} · Phase: {scope|contract|plan|execute|validate|done} · Budget: {spent}/{cap}
Contract: mission/validation-contract.md ({N} assertions, approved {date})

## Milestones
- [ ] M1 — {name}: F-001, F-002 · validated: no

## Features
| ID | Feature | Milestone | Assertions | Status | Handoff |
|----|---------|-----------|------------|--------|---------|
| F-001 | {name} | M1 | A-001, A-002 | pending | — |

## Log
- {YYYY-MM-DD HH:MM} {event}
```
