---
name: verify
description: Review {PROJECT_NAME}'s working diff from three independent lenses at once
---

# Verify — {PROJECT_NAME}

A fan-in barrier over the current diff: three reviewers, three lenses, run
concurrently, and nothing is "done" until all three report.

Why this shape — in fanned-out work, one bad node poisons the final answer and
you cannot trace it, because only the finished result surfaces. Separate,
attributable verdicts are the fix.

## Run

1. **Capture the diff.** `git diff main...HEAD`, or `git diff HEAD` for
   uncommitted work. Empty diff → say so and stop. Do not invent findings.

2. **Spawn three agents in a single message** so they actually run at once. Each
   gets the diff and the acceptance criteria — **nothing else**. No build
   reasoning, no conversation history, no "here's what I was going for."

   | Agent | Invokes | Hunts |
   |---|---|---|
   | correctness | `/code-review` | bugs, broken edge cases, bad error handling |
   | reuse & clarity | `/simplify` — **report only, see below** | duplication, wrong altitude, dead ends |
   | over-engineering | `ponytail:ponytail-review` | speculative abstraction, reinvented stdlib, needless deps |

   **`/simplify` applies fixes by default. In this barrier it must not.** Instruct
   that agent to perform the analysis and return findings *without editing any
   file*. Three agents running concurrently means two of them are reading files
   the third would be rewriting — a lens that edits corrupts the other verdicts
   and races on the working tree. Any lens that normally auto-applies runs in
   report-only mode here; applying happens later, in step 4, one change at a time.

   Pin every reviewer to a strong model (`model: "opus"`). This is not the place
   to save tokens: a cheap judge over-reports, and its false findings cost more
   downstream — agents editing code that was never broken — than the review ever
   saved.

3. **Report three separate verdicts**, each finding tagged `file:line`. Never
   merge them into one summary. Attribution is the whole point.

4. **Triage with the user.** A finding is a claim: confirm it against the code
   before acting on it. Reviewers report; they do not edit.

## Rules

- Never review your own work in-context. The agent that built it is the worst
  one to judge it — that is why reviewers start blind.
- Security is NOT in this barrier: run `/security-review` before any commit, as
  its own gate. If the diff touches a critical zone and the project uses DeepSec,
  also run `pnpm deepsec process --diff main` from `.deepsec/`. Remind; don't skip.
- UI projects: add `web-design-guidelines` as a fourth lens. Skip it elsewhere.
