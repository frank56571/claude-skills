# Parallelization — Branches, PRs, and Parallel Work

Every project ships with git branch + PR discipline so work can be split across
parallel sessions without stepping on itself. This file defines the git model,
the **two parallelization modes**, and how to generate the per-instance prompts.

---

## 1. Git & PR model (always applied)

- `git init` on scaffold; `main` is trunk and stays releasable.
- **Never commit to `main` directly.** Every unit of work gets a branch:
  `feat/<slug>`, `fix/<slug>`, `chore/<slug>`, `refactor/<slug>`.
- One branch → one PR. Small, focused, reviewable diffs.
- PR body: what changed, why, test plan, and the acceptance criteria it satisfies.
- A **human merges** (HITL). CI/tests must be green first.
- If the repo has a GitHub remote, PRs go through `gh pr create`. If it's
  local-only, the "PR" is a branch + `git diff main...HEAD` review before a
  fast-forward merge — same discipline, no remote.

This section goes into the generated `CLAUDE.md` (see the Git & Parallelization
block in `templates/claude-md.md`).

---

## 2. Pick a parallelization mode

The `/new-project` interview asks how the owner wants to parallelize. Two modes:

| | **Single instance** | **Multiple instances** |
|---|---|---|
| What | One Claude session using subagents / a Workflow | Several Claude sessions, one per task |
| Isolation | Shared context, in-process | **git worktrees** — one working copy per branch |
| Best for | Tasks that share context, need a coordinator, or fan-out+synthesize | Independent tracks (frontend vs backend, 3 unrelated features) that run for a while |
| Conflict risk | None (one working tree) | Zero if worktrees + clear file ownership; high if same checkout |
| Cost | Cheapest | More disk + you drive N sessions |

Rule of thumb: **shared context or short fan-out → single instance. Long,
independent tracks a human wants to run in separate terminals → multiple
instances with worktrees.** When unsure, default to single instance — it's
cheaper and you can always split out later.

---

## 3. Single instance (workflows / subagents)

No worktrees needed — one working tree, one branch per unit of work.

- Use **subagents** to offload research/exploration/parallel analysis and keep
  the main context clean (already in the CLAUDE.md Operating System).
- Use the **Workflow** tool when the fan-out is structured (N independent
  reviewers, pipeline stages, loop-until-done) — only when the owner opts into
  multi-agent orchestration.
- The main session stays the single writer to the working tree; subagents
  return findings, the main session commits.

No `tasks/parallel-prompts.md` is generated in this mode. Instead, note in
`tasks/todo.md` which steps are subagent-parallelizable.

---

## 4. Multiple instances (git worktrees + prompts)

Each parallel track gets its **own worktree** (a separate checkout on its own
branch, sharing one `.git`). Sessions never share a working tree, so they can't
clobber each other.

Prefer the **`superpowers:using-git-worktrees`** skill if installed. Otherwise,
the native flow (run from repo root):

```bash
# one worktree per task, each on its own branch, as siblings of the repo
git worktree add ../<repo>-wt/<task-slug> -b feat/<task-slug>
# ...repeat per task
git worktree list          # see them all
git worktree remove ../<repo>-wt/<task-slug>   # when merged
```

Worktrees live **outside** the repo (`../<repo>-wt/`) so they never nest inside
the tracked tree. Add `*-wt/` and `.worktrees/` to `.gitignore` as a safety net.

**File ownership is the anti-conflict rule.** When splitting tasks, give each
instance a disjoint set of files/dirs to own. Shared files (schemas, config,
`CLAUDE.md`) are owned by exactly one task or edited only via a follow-up
integration branch — never by two instances at once. State the ownership in
each prompt.

### Generate `tasks/parallel-prompts.md`

Write one file at scaffold time (or when the owner splits a feature) with a
ready-to-paste prompt per task. Each task section carries: the worktree/branch,
the scoped goal, the files it owns, acceptance criteria, and the standing rules
(read memory first, open a PR when done). Template:

```markdown
# Parallel Prompts — <project>

Setup (run once from repo root):
    git worktree add ../<repo>-wt/<slug-a> -b feat/<slug-a>
    git worktree add ../<repo>-wt/<slug-b> -b feat/<slug-b>

Then open a fresh `claude` session inside each worktree dir and paste its prompt.

---

## Task A — <title>   ·   branch `feat/<slug-a>`   ·   worktree `../<repo>-wt/<slug-a>`

```text
You are working on <project> in an isolated git worktree on branch
`feat/<slug-a>`. Do NOT touch `main` or other branches.

First: read `CLAUDE.md`, then `~/SecondBrain/projects/<slug>/MEMORY.md`, then
run `/graphify query "<the area you'll touch>"` before opening files.

Your task: <one-paragraph scoped goal>.
You OWN these files/dirs (edit only inside them): <path>, <path>.
Do NOT edit (owned by another session): <path>, <path>.

Acceptance criteria:
- <criterion 1>
- <criterion 2>
- Smoke test passes: <command>.

When done: commit, push, and open a PR against `main` with `gh pr create`
(or, if local-only, stop at a clean branch + `git diff main...HEAD` summary).
Do not merge — a human merges after review.
```

---

## Task B — <title>   ·   branch `feat/<slug-b>`   ·   worktree `../<repo>-wt/<slug-b>`

```text
<same shape, scoped to Task B, with its own owned files>
```
```

Fill every `<placeholder>` with real values from the project. If the owner also
wants the prompts in chat, print the same content after writing the file.

---

## 5. Checklist

- [ ] `git init`, `main` is trunk, no direct commits to `main`
- [ ] Branch convention + PR flow written into the generated `CLAUDE.md`
- [ ] Interview captured the mode (single instance vs multiple instances)
- [ ] Single instance → subagent/Workflow guidance noted in `tasks/todo.md`
- [ ] Multiple instances → `tasks/parallel-prompts.md` exists with real,
      paste-ready prompts, disjoint file ownership per task, and the worktree
      setup commands
- [ ] `.gitignore` ignores `*-wt/` / `.worktrees/`
