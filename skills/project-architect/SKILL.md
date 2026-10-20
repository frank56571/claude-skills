---
name: project-architect
description: Architecture patterns, guardrails, schemas, and scaffolding for new projects of any kind — agent systems, APIs, web apps, CLIs, libraries, pipelines, prototypes. Activates when creating new projects, designing systems, or scaffolding infrastructure. Use when the user says "new project", "scaffold", "set up", or invokes /new-project.
disable-model-invocation: true
user-invocable: false
---

# Project Architect

You are scaffolding a new project using a curated, battle-tested framework. The framework adapts to the project category — it is not tied to any specific company or domain. This skill contains the architectural standards, templates, and patterns to apply.

## How to Use This Skill

Based on the project category supplied by `/new-project` (or inferred from the user's request), read the relevant reference files. Skip what doesn't apply — the framework is modular.

### For ALL projects (mandatory, every category):
- `references/folder-structure.md` — standard directory layout (adapt to language)
- `references/checklist.md` — pre-deploy checklist (P0/P1/P2)
- `references/knowledge-layer.md` — **ALWAYS apply.** The three knowledge layers: central Obsidian second brain (`~/SecondBrain/projects/<slug>/`) for authored memory, Graphify code graph (`graphify-out/`, repo-local) for code structure, and a NotebookLM research notebook for external source material. Required regardless of project category (the notebook alone is skippable).
- `references/companion.md` — **ALWAYS apply.** The loop the project runs *after* scaffolding: orient → rank → propose → confirm → design → execute → verify → record. Generates `.claude/commands/next.md`. Also defines the RESUME/retrofit semantics for re-running `/new-project` in an existing project.
- `references/graph-verification.md` — **ALWAYS apply.** Task-graph (fan-out) shapes and the verification barrier that keeps a bad node traceable. Carries the judge-model rule. Generates `.claude/commands/verify.md`. **Not** about the Graphify code graph — the file opens by disambiguating the two.
- `references/parallelization.md` — **ALWAYS apply.** Git branch/PR model + the two parallel modes (single instance with subagents/Workflow, or multiple instances with git worktrees) and the per-instance prompt format. Every project ships branch + PR discipline.
- `references/shipping-discipline.md` — **ALWAYS apply.** `specs/PRD.md` + MVP-first, the `/direction` drift check, Must-Not-Trade-Off rules with a check each, critical zones, and the adversaries (`breaker` for stateful/multi-user apps, `first-user` + journey suite for UIs). From an interview with Vercel's CEO.
- `templates/claude-md.md` — **ALWAYS use as the CLAUDE.md base.** It carries the Workflow-Orchestration operating system (plan-mode-default, subagent strategy, self-improvement loop, verification-before-done, demand-elegance, autonomous bug-fixing, golden rule) + Task-Management loop. Tailor the placeholders; keep the operating-system and Knowledge & Memory sections intact.

### For agent-based projects (`agent-system`, `single-agent-app`):
- `references/guardrails.md` — 4-layer guardrail system (runtime enforcement)
- `references/safe-agentic-workflow.md` — SAW delivery layer (stop-the-line gate, independent QA/Security, evidence-based delivery, exit-state chain). Apply the Level-1 contract by default for team/agent projects; vendor the full harness only when the team wants it.
- `references/schemas.md` — inter-agent data contracts
- `references/orchestrator.md` — orchestrator patterns
- `references/memory-rehydration.md` — memory and rehydration

### For orchestrated parallelization (any category, Q10 = `orchestrated`):
- `references/orchestration.md` — multi-terminal agent team on a self-generated MCP task board: orchestrator terminal with coordination tools (`create_task`, `get_task_status`, `claim_task`, …), workers in worktrees, deterministic anti-overlap enforced by the board server, hybrid sentinel red-flag screening. Generated from `templates/coordination/`.

### For services / apps / pipelines (`api-service`, `web-app`, `data-pipeline`):
- `references/folder-structure.md` — layout, plus framework conventions
- `references/checklist.md` — pre-deploy checklist
- Apply schema/guardrail references only where boundaries warrant them

### For CLIs / libraries / prototypes (`cli-tool`, `library-sdk`, `research-prototype`):
- `references/folder-structure.md` and `references/checklist.md` are usually sufficient
- Skip orchestrator/agent references entirely

### Templates (copy and adapt to the project's language/runtime):
- `templates/claude-md.md` — CLAUDE.md starter for new projects
- `templates/orchestrator.py` — orchestrator skeleton (agent systems only)
- `templates/client-config.json` — per-tenant / per-client config template (multi-tenant systems only)
- `templates/docker-compose.yml` — base Docker setup (when local services are needed)
- `templates/gitignore` — generic .gitignore; adapt to the chosen language
- `templates/commands/{next,verify,direction}.md` — → project `.claude/commands/`. The companion loop, the verification barrier, and the drift check. **Every category**, fill `{PROJECT_NAME}`/`{PROJECT_SLUG}`.
- `templates/agents/breaker.md` — → `.claude/agents/`. Stateful / multi-user categories (`api-service`, `web-app`, `agent-system`, `single-agent-app`, `data-pipeline`).
- `templates/agents/first-user.md` — → `.claude/agents/`. UI-bearing projects only; fill `{BROWSER_TOOLS}` with the browser MCP tools this project uses (comma-separated full names) — never add Read/Grep/Bash/Edit.
- `templates/coordination/` — orchestrated-mode task board: `board_logic.py` + `board_server.py` + `test_board_server.py` (copied verbatim into the project's `coordination/`), `mcp.json` (→ project `.mcp.json`), `commands/{orchestrate,worker}.md` (→ `.claude/commands/`), `agents/{sentinel,task-planner}.md` (→ `.claude/agents/`). Only when Q10 = `orchestrated`.

### Examples:
- `examples/bookkeeping-agent/` — agent-system reference (PARSER/SCRIBE architecture). Use as inspiration, not as a hard template — adapt to the actual project category.

## Core Principles
1. Config separated from logic — business rules in JSON/YAML/TOML or env, never hardcoded in prompts or source
2. Schemas validated at every boundary — Pydantic, zod, JSON Schema, or the language's equivalent. No loose dicts crossing module lines.
3. Idempotent actions — re-running never duplicates effects
4. Business-context logging — log WHY decisions were made and which entity they affect, not just HTTP status
5. Progressive approval gates — auto / notify / require tiers in code, not just prompts (only for systems with side effects)
6. Edge cases go to a parking lot — uncertain items queued for review, never force a decision
7. Prompts and public APIs are versioned — changelog with date + change + reason; never silently edit `v1`
8. Use battle-tested skeletons when they exist (`create-next-app`, `uv init`, `cargo new`, etc.) and layer the framework on top — don't reinvent foundational tooling
9. Every project ships a knowledge layer — authored memory in the **central** Obsidian second brain (`~/SecondBrain/projects/<slug>/`) for the *why*, a repo-local Graphify code graph (`graphify-out/`) for the *what connects to what*, and a NotebookLM notebook for what **external** sources say. See `references/knowledge-layer.md`. Non-negotiable for all categories (the notebook alone may be skipped).
10. Every project's `CLAUDE.md` is built from `templates/claude-md.md` so it ships the Workflow-Orchestration operating system + Task-Management loop. The generated CLAUDE.md must point the agent at the Obsidian vault + graphify FIRST (fast recall, less context) before grepping.
11. Discover, don't reinvent — the generated CLAUDE.md tells the project's agent to check `find-skills` / `npx skills find` before hand-rolling a common capability, but only when a capability is clearly missing (don't over-do it on routine work).
12. Parallel-ready by default — every project gets `git init` + branch/PR discipline (`main` stays clean, one branch → one PR, human merges) so work can be split across sessions. The `/new-project` interview asks the parallel mode: **single instance** (subagents / Workflow) or **multiple instances** (git worktrees, one per task). For multiple instances, generate `tasks/parallel-prompts.md` with paste-ready per-session prompts and disjoint file ownership. See `references/parallelization.md`.
13. Scaffolding is hour zero, not the deliverable — every project ships a **companion** (`.claude/commands/next.md`) that ranks the next move from P0/P1/P2 + `todo.md`, proposes it with its reasoning, **waits for confirmation**, sketches the design before writing code when the move is big (3+ files, or a new endpoint/table/screen — signatures with no bodies, call stack, test plan, and the decisions it is least sure about), builds it vertically, verifies it, and records the durable lesson to the vault. Re-running `/new-project` in a scaffolded project is a RESUME, never a fresh interview. See `references/companion.md`.
14. The node that judges never runs cheap — every project ships a verification barrier (`.claude/commands/verify.md`) that reviews the diff from three lenses concurrently, with reviewers pinned to a strong model and started **blind** (diff + acceptance criteria, never the build conversation). Verdicts are reported separately, never merged, so a bad node stays traceable. A cheap judge over-reports, and downstream agents then burn tokens "fixing" what was never broken. See `references/graph-verification.md`.
15. Measure direction, not volume — building is the cheap part. Every project ships `specs/PRD.md`, starts with an MVP, runs `/direction` against the specs, and lists its Must-Not-Trade-Off rules each with a committed check. Apps with users ship their adversaries: `breaker` (on an isolated data copy) and, with a UI, `first-user` (browser-only). See `references/shipping-discipline.md`.
