---
name: direction
description: Check whether {PROJECT_NAME} is still heading where specs/ says it should
---

# Direction — {PROJECT_NAME}

Volume (tokens, PRs, features) says how much was built, not where it is going.
This checks the code against the plan in `specs/` and reports drift. It never
edits code or specs — the owner decides each drift item.

## Run

1. **List the plan.** Every file in `specs/` (PRD first). Empty or missing →
   say so and stop; there is nothing to drift from.

2. **One agent per spec doc, in a single message** so they run concurrently.
   Each gets: that one doc + read access to the repo. Nothing from this
   conversation. Each returns, per requirement in its doc:
   `delivered | partial | missing | contradicted` + the `file:line` evidence.
   Pin them to a strong model (`model: "opus"`) — a cheap judge over-reports.

3. **You, in parallel: unplanned work.** From `git log` since the last
   `/direction` (or since the first commit) and `/graphify query`, list features,
   endpoints, screens or dependencies that **no spec asks for**.

4. **Report:**

   ```
   Scorecard
     specs/PRD.md      7/9 delivered · 1 partial · 1 missing
     specs/<doc>.md    …
   Must-Not-Trade-Off  each rule: check passes | fails | no check
   Unplanned work
     - <change> (<file:line>) — adopt into <spec> or revert?
   Actions
     - <numbered, smallest first>
   ```

5. **Stop.** For each unplanned item the owner chooses **adopt** (update the
   spec to match reality) or **revert** (remove the change). Record the
   decision in `~/SecondBrain/projects/{PROJECT_SLUG}/decisions/` and note the
   run date in `## Estado` so the next `/direction` knows where to start.

## Rules

- Report-only. Applying adopt/revert happens afterwards through `/next`.
- A requirement with no evidence is `missing`, never assumed delivered.
- Don't re-litigate the plan here — drift is reported, not judged as good or bad.
