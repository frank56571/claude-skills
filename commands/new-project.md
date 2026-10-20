---
name: new-project
description: Scaffold a new project with a curated framework — agent architecture, guardrails, schemas, orchestrator, configs, or whatever the project type requires. Use when starting any new product, client system, agent-based project, web app, CLI, library, or service.
argument-hint: [project-name]
---

# New Project Scaffold

You are scaffolding a new project using a curated, battle-tested framework, and then acting as its companion for the rest of the build. The framework adapts to project type — it is not tied to any specific company or domain. Follow these steps IN ORDER.

## Step 0: Is this actually new? (RUN THIS FIRST — do not skip to the interview)

Scaffolding is hour zero, not the whole job. Before interviewing anyone, find out whether this project already exists. Derive the slug from the current directory name (kebab-case); if that misses, match against the pointer lines under `## Proyectos` in `~/SecondBrain/HOME.md`.

| State | What you do |
|-------|-------------|
| cwd has `CLAUDE.md` **and** `~/SecondBrain/projects/<slug>/MEMORY.md` exists **and** `.claude/commands/next.md` exists | **RESUME.** Do NOT interview. Read the vault `MEMORY.md` (especially `## Estado`), `tasks/todo.md`, and `git status`. Report where the project stands, then hand off to `/next`. Never re-plan from scratch. |
| Scaffolded, but **no `.claude/commands/next.md`** | **RETROFIT** — scaffolded before the companion existed. Ask first, then generate ONLY: `.claude/commands/{next,verify}.md`, the research notebook + its `reference/notebook.md` pointer, and a `## Estado` block in the existing `MEMORY.md`. Touch nothing else — no folder restructuring, no CLAUDE.md rewrite, no overwriting existing notes. |
| Neither | **NEW.** Continue to Step 1. |

On RESUME, if the project lacks `.claude/commands/direction.md` (scaffolded before 2026-10-20), say so once and offer to add only `direction.md`, a `specs/PRD.md` reconstructed from the vault + code (owner confirms it), the Must-Not-Trade-Off section, and the adversaries the category calls for. Ask first; touch nothing else.

This mirrors the semantics the task board already uses (`references/orchestration.md`: *"Board has tasks → this is a RESUME … Never re-plan from scratch."*). See `references/companion.md`.

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
    - `orchestrated` — multi-terminal agent team on a **self-generated MCP task board**: terminal 1 = orchestrator (`/orchestrate`, owns the board via `create_task`/`get_task_status`/`close_task` tools), terminals 2..N = workers (`/worker`) in git worktrees claiming tasks whose disjoint file scopes are **enforced by the board tool itself**; a `sentinel` agent screens every handoff for red flags. Generates `coordination/` (board server + smoke test), `.mcp.json`, project commands, and `sentinel`/`task-planner` agents. Requires `uv`. See `references/orchestration.md`
    - `decide-later` — set up branches/PRs now, choose the parallel mode when work actually needs splitting
    See `references/parallelization.md` for the mechanics. (Separate from this choice: for long multi-feature builds after scaffolding, the user can run `/mission-control` — an orchestrated execution mode with contract-first validation. The generated CLAUDE.md mentions it; do not set it up here.)
11. **Reference material to seed the research notebook** (optional — offer it, accept "none") — any API docs, specs, videos, PDFs, or competitor pages this project depends on but did not write? These get ingested once into a NotebookLM notebook and become queryable for the whole build instead of re-skimmed every session. See `references/knowledge-layer.md` Part 3. This layer writes to an external service, so it is **confirm-first and skippable** — if the user declines or the MCP server is unavailable, skip it and continue; the scaffold does not depend on it.
12. **Must-not-trade-offs** — what will this project never give up, whatever the deadline? (e.g. payroll totals exact to the cent, p95 < 300 ms, client data never leaves the tenant). And which parts are **critical zones** (auth, payments, user data) where speed never beats quality? Each answer becomes a CLAUDE.md rule with a check. See `references/shipping-discipline.md` §4.
13. **Security scanning depth** — `/security-review` after every feature is always on. Add **DeepSec** (Vercel's agent-powered scanner) on top? It costs real money per run, sends source to a model provider, and runs as an agent with shell access. Options: `deepsec` (own Anthropic/OpenAI key via `--model-auth direct`, cost-capped) · `none`. Default to `none` when the code must not reach a third party. See `references/shipping-discipline.md` §3a. **Confirm-first**, like the notebook.

## Step 2: Load the Skill

Read the `project-architect` skill. Based on the project category from Step 1, read the relevant files from `references/` and `templates/`. If the category is outside what the skill covers, fall back to the universal pieces (folder-structure, checklist, gitignore, claude-md template) and adapt.

ALWAYS read, regardless of category:
- `references/knowledge-layer.md` — the three knowledge layers every project ships: Obsidian memory vault, Graphify code graph, NotebookLM research notebook.
- `references/companion.md` — the post-scaffold loop (orient → rank → propose → confirm → design → execute → verify → record) and the RESUME/retrofit semantics from Step 0.
- `references/graph-verification.md` — task-graph fan-out shapes, the verification barrier, and the judge-model rule. Read it before generating `verify.md`; note it is **not** about the Graphify code graph.
- `references/parallelization.md` — the git branch/PR model + single-instance vs multiple-instances (worktrees) modes and the per-instance prompt format.
- `references/shipping-discipline.md` — `specs/PRD.md` + MVP-first, `/direction` drift check, Must-Not-Trade-Off rules, critical zones, and the `breaker` / `first-user` adversaries.
- `templates/claude-md.md` — the CLAUDE.md base carrying the Workflow-Orchestration operating system + Task-Management loop.
- `templates/commands/{next,verify,direction}.md` — the companion, verification barrier, and drift check that ship into every project's `.claude/commands/`.

If the project needs staged delivery gates (Step 1 Q9 = yes), also read `references/safe-agentic-workflow.md` and apply at least its Level-1 contract.

If Q10 = `orchestrated`, also read `references/orchestration.md` and the `templates/coordination/` tree before generating.

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
  - Q10 = `orchestrated` → generate the coordination layer per `references/orchestration.md`: copy `templates/coordination/{board_logic.py,board_server.py,test_board_server.py}` into `coordination/`, `templates/coordination/mcp.json` → `.mcp.json` at repo root (merge if one exists), `commands/{orchestrate,worker}.md` → `.claude/commands/`, `agents/{sentinel,task-planner}.md` → `.claude/agents/` (fill `{PROJECT_NAME}`/`{PROJECT_SLUG}` placeholders in the commands/agents; the `.py` files are copied verbatim); append the board-state block to `.gitignore`; include the Orchestrated Mode block in CLAUDE.md. Do NOT generate `tasks/parallel-prompts.md` — the board replaces it.
  - Q10 = `decide-later` → set up git + branch/PR flow only; skip the prompt file until work is split.
- **Plan + non-negotiables (mandatory, see `references/shipping-discipline.md`)**:
  - `specs/PRD.md` — problem, target user, main features as a numbered list with acceptance criteria, built from the interview only. Seed `tasks/todo.md` with the MVP (thinnest end-to-end cut of the core features) as the first item.
  - CLAUDE.md `## 🚫 Must-Not-Trade-Off` from Q12 — each rule with the test path or command that checks it, and generate that check now (a passing test in `tests/`); a rule you can't check yet goes in `tasks/todo.md` as P0, not in CLAUDE.md as prose. Fill the critical zones line.
  - **Security (Q13)** — always: critical zones line + `/security-review` after each feature in CLAUDE.md. If Q13 = `deepsec`: include the DeepSec line in CLAUDE.md, the `.deepsec/` entries from `templates/gitignore`, `DEEPSEC_ANTHROPIC_API_KEY` (or the OpenAI equivalent) in `.env.example`, and a P1 item in `tasks/todo.md`: *"Set up DeepSec after the first real feature, capped"* with the exact `init` command from §3a. Do NOT run `deepsec init` during scaffolding — nothing to scan yet, and it spends money.
  - **Adversaries** → `.claude/agents/`: `breaker.md` from `templates/agents/breaker.md` for `api-service`, `web-app`, `agent-system`, `single-agent-app`, `data-pipeline`; `first-user.md` from `templates/agents/first-user.md` for anything with a UI, with `{BROWSER_TOOLS}` set to this project's browser MCP tools (browser tools only). UI projects also get `tests/e2e/` for the journey suite (results → `tests/e2e/journeys.json`). Skip both for `cli-tool`, `library-sdk`, `research-prototype` and drop the Adversaries line from CLAUDE.md.
- `README.md` with one-paragraph pitch + run instructions
- `.gitignore` appropriate to the language/runtime
- Test directory scaffolded with the language's standard runner (pytest, vitest, go test, etc.) and at least one passing smoke test
- Config strategy — environment via `.env.example` + a typed config loader (pydantic-settings, zod, envalid, etc.) — never hardcode
- **Knowledge layer (mandatory, see `references/knowledge-layer.md`)**:
  - **Central Second Brain** — the project's authored memory lives in the shared vault at `~/SecondBrain/projects/<project-slug>/`, NOT inside the repo. Create that folder with a `MEMORY.md` index + `decisions/`, `domain/`, `context/`, `reference/` subfolders, seed it with a first ADR capturing the stack/category choices from Step 1 (the *why*), and add a pointer line under "## Proyectos" in `~/SecondBrain/HOME.md`. This is the single source of memory across all sessions and cwds.
  - `MEMORY.md` must carry a **`## Estado`** block — what is currently in flight. Seed it with "scaffolded `<absolute date>`, nothing in flight yet". This is the first thing `/next` reads every session.
  - Graphify code graph + Obsidian vault — after the initial files exist, run `/graphify . --obsidian` to generate `graphify-out/` (graph.json, graph.html, GRAPH_REPORT.md, and a browsable `obsidian/` vault of the codebase) **inside the repo** (code map is repo-local, regenerated, gitignored). Add `graphify-out/` and Obsidian's `.obsidian/workspace*` to `.gitignore`. Refresh later with `/graphify . --update`. (Graphify is installed globally; if missing, `uv tool install graphifyy && graphify install`.)
  - **Research notebook** — `notebook_create` titled with the project name, `source_add` for each reference from Q11, and write the UUID to `~/SecondBrain/projects/<slug>/reference/notebook.md` with a pointer line in `MEMORY.md`. **Confirm before creating** (it writes to an external service) and skip the whole layer if the user declines or the `notebooklm-mcp` server is unavailable — note the skip in `reference/notebook.md` and move on. Never ingest anything the user did not point at.
- **Companion + verification (mandatory, every category — see `references/companion.md` and `references/graph-verification.md`)**:
  - `.claude/commands/next.md` from `templates/commands/next.md` — the companion loop. Fill `{PROJECT_NAME}` / `{PROJECT_SLUG}`.
  - `.claude/commands/verify.md` from `templates/commands/verify.md` — the three-lens verification barrier (`/code-review` + `/simplify` + `ponytail:ponytail-review`), reviewers pinned to a strong model and started blind on the diff. For UI-bearing categories (`web-app`, or any project with a frontend), add `web-design-guidelines` as a fourth lens; omit it everywhere else.
  - `.claude/commands/direction.md` from `templates/commands/direction.md` — drift check of the code against `specs/`. Fill `{PROJECT_NAME}` / `{PROJECT_SLUG}`.
  - Tell the user in the handoff that `/next` is how they drive the build from here — it proposes and waits, it does not build unasked.

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
- If Q10 = `orchestrated`: `uv run --script coordination/test_board_server.py` exits 0; `.mcp.json` parses and points at `coordination/board_server.py`; `/orchestrate` + `/worker` commands and `sentinel` + `task-planner` agents exist with no `{PLACEHOLDER}` tokens; `coordination/board.json`, `board.json.bak`, `handoffs/`, `DASHBOARD.md`, `.board.lock` are gitignored while the three `.py` files and `.mcp.json` are tracked
- If staged delivery was requested, the SAW Level-1 contract is present in CLAUDE.md (stop-the-line, independent QA/Security, evidence-before-merge, HITL merge)
- All inter-module contracts have schema validation at boundaries
- Approval / safety gates exist for every side-effect action the user named in Step 1
- No credentials hardcoded — `.env.example` lists every required variable
- Smoke test runs and passes (`pytest`, `npm test`, `go test ./...`, etc.)
- `~/SecondBrain/projects/<slug>/` exists with a populated `MEMORY.md` index and at least one seeded note (the initial-stack ADR), and `~/SecondBrain/HOME.md` has a pointer line for the project
- `MEMORY.md` contains a `## Estado` block with an absolute date
- `graphify-out/` was generated via `/graphify . --obsidian` and is gitignored; the project `CLAUDE.md` points the agent at both `~/SecondBrain/projects/<slug>/MEMORY.md` and graphify
- `.claude/commands/{next,verify,direction}.md` all exist with **zero `{PLACEHOLDER}` tokens left**
- `specs/PRD.md` exists with numbered features + acceptance criteria; `tasks/todo.md` starts with the MVP
- Every Must-Not-Trade-Off rule in CLAUDE.md names a check, and that check runs and passes
- If Q13 = `deepsec`: `.deepsec/data/` and findings are gitignored, the key's env var NAME is in `.env.example` (no value), and the capped setup is in `tasks/todo.md` — `deepsec init` was not run
- `breaker.md` / `first-user.md` exist exactly where the category calls for them; `first-user.md` `tools:` lists browser tools only
- `reference/notebook.md` exists in the vault holding either a real notebook UUID or an explicit note that the layer was skipped — never left half-written
- Re-running `/new-project` here now takes the Step 0 RESUME path instead of re-interviewing. Confirm this, it is the behavior the scaffold previously lacked
- List what the user needs to do next: which env vars to fill, which API keys to obtain, which command runs the first end-to-end check — and that `/next` drives the build from here

## Rules

- NEVER generate placeholder/stub code with `TODO` comments — generate real, functional code or omit the file entirely
- All code uses the language's strict mode (type hints + mypy strict for Python, `strict: true` for TS, `go vet` clean for Go)
- All config is externalized — JSON / YAML / TOML files or env vars — never hardcoded in prompts or source
- For agent systems: every agent has explicit CAN / CANNOT rules in its system prompt
- Logging includes business context (who, what entity, why) — not just technical errors
- Immutable data by default — return new objects, never mutate
- Many small files over few large files — 200–400 lines typical, 800 hard max
- If the project category has battle-tested skeletons available (e.g. `create-next-app`, `cargo new --lib`, `uv init`), use them as the foundation and layer the framework on top rather than reinventing
- ALWAYS ship the knowledge layer — every project, every category, no exceptions: authored memory in the central `~/SecondBrain/projects/<slug>/` vault (the *why*, shared across sessions) + Graphify `graphify-out/` repo-local (the *what connects to what*) + a NotebookLM notebook for what external sources say. It is what makes memory and context efficient across sessions. The notebook is the only skippable piece, because it writes to an external service.
- ALWAYS ship the companion — `.claude/commands/{next,verify}.md` in every project, every category. Scaffolding is hour zero; the companion is what carries the build. `/next` proposes and waits for confirmation, it never builds unasked.
- Measure direction, not volume — the PRD, `/direction`, and the Must-Not-Trade-Off checks ship in every project. Never hand the agent a rule without a way to check it.
- Security scanners spend money and see code: DeepSec is opt-in, every run is cost-capped, never runs on unreviewed third-party code or on a machine with production secrets, and its findings are never committed.
- Adversaries attack isolated copies only — `breaker` never touches staging, production, or real client data; `first-user` never sees the code.
- NEVER run a reviewer or judging node on a cheap model, and never let it see the build conversation. A cheap judge over-reports and downstream agents burn tokens "fixing" what was never broken; an author reviewing itself defends its own choices. Diff + acceptance criteria only, verdicts reported separately.
