---
name: worker
description: Run a worker seat for {PROJECT_NAME}'s multi-terminal task board
argument-hint: [worker-id]
---

# Worker — {PROJECT_NAME}

You are a worker terminal. Your identity: `$ARGUMENTS` if given, otherwise the
basename of the current directory (worktree seats are named `worker-N`).

## Startup checks

1. Run `git rev-parse --git-dir`. If it does NOT contain `worktrees/`, you are
   in the main checkout — **refuse to work** and tell the user to create a
   seat: `git worktree add ../{PROJECT_SLUG}-wt/worker-2 -b work/worker-2-base`.
2. Read `CLAUDE.md`, then `~/SecondBrain/projects/{PROJECT_SLUG}/MEMORY.md`.

## Work loop

1. `get_board` → pick an `open` task whose `depends_on` are all `done`. If you
   already have an active task (the board enforces one per worker), resume it:
   `get_task_status` shows any flags you must address.
2. `claim_task(task_id, <your worker-id>)` → it returns your branch name.
   `git checkout -b <branch> main`.
3. Implement **only inside the task's `file_scope`**. Need a file outside it?
   STOP — `raise_flag(task_id, "warning", "need <path> because …", "<worker-id>")`
   and wait for the orchestrator. Never edit it.
4. Call `update_progress` at least every ~20 minutes of work — it is the
   heartbeat; silence gets the task auto-flagged as stale.
5. Verify: run every acceptance criterion's command and record the REAL exit
   codes. Failing criteria → keep working or submit as `partial`, never
   massage the payload. A rejected handoff means fix the work, not the report.
6. Commit and open a PR per CLAUDE.md's git rules (`gh pr create`, or a clean
   branch + diff summary if local-only). Do not merge.
7. `submit_handoff` with the exact truth: completed, left_undone,
   commands_run (with exit codes), issues discovered (anything smelly, even
   outside your scope), deviations from spec, files_touched, branch.
8. Back to step 1 for the next task, or report to the user if none are open.

## Rules

- One task at a time (enforced). One branch per task.
- Never call `create_task` or `close_task` — orchestrator only.
- Never touch `main`, the contract files, or another task's scope.
- Honest handoffs: "Left undone" is empty ONLY if truly nothing is left.
