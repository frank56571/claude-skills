# Companion Loop — the project after scaffolding

Scaffolding is hour zero. This file governs every session after it. The generated `.claude/commands/next.md` implements this loop, and `/new-project`'s Step 0 hands off to it.

## No new state store

The companion reads state that already exists. Do not invent a status file.

| Source | Holds | When |
|---|---|---|
| `~/SecondBrain/projects/<slug>/MEMORY.md` | the *why* + `## Estado` (what is in flight) | always |
| `tasks/todo.md` | the active plan — checkable items + review section | always |
| `references/checklist.md` P0/P1/P2 | what "ready" means, by horizon | the ranking source |
| `/graphify query "…"` | what connects to what | code-shaped questions only |
| `notebook_query` | what the external source actually says | external contracts only |

Read in that order and stop as soon as you can name the next move. Rows 4–5 are on-demand: "what's next" almost never needs them; "how does auth reach the DB" needs row 4; "what does the webhook contract require" needs row 5.

The design sketch from step 4 is not state and gets no file. It lives in the message, and in `tasks/todo.md` only if the build will span sessions. Once the code exists the sketch is worthless — the code says it better. If a *decision* inside it turns out to outlive the feature, that goes to the vault as one note, not the whole sketch.

## The loop

**1. Orient.** Read `MEMORY.md` `## Estado` and `tasks/todo.md`, then `git status`. If there is uncommitted work, *that* is the state — report it before proposing anything new.

**2. Rank.** Candidate moves, in this order:

1. **P0 items** — blocks deploy.
2. **Whatever unblocks the most `todo.md` items.** A move that frees three others beats a move that frees none, even at equal priority.
3. P1, then P2.

Tie-break toward the move whose acceptance criteria are already written.

**3. Propose — then stop.** Present the top move with what it is, **why now** (the dependency or gate that makes it the move, not a restatement of the item), the runner-up and what makes it second, and roughly what it touches. Then **wait**. The companion does not build unasked. This is a hard gate, not a formality.

**4. Design — only when the move is big.** Trigger: 3+ files, or a new endpoint, table, or screen. Below that, skip straight to execute. Read the code being changed, then post a sketch: file locations, types and method signatures **with no bodies**, the call stack of the main path, the test names and what each asserts, and a numbered list of the decisions taken with least confidence. Then wait again.

The point is the asymmetry: a wrong signature costs a sentence here and a rewrite once the code exists. `/verify` catches the same class of mistake, but only on the finished diff — too late to be cheap. The least-confident list is what makes it work: it aims the human's attention at the calls that actually deserve it, which no diff review can do on its own.

**5. Execute.** On confirmation, build it, following the project's own CLAUDE.md operating system — it already carries plan-first, tests-first, small files, and verification-before-done.

Vertical, never horizontal. A move that spans layers gets cut end-to-end with the middle mocked first, then the mocks get replaced one at a time. Never all of the schema, then all of the service, then all of the UI, with nothing runnable until the end — that shape hides every integration mistake until the diff is too big to re-steer. Show each cut running before starting the next.

**6. Verify.** Run the barrier (`/verify`, see `graph-verification.md`) before claiming the move is done: three separate verdicts, on the diff, from agents with no build context.

**7. Record.** Split by durability — the rule `knowledge-layer.md` already sets:

- `tasks/todo.md` → check the item off, note what surfaced. Active tracking.
- `~/SecondBrain/projects/<slug>/` → the durable lesson **only**: a gotcha, a decision and its *why*, a domain term that got pinned down. One fact per note, pointer line in `MEMORY.md`, absolute dates.
- `## Estado` in `MEMORY.md` → overwrite with what is in flight now. This is what the next session reads first.

Nothing durable surfaced? Write nothing. An empty vault beats a note that restates the diff.

## Recommending, not just executing

"What's next" is the common case, but the companion is also the thing that *notices*. Volunteer these when true — briefly, once, without derailing the move:

- a P0 checklist item still unchecked while work continues on P2 things
- a `## Estado` entry that has not moved in several sessions
- a note in `decisions/` that the code has since contradicted
- a god node in `graphify-out/GRAPH_REPORT.md` that keeps growing (the report already computes this)
- an external dependency that was assumed rather than read → add it to the notebook and query it

Say it in a line. Do not turn a build session into an audit.

## Re-entry

`/new-project` in an already-scaffolded directory is a **RESUME**, never a fresh interview — the same semantics the task board already uses (`references/orchestration.md`: *"Board has tasks → this is a RESUME … Never re-plan from scratch."*). Report state, then hand off to `/next`.

A project scaffolded before the companion existed has no `.claude/commands/next.md`. That is a **retrofit**, not a rebuild: generate the two commands, the notebook, and the vault `## Estado` block. Touch nothing else.
