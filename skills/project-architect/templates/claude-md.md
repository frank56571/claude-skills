# {PROJECT_NAME}

> {ONE_LINE_DESCRIPTION}
> Category: {PROJECT_CATEGORY} · Stack: {LANGUAGE_RUNTIME} · Owner: {OWNER}

---

## ⚡ Operating System — Workflow Orchestration

The default way you work on this project. (Boris Cherny's CLAUDE.md operating system.)

1. **Plan Mode Default** — Enter plan mode for ANY non-trivial task (3+ steps or an architectural decision). Write the spec upfront to reduce ambiguity. If something goes sideways mid-task, STOP and re-plan instead of pushing through. Use plan mode for verification steps too, not just building.
2. **Subagent Strategy** — Use subagents liberally to keep the main context window clean. Offload research, exploration, and parallel analysis to them. One task per subagent for focused execution. Throw more compute at hard problems via subagents.
3. **Self-Improvement Loop** — After ANY correction from the owner, capture the pattern as a lesson in the memory vault (see Knowledge & Memory) and write a rule that prevents the same mistake. Review relevant lessons at session start.
4. **Verification Before Done** — Never mark a task complete without proving it works: run tests, check logs, demonstrate correctness. Diff behavior between main and your change when relevant. Ask: *"Would a staff engineer approve this?"*
5. **Demand Elegance (Balanced)** — For non-trivial changes, pause and ask *"Is there a more elegant way?"* If a fix feels hacky, implement the solution you'd choose knowing everything you know now. Skip this for simple, obvious fixes — don't over-engineer. Challenge your own work before presenting it.
6. **Autonomous Bug Fixing** — Given a bug report, just fix it. Point at the logs, errors, and failing tests, then resolve them. Go fix failing CI without being told how. Zero context-switching required from the owner.

**🟠 Golden Rule:** Be proactive. Think like an owner. Act like a senior engineer. Never make me repeat myself.

---

## ✅ Task Management

**`/next` drives this project.** At the start of a work session, if the owner hasn't named a task, run `/next`: it reads `## Estado` in the vault + `tasks/todo.md` + `git status`, ranks what matters (P0 → whatever unblocks the most items → P1 → P2), and proposes the move with its reasoning. It **waits for confirmation** before building. `/verify` runs the three-lens review barrier on the diff before anything is called done — `/next` invokes it automatically, and the owner can run it standalone on finished work. `/direction` checks the code against `specs/` and reports drift (scorecard + unplanned work) — run it before a release and every few merged features. Volume shipped is not progress; direction is.

1. **Plan First** — Write the plan to `tasks/todo.md` as checkable items before coding.
2. **Verify Plan** — Check in with the owner before starting implementation.
3. **Track Progress** — Mark items complete in `tasks/todo.md` as you go.
4. **Explain Changes** — Give a high-level summary at each step.
5. **Document Results** — Add a review section to `tasks/todo.md` when done.
6. **Capture Lessons** — On any correction, record the lesson in the memory vault (durable, not a throwaway file).
7. **Big builds → missions** — For multi-feature work spanning hours/days, the owner can run `/mission-control`: contract-first validation, serial workers, adversarial validators. Mission state lives in `mission/` (user-invoked only — never start one yourself).

---

## 🧠 Knowledge & Memory — read FIRST, it saves context

Three layers. Hit them *before* grepping, reading many files, or guessing at an external contract — that is the whole point of having them.

- **Memory vault (the *why*)** → central Obsidian second brain at `~/SecondBrain/projects/{PROJECT_SLUG}/`. Read its `MEMORY.md` at the start of work: decisions, domain glossary, ongoing context, gotchas, lessons. When you learn something non-obvious (a decision, a gotcha, a correction), add a one-fact note under `decisions/`, `domain/`, `context/`, or `reference/`, link it with `[[wikilinks]]`, and add a pointer line in `MEMORY.md`. Shared across every session and cwd — memory is never lost.
- **Code graph (the *what connects to what*)** → Graphify. For any "where is X used / how does this flow / what touches Y" question, run `/graphify query "…"` FIRST instead of reading files. Rebuild with `/graphify . --update` after structural changes. `graphify-out/` is gitignored — regenerate on a fresh clone with `/graphify . --obsidian`.

- **Research notebook (what the *external source* says)** → NotebookLM. API contracts, specs, vendor limits, docs and videos this project depends on but did not write. Notebook UUID is in `~/SecondBrain/projects/{PROJECT_SLUG}/reference/notebook.md`. Query it with `notebook_query` **before** designing against an external contract, and cite what it returns. New doc or spec comes up mid-build → `source_add` it instead of skimming it again next week.

Rule of thumb: **code/architecture question → graphify query first. "Why / what's the plan / what does this term mean" → read the vault first. "What does the source actually say" → query the notebook, don't guess.**

---

## 🔌 Skill Discovery (don't over-do it)

Before hand-rolling a capability that is probably common (testing, deploy, design, changelog, PR review, animations), check whether a skill already exists: run `npx skills find <query>` or use the **find-skills** skill, then install with `npx skills add <owner/repo@skill> -g -y`. Only reach for this when a capability is *clearly missing* — do not interrupt routine work to shop for skills.

---

## 🌿 Git & Parallelization

- **`main` is trunk and stays releasable.** Never commit to `main` directly.
- One unit of work → one branch (`feat/`, `fix/`, `chore/`, `refactor/<slug>`) → one focused PR. PR body = what/why + test plan + acceptance criteria. **A human merges** after CI/tests are green.
- **Splitting work across sessions?**
  - *Single instance* — stay in one session; use subagents / the Workflow tool for fan-out. One writer to the working tree.
  - *Multiple instances* — one **git worktree** per task so sessions can't clobber each other: `git worktree add ../{PROJECT_SLUG}-wt/<slug> -b feat/<slug>`, open a fresh `claude` there. Startup prompts live in `tasks/parallel-prompts.md`. Give each instance a **disjoint set of files to own**; shared files (schemas, config, this file) belong to exactly one task at a time.
- `*-wt/` and `.worktrees/` are gitignored.

---

<!-- ───── INCLUDE ONLY when Q10 = orchestrated. Delete this whole section otherwise. ───── -->
## 🎛️ Orchestrated Mode

- Board tools (`create_task`, `claim_task`, `get_task_status`, …) come from `.mcp.json` (`coordination/board_server.py`); state lives in `coordination/` (regenerated, gitignored).
- Terminal 1 runs `/orchestrate` (plans, reviews handoffs, closes tasks — never writes code); workers run `/worker` in their own worktrees.
- **Never edit files outside your claimed task's `file_scope`** — the board rejects overlap; raise a flag if you need a file you don't own.
- Full mechanics + iron rules: `.claude/commands/orchestrate.md` and `worker.md`.
<!-- ───── end orchestrated section ───── -->

<!-- ───── INCLUDE ONLY for agent/team projects with staged delivery (Step 1 Q9 = yes). Delete this whole section otherwise. ───── -->
## 🚦 Delivery Workflow — SAW Level-1 Contract

**Apply per unit of work, at your discretion — not on every message.** Gate a change when it **merges to main**, has a **side effect** (send/publish/delete/pay/deploy), or is **non-trivial** (3+ steps / architectural). Skip the ceremony for typos, local refactors, and reversible one-offs — that judgment call is yours to make each task.

When a change IS gated:
- **Stop-the-Line gate:** before starting, confirm acceptance criteria / definition-of-done exists. If missing, STOP and route to the owner — never invent requirements.
- **Independent verification:** the agent that implements does NOT validate its own work. "Independent" = a **fresh reviewer subagent** (separate context) or a **human** — never self-review. Self-approving your own output is not a gate.
- **Evidence before done:** "done" only with verifiable proof (tests, logs, screenshots), not "trust me".
- **Exit-state chain:** Implementer → independent review → PR/CI → HITL → MERGE. Only a human merges.
<!-- ───── end optional SAW section ───── -->

## Build & Run
- {INSTALL_COMMAND}            <!-- e.g. uv sync · npm install · go mod download -->
- `cp .env.example .env` and fill in real values
- {RUN_COMMAND}                <!-- e.g. uv run -m src.main · npm run dev · go run ./cmd -->

## Test
- {TEST_COMMAND}               <!-- e.g. pytest · npm test · go test ./... -->
- Run the smoke test before claiming anything works (Verification Before Done).

## Architecture
- {ARCHITECTURE_SUMMARY — 3–6 bullets: entry point, module boundaries, data flow}
- Config is externalized ({CONFIG_FORMAT}), never hardcoded.
- Data crossing module boundaries is validated by schema ({SCHEMA_TOOL}).

## Critical Rules
- NEVER commit secrets — everything sensitive lives in `.env` (`.env.example` lists every var).
- NEVER publish / send / delete / pay / deploy without explicit owner approval.
- Validate all external input at the boundary; never trust API responses or user input.
- Immutable data by default — return new objects, never mutate.
- Many small files over few large ones (200–400 lines typical, 800 hard max).
- {CATEGORY_SPECIFIC_RULE}

## 🚫 Must-Not-Trade-Off
What this project never gives up, whatever the deadline. Every rule names its check — a rule with no check is a wish.
- {RULE} — checked by `{TEST_PATH_OR_COMMAND}`

**Critical zones** (full `/verify` + tests on every change; slop is not accepted here): {CRITICAL_ZONES — e.g. auth, payments, user data}. Outside them, speed is allowed. Run `/security-review` after finishing each feature, not only before deploy.
<!-- INCLUDE ONLY when Q13 = deepsec. --> Deeper scan: `cd .deepsec && pnpm deepsec process --diff main` on every change to a critical zone (exit 1 = new finding → triage before merge). Every DeepSec run is cost-capped; `.deepsec/data/` and findings are never committed.

<!-- ───── INCLUDE ONLY the agents this project shipped. ───── -->
**Adversaries:** `breaker` agent tries to break the app on an isolated data copy — every confirmed break becomes a regression test. `first-user` agent uses the app through the browser only, as a newcomer. Journey suite (`tests/e2e/`, results in `tests/e2e/journeys.json`) runs before every ship.

## Gotchas
- {Add gotchas as they are discovered — and mirror durable ones into the memory vault}
