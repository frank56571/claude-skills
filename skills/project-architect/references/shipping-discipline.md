# Shipping Discipline — direction, trade-offs, adversarial testing

Source: AI LABS, *"Vercel's CEO Just Unveiled The Greatest AI Coding Workflow Ever"*
(2026-10-19), seven tips from an interview with Vercel's CEO. Sponsor segment
omitted. This file turns the tips into what `/new-project` ships.

The thread through all seven: **with agents, building is the cheap part.**
Tokens spent and changes shipped measure *how much* you build, not *where it is
going*. An agent builds whatever it is asked and has no idea which features
matter. The scaffold has to carry the plan, the non-negotiables, and the
adversaries that the agent will not supply by itself.

| # | Tip | What ships | When |
|---|-----|-----------|------|
| 1 | Validate before committing | `specs/PRD.md` + MVP-first rule | every category |
| 2 | Measure direction, not volume | `.claude/commands/direction.md` | every category |
| 3 | Security + slop debt | critical zones in CLAUDE.md, `/security-review` after each feature, DeepSec opt-in (§3a) | every category |
| 4 | Decide what you won't trade off | `## 🚫 Must-Not-Trade-Off` in CLAUDE.md, one check per rule | every category |
| 5 | Try to break it on purpose | `.claude/agents/breaker.md` | stateful / multi-user (api-service, web-app, agent-system, single-agent-app, data-pipeline) |
| 6 | See it as a first-time user | `.claude/agents/first-user.md` + journey suite | anything with a UI |
| 7 | Act fast on customer feedback | P2 checklist item, not scaffolded | once real users exist |

## 1. Validate before committing

- Every project starts with `specs/PRD.md`: the problem, the target user, and the
  **main features** as a numbered list with acceptance criteria. Written from the
  interview, not invented — a feature the owner didn't name doesn't go in.
- The companion's first move is an **MVP**: the thinnest version that exercises
  the core features end-to-end, so the idea is seen built before the early
  decisions harden. If the MVP shows the idea isn't worth it, drop it cheaply.
  Building the whole app from the PRD discovers a bad premise last, under
  everything built on top of it.
- Don't go off vibes. A claim about a model, prompt style, library or vendor
  ("model X does better with prompt Y") gets checked in a throwaway sandbox by
  an agent starting from scratch before the project depends on it. Record the
  result in the vault (`decisions/`), not the claim.

## 2. `/direction` — drift check against the plan

Template: `templates/commands/direction.md`. Reads every doc in `specs/`, one
blind subagent per doc checks whether the code delivers it; the main agent
separately lists **changes no spec asked for**. Output: a scorecard per spec +
an unplanned-work list. For each drift item the owner chooses: **adopt** (update
the spec to match) or **revert** (remove the change). `/direction` never edits
code or specs itself.

The companion proposes `/direction` before a release and every few merged
features — not every session.

## 3. Security debt and slop debt

- **Security debt** grows with agent-written volume, and attackers have agents
  too: models are cheap and good at finding holes. Run `/security-review` after
  finishing each feature, not only before deploy. Free, local, always on.
- **DeepSec** (opt-in, Interview Q13) is the deeper layer. See §3a.
- **Slop debt** = messy code you accept to move fast. Fine at the edges, not at
  the core. CLAUDE.md marks the **critical zones** (auth, payments, user data,
  anything money/fiscal) — those get the full `/verify` barrier and tests on
  every change. Outside them, speed is allowed.
- Tests say *it works*; a quality gate says *it's good enough*. `/verify` is the
  gate — nothing in a critical zone merges until it passes.

## 3a. DeepSec — agent-powered vulnerability scanner (opt-in)

Verified 2026-10-20 against the official repo `github.com/vercel-labs/deepsec`
(Apache-2.0, npm `deepsec` 2.3.10, site deepsec.sh). Re-check the README before
relying on any flag below; the CLI moves fast.

What it is: `scan` (regex matchers, free) → `process` (an AI agent investigates
each candidate, emits findings) → optional `revalidate` (cuts false positives).
`process --diff <ref>` reviews only the changed files and exits `1` when it
produces a **net-new** finding, so it works as a per-feature or CI gate.

Why it's opt-in, not default:
- **Cost.** It runs top models at max thinking; upstream warns full scans can
  cost thousands of USD on large repos. Every run gets a cap:
  `npx deepsec init --max-cost-usd <N> --max-duration <T>`. Never run it uncapped.
- **Code leaves the machine.** Source goes to the model provider. Use
  `--model-auth direct` with the project's own Anthropic/OpenAI key
  (`--ai-provider`, `--ai-api-key-env <VAR_NAME>` — DeepSec stores only the env
  var *name*, never the key). Vercel AI Gateway is the default route; pick it
  only if the owner already uses Vercel. Projects whose code must not reach a
  third party skip DeepSec entirely.
- **It is a coding agent with full shell access** (upstream's own security
  model). Run it only on trusted source, never on a checkout of an unreviewed
  third-party PR, and never on a machine that holds production secrets or real
  client data. Vercel Sandbox mode limits exposure but needs a Vercel account.

How it plugs in:
- **Not at hour zero** — there's nothing to scan yet. The first real feature
  merge triggers the setup offer via `/next`.
- Setup: `npx deepsec init --model-auth direct --ai-provider anthropic
  --ai-api-key-env DEEPSEC_ANTHROPIC_API_KEY --max-cost-usd 20 --max-duration 30m`
  (adjust the cap with the owner). Adds only `.deepsec/`. Gitignore its state:
  `.deepsec/data/` holds absolute paths and raw findings, and exported findings
  are an exploit list — **never commit them, above all in a public repo.**
- Per feature touching a critical zone: `cd .deepsec && pnpm deepsec process
  --diff main` after `/security-review`. Exit `1` → triage before merge.
- Before a release: `pnpm deepsec scan && pnpm deepsec process && pnpm deepsec
  revalidate`, then `pnpm deepsec export --format md-dir --out ./findings`.
- Findings are claims, like `/verify`'s: confirm each against the code, fix
  through `/next`, add a regression test, then `revalidate`.

## 4. Must-not-trade-off rules

Every build trades speed against safety, features against time, polish against
cost. The agent can't spend unlimited effort, so it picks — and if it doesn't
know what you won't give up, it picks for you. Interview Q12 collects the
non-negotiables (correctness of X, latency under N ms, data never leaving Y).

Each rule in CLAUDE.md carries **how it's checked** — a committed test path or
a command. Prose rules get forgotten as context grows; a test in git can't be
skipped. A rule with no check is a wish: either write the check or drop it.

## 5. Breaker agent

Template: `templates/agents/breaker.md`. The agent that built a feature tests it
the way it was built to be used, so everything passes. Real users skip steps,
double-submit, race each other and hit it at load. The breaker attacks the app
in its own context: concurrent conflicting operations, skipped/reordered steps,
bad input, latency under load. Report-only, each break with a repro.

- Runs **only against an isolated copy** — temp DB copy, fixtures, local
  stack. It refuses if the target points at staging, production, or real client
  data.
- Each confirmed break → a regression test, fixed through `/next`, breaker
  re-run. Loop until a run finds nothing new.

## 6. First-time user + journeys (error-free sessions)

Template: `templates/agents/first-user.md`. You can never be a first-time user
of your own app. This agent can only drive a browser — its `tools:` allowlist
holds browser tools only, no Read/Grep/Edit/Bash — so it cannot learn the app
from the code. The parent starts the app and hands over the URL. It reports
where a newcomer gets stuck, confused, or lost.

Separately, the metric Vercel's CEO tracks is **error-free sessions**: how many
users get through without anything going wrong. The proxy here is a journey
suite — one e2e test per path every customer must complete (sign-up, core
action, checkout…), run via the global `e2e-runner` agent, results written to
`tests/e2e/journeys.json` (pass/fail + duration per step). Run it before every
ship; slow steps are findings too.

## 7. Feedback loop (post-launch)

The company-level measure of agent use: when a customer reports a problem, how
long until a real reply, a diagnosis, and — if it's a clear bug — a fix. Once
real users exist, connect the feedback sources via MCP (Sentry for errors no one
reported, the support inbox) and triage:

- **Clear breakage** (screenshot of a broken button, failing payment) → fix
  fast through `/next` + `/verify`. Production changes still need owner approval.
- **Needs judgment** ("I'm confused by…") → escalate to the owner; that's a
  conversation with the customer, not a prompt.

Track time-to-resolution. Not scaffolded at hour zero — there are no customers
yet; it lives in the P2 checklist.
