# Graph Verification — task graphs and the node that judges them

## First: which "graph" this is about

Two unrelated things in this framework share the word. Never conflate them.

| Term | Means | Lives in |
|---|---|---|
| **code graph** | Graphify's knowledge graph of the codebase — functions, classes, god nodes | `graphify-out/`, see `knowledge-layer.md` |
| **task graph** | work fanned out to parallel agents instead of one linear loop | the `Workflow` tool, or parallel `Agent` calls |

This file is about **task graphs**. A code-graph question (`/graphify query "…"`) has nothing to do with it.

## Loop vs task graph

A **loop** is linear: do a piece of work, verify it, move on. Every step waits on the previous one even when the two have nothing to do with each other.

A **task graph** splits the work and gives each part its own agent. It buys two things: wall-clock (parts run at once) and per-node model choice (the cheap parts stop burning the expensive model).

**Cost warning, stated up front, not buried:** a task graph burns far more tokens than the same work in a loop. Fan-out is **opt-in per task**, never the default shape. On metered API pricing, don't fan out at all. On a subscription, expect limits sooner than usual.

## The flaw

> One error in a small node disturbs the entire output, and it is hard to trace because all you get at the end is the finished result.

This is the failure mode that matters. A linear loop fails visibly at the step that broke. A graph launders the failure through a synthesizer, so you receive one confident answer with a bad fact buried inside it and no signal about which node produced it.

Everything below exists to make that traceable.

## The two shapes

- **Diamond** — fan out to sub-agents, then narrow back into one agent that pulls everything into a single answer.
- **Fan-in at a barrier** — the same problem goes to several agents, each looking through a different lens, and nothing moves forward until all of them report.

These are not new machinery. `Workflow`'s `pipeline()` is the diamond and `parallel()` is the barrier. And **a single barrier does not need `Workflow` at all** — several `Agent` calls in one message *is* a barrier. Reach for `Workflow` when the graph has more than one stage; otherwise parallel `Agent` calls are the whole implementation.

## Rules for the judging node

**1. The judge never runs on a cheap model.**

Measured, from the source this file is based on: the same review on a small model returned a long list of issues; on a frontier model, far fewer. The small model's extra findings were mostly things that had been left there **on purpose**.

In a loop you read that list and discard the noise. In a graph, downstream agents *act* on it — burning tokens editing code that was never broken, and introducing real defects into working code. Saving tokens on a judge is negative value. Pin reviewer/judge nodes to a strong model; only mechanical nodes (rename, reformat, mirror an existing pattern) may drop a tier.

**2. Reviewers get the diff, never the build conversation.**

The agent that built the thing is the worst one to review it — it will defend its own choices and it already believes the code is correct. Reviewers must start with no build context: pass `git diff` plus the acceptance criteria, and nothing else. Subagents are fresh by construction, so this holds as long as you don't paste your reasoning in. (`claude -p` is the CLI equivalent.) `references/orchestration.md` already applies exactly this rule to handoff review — *"validators stay blind: diff + acceptance criteria only."*

**3. Verdicts stay separate.**

Each reviewer returns findings tagged `file:line`, and the barrier reports **per-reviewer verdicts — never one merged blob**. Merging is what destroyed traceability in the first place. Three verdicts you can attribute beat one summary you have to trust.

**4. A finding is a claim until it is checked.**

Reviewers report; they do not edit. Act on a finding only after confirming it against the code — a confident review is still just one node's output.

**5. No node in a barrier writes to the working tree.**

This is a mechanical constraint, not a preference. Concurrent nodes read the same files; if one of them edits, the others are reviewing a tree that is shifting underneath them and their verdicts become garbage. Note that some review skills **auto-apply by default** — `/simplify` is one — so a barrier must explicitly put them in report-only mode. Fixes get applied afterward, serially, one confirmed finding at a time. (The alternative is `isolation: 'worktree'` per node, which is real but costs setup and disk per agent — for a review barrier, report-only is the cheaper correct answer.)

## The barrier this framework ships

Three lenses, run concurrently, on the diff:

| Lens | Skill | Hunts |
|---|---|---|
| Correctness | `/code-review` | bugs, broken edge cases, bad error handling |
| Reuse & clarity | `/simplify` | duplication, wrong altitude, dead ends |
| Over-engineering | `ponytail:ponytail-review` | speculative abstraction, reinvented stdlib, needless deps |

Generated per project as `.claude/commands/verify.md`. Two ways to run it, and they are different tools:

- **standalone** — the user invokes `/verify` for a deep pass on finished work.
- **embedded** — `/next` calls it automatically before reporting a move complete.

Deliberately **not** in this barrier: security review and design review. Security has its own mandatory gate before any commit (`~/.claude/rules/common/security.md`) and is not weakened by being separate. Design review only applies to projects with a UI — add `web-design-guidelines` as a fourth lens there and skip it everywhere else.
