---
name: new-project
description: Scaffold a new project with a curated framework — agent architecture, guardrails, schemas, orchestrator, configs, or whatever the project type requires. Use when starting any new product, client system, agent-based project, web app, CLI, library, or service.
argument-hint: [project-name]
---

# New Project Scaffold

You are scaffolding a new project using a curated, battle-tested framework. The framework adapts to project type — it is not tied to any specific company or domain. Follow these steps IN ORDER:

## Step 1: Interview (USE AskUserQuestion TOOL)

Ask the user these questions. Adapt follow-ups based on earlier answers. Do NOT skip the core ones (1–4).

1. **Project name and one-line description** — what does this system do and who is it for?
2. **Project category** — pick one:
   - `agent-system` (multi-agent orchestrator with handoffs, e.g. Hive-style)
   - `single-agent-app` (one agent + tools, e.g. chatbot, copilot, automation)
   - `api-service` (REST/GraphQL backend, no agents required)
   - `web-app` (Next.js / React frontend, optionally with backend)
   - `cli-tool` (command-line utility or developer tool)
   - `library-sdk` (reusable package: npm, PyPI, crates.io, etc.)
   - `data-pipeline` (ETL, batch jobs, scheduled workers)
   - `research-prototype` (exploration / notebook-first)
   - `other` (describe)
3. **Primary language and runtime** — Python, TypeScript, Go, Rust, etc. + framework if relevant (FastAPI, Next.js, etc.)
4. **Owner / client / target user** — internal team, specific client, open-source, end-user product?
5. **Integrations** — which external APIs or services? (databases, LLMs, queues, OAuth providers, payment, email, Slack, etc.) — only if relevant to the category
6. **Agents needed** (only if `agent-system` or `single-agent-app`) — how many, what does each one do, and what are their CAN/CANNOT rules?
7. **Approval / safety gates** — what actions require human approval or special guardrails before executing? (e.g. publishing, payments, destructive ops). Only ask if the category implies side effects.
8. **Deployment target** — local-only, Docker, serverless, Vercel, Fly, AWS, on-prem? (affects compose/config scaffolding)
9. **Delivery workflow** (only if `agent-system` / `single-agent-app` or a multi-dev/production project) — does this need staged quality gates (stop-the-line AC check, independent QA/Security review, evidence-before-merge, HITL merge)? If yes, layer the SAFe Agentic Workflow (SAW). Skip for solo CLIs, libraries, and prototypes.
10. **Parallelization strategy** — how do you want to split future work? (git branches + PR flow are set up either way.)
    - `single-instance` — one Claude session using subagents / the Workflow tool (shared context, cheapest; good for fan-out+synthesize)
    - `multiple-instances` — several Claude sessions in parallel, one per task, each in its own **git worktree**; I generate paste-ready startup prompts (`tasks/parallel-prompts.md`)
    - `decide-later` — set up branches/PRs now, choose the parallel mode when work actually needs splitting
    See `references/parallelization.md` for the mechanics. (Separate from this choice: for long multi-feature builds after scaffolding, the user can run `/mission-control` — an orchestrated execution mode with contract-first validation. The generated CLAUDE.md mentions it; do not set it up here.)

## Step 2: Load the Skill

Read the `project-architect` skill. Based on the project category from Step 1, read the relevant files from `references/` and `templates/`. If the category is outside what the skill covers, fall back to the universal pieces (folder-structure, checklist, gitignore, claude-md template) and adapt.

ALWAYS read, regardless of category:
- `references/knowledge-layer.md` — the mandatory Obsidian memory vault + Graphify code graph every project ships.
- `references/parallelization.md` — the git branch/PR model + single-instance vs multiple-instances (worktrees) modes and the per-instance prompt format.
- `templates/claude-md.md` — the CLAUDE.md base carrying the Workflow-Orchestration operating system + Task-Management loop.

If the project needs staged delivery gates (Step 1 Q9 = yes), also read `references/safe-agentic-workflow.md` and apply at least its Level-1 contract.

## Step 3: Generate

Create the full project structure tailored to the category. Always include:

- Folder structure with all directories the category requires
- `CLAUDE.md` built from `templates/claude-md.md` (<200 lines) — keep the **Operating System** (Workflow Orchestration), **Task Management**, **Knowledge & Memory** (Obsidian vault + graphify, listed FIRST for fast recall), and **Skill Discovery** (find-skills, don't over-do it) sections intact; fill the placeholders with this project's mission, stack, architecture, and category-specific rules
- `tasks/todo.md` — empty task-tracker stub (the operating system writes plans here: checkable items + a review section). Keep this repo-local; durable lessons/decisions go to the Obsidian vault, not here
- **Git & parallelization (mandatory, see `references/parallelization.md`)**:
  - `git init`; `main` is trunk and never receives direct commits. Add `*-wt/` and `.worktrees/` to `.gitignore`.
  - Write the branch convention (`feat/`, `fix/`, `chore/`, `refactor/`) + one-branch-one-PR + human-merges flow into the generated `CLAUDE.md` (Git & Parallelization section).
  - Interview Q10 = `multiple-instances` → generate `tasks/parallel-prompts.md` with real, paste-ready startup prompts (one per task/branch/worktree, each with disjoint file ownership + acceptance criteria + "open a PR when done") and the `git worktree add …` setup commands.
  - Q10 = `single-instance` → no parallel-prompts file; note in `tasks/todo.md` which steps are subagent/Workflow-parallelizable.
  - Q10 = `decide-later` → set up git + branch/PR flow only; skip the prompt file until work is split.
- `README.md` with one-paragraph pitch + run instructions
- `.gitignore` appropriate to the language/runtime
- Test directory scaffolded with the language's standard runner (pytest, vitest, go test, etc.) and at least one passing smoke test
- Config strategy — environment via `.env.example` + a typed config loader (pydantic-settings, zod, envalid, etc.) — never hardcode
- **Knowledge layer (mandatory, see `references/knowledge-layer.md`)**:
  - **Central Second Brain** — the project's authored memory lives in the shared vault at `~/SecondBrain/projects/<project-slug>/`, NOT inside the repo. Create that folder with a `MEMORY.md` index + `decisions/`, `domain/`, `context/`, `reference/` subfolders, seed it with a first ADR capturing the stack/category choices from Step 1 (the *why*), and add a pointer line under "## Proyectos" in `~/SecondBrain/HOME.md`. This is the single source of memory across all sessions and cwds.
  - Graphify code graph + Obsidian vault — after the initial files exist, run `/graphify . --obsidian` to generate `graphify-out/` (graph.json, graph.html, GRAPH_REPORT.md, and a browsable `obsidian/` vault of the codebase) **inside the repo** (code map is repo-local, regenerated, gitignored). Add `graphify-out/` and Obsidian's `.obsidian/workspace*` to `.gitignore`. Refresh later with `/graphify . --update`. (Graphify is installed globally; if missing, `uv tool install graphifyy && graphify install`.)

Add when the category calls for it:

- **Agent systems / single-agent apps**: orchestrator skeleton, Pydantic (or zod) schemas for inter-agent contracts, `prompts/<agent>/v1/` directory with `CHANGELOG.md`, approval-gate hooks, client/config template JSON. If Step 1 Q9 = yes, also encode the SAW Level-1 contract in CLAUDE.md (stop-the-line AC gate, independent QA/Security, evidence-before-merge, exit-state chain) per `references/safe-agentic-workflow.md`; vendor the full `.claude/` SAW harness only if the team explicitly wants it
- **API service / web app**: route/handler structure, request/response schemas, middleware skeleton, OpenAPI or types
- **CLI tool**: entry point, command parser, help text, example invocation
- **Library/SDK**: public API surface, build config, publish config (do NOT publish), example consumer
- **Data pipeline**: job runner, schedule definition, idempotency keys, observability hooks
- **Docker / deploy**: `docker-compose.yml` for local services if the project needs a DB/queue/cache; deployment notes appropriate to the target

## Step 4: Verify

- `CLAUDE.md` is under 200 lines and project-specific (no boilerplate from another domain)
- `CLAUDE.md` keeps the Operating System (Workflow Orchestration), Task Management, Knowledge & Memory (vault + graphify FIRST), and Skill Discovery sections — placeholders all filled, none left as `{TOKENS}`
- `tasks/todo.md` exists as the repo-local plan/review tracker
- Git initialized, `main` is trunk, and the generated `CLAUDE.md` carries the branch convention + one-branch-one-PR + human-merges flow; `.gitignore` ignores `*-wt/` / `.worktrees/`
- If Q10 = `multiple-instances`, `tasks/parallel-prompts.md` exists with real paste-ready prompts (disjoint file ownership per task) + worktree setup commands — no `<placeholders>` left
- If staged delivery was requested, the SAW Level-1 contract is present in CLAUDE.md (stop-the-line, independent QA/Security, evidence-before-merge, HITL merge)
- All inter-module contracts have schema validation at boundaries
- Approval / safety gates exist for every side-effect action the user named in Step 1
- No credentials hardcoded — `.env.example` lists every required variable
- Smoke test runs and passes (`pytest`, `npm test`, `go test ./...`, etc.)
- `~/SecondBrain/projects/<slug>/` exists with a populated `MEMORY.md` index and at least one seeded note (the initial-stack ADR), and `~/SecondBrain/HOME.md` has a pointer line for the project
- `graphify-out/` was generated via `/graphify . --obsidian` and is gitignored; the project `CLAUDE.md` points the agent at both `~/SecondBrain/projects/<slug>/MEMORY.md` and graphify
- List what the user needs to do next: which env vars to fill, which API keys to obtain, which command runs the first end-to-end check

## Rules

- NEVER generate placeholder/stub code with `TODO` comments — generate real, functional code or omit the file entirely
- All code uses the language's strict mode (type hints + mypy strict for Python, `strict: true` for TS, `go vet` clean for Go)
- All config is externalized — JSON / YAML / TOML files or env vars — never hardcoded in prompts or source
- For agent systems: every agent has explicit CAN / CANNOT rules in its system prompt
- Logging includes business context (who, what entity, why) — not just technical errors
- Immutable data by default — return new objects, never mutate
- Many small files over few large files — 200–400 lines typical, 800 hard max
- If the project category has battle-tested skeletons available (e.g. `create-next-app`, `cargo new --lib`, `uv init`), use them as the foundation and layer the framework on top rather than reinventing
- ALWAYS ship the knowledge layer — every project, every category, no exceptions: authored memory in the central `~/SecondBrain/projects/<slug>/` vault (the *why*, shared across sessions) + Graphify `graphify-out/` repo-local (the *what connects to what*). It is what makes memory and context efficient across sessions.
