---
name: next
description: Propose, execute and verify the next move on {PROJECT_NAME}
---

# Next — {PROJECT_NAME}

You are the companion for this project across the whole build, not a one-shot
task runner. You orient, recommend with reasoning, wait for a go, build, verify,
and record. **You never start building unasked.**

## 1. Orient (cheapest first — stop when you can name the move)

1. Read `~/SecondBrain/projects/{PROJECT_SLUG}/MEMORY.md` — the *why* + `## Estado`.
2. Read `tasks/todo.md` — the active plan.
3. `git status` — uncommitted work IS the current state. Report it before
   proposing anything new.

On demand only:

- Code-shaped question ("where does X flow", "what breaks if I change Y") →
  `/graphify query "…"`, not grep.
- External contract involved (an API's shape, a spec, a vendor's limits) →
  `notebook_query` against this project's notebook (UUID in
  `~/SecondBrain/projects/{PROJECT_SLUG}/reference/notebook.md`). Cite what it
  says. Never assume an external contract you could have read.

## 2. Rank

1. P0 — blocks deploy.
2. Whatever unblocks the most `todo.md` items. A move that frees three others
   beats one that frees none at equal priority.
3. P1, then P2.

Tie-break toward the move whose acceptance criteria are already written.

No MVP yet? The MVP is the move: the thinnest end-to-end cut of the core
`specs/PRD.md` features, so the idea is seen built before early decisions harden.

## 3. Propose, then STOP

```
Next move (P0 — blocks deploy):
→ <what it is>
   why now:   <the gate or dependency that makes it THE move>
   touches:   <rough surface>
   runner-up: <what> — <why it came second>
```

Then wait for confirmation. This gate is real — do not build through it.

## 4. Design before code (only when the move is big)

Trigger: the move touches 3+ files, or adds an endpoint, a table, or a screen.
Anything smaller goes straight to 5.

Read the code you are about to change first — never design against an imagined
codebase. Then post the sketch in the message. No new file: it dies the moment
the code exists.

```
Design:
  files:      <path — one line on why it lives there>
  signatures: <types + method signatures, NO bodies>
  call stack: <what calls what, top to bottom, main path only>
  tests:      <test names + what each one asserts>
  least sure: <numbered — the calls most worth challenging while changing them is free>
```

Then wait again. Thirty seconds of reading here beats `/verify` catching the same
thing in the diff, where the fix costs a rewrite. Wrong shape? Fix the sketch.

## 5. Execute

Build it, following this project's CLAUDE.md operating system: plan first, tests
first, small files, no stubs, no placeholder TODOs.

Vertical, never horizontal. If the move spans layers, the first cut runs
end-to-end with the middle mocked, then the mocks get replaced — never all of the
schema, then all of the service, then all of the UI, with nothing runnable until
the end. Show each cut actually running, then ask whether to continue or
re-steer.

## 6. Verify

Run `/verify` on the diff before calling the move done. Three separate verdicts,
from agents that never saw your reasoning. Never review your own work yourself.

## 7. Record

- `tasks/todo.md` — check the item off, note what surfaced. Active tracking.
- `~/SecondBrain/projects/{PROJECT_SLUG}/` — durable lessons ONLY: a gotcha, a
  decision + its *why*, a domain term pinned down. One fact per note, pointer
  line in `MEMORY.md`, absolute dates. Nothing durable? Write nothing.
- `## Estado` in `MEMORY.md` — overwrite with what is in flight now. The next
  session reads this first.

## Also worth saying (one line, when true)

A P0 still unchecked while P2 work continues · a `## Estado` that hasn't moved in
several sessions · a `decisions/` note the code now contradicts · a growing god
node in `graphify-out/GRAPH_REPORT.md` · an external dependency assumed instead
of read · several features merged (or a release coming) since the last `/direction` run. Mention it once; don't turn a build session into an audit.
