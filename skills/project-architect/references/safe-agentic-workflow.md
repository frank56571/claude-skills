# SAFe Agentic Workflow (SAW) — Delivery Layer

**Opt-in.** Layer this on `agent-system`, `single-agent-app`, or any project where multiple agents/devs ship to production and need quality gates. Skip it for solo CLIs, libraries, and throwaway prototypes — the operating-system section of the project `CLAUDE.md` is enough there.

Source: https://github.com/bybren-llc/safe-agentic-workflow — adapts the Scaled Agile Framework so AI agents act as accountable team members with explicit boundaries, evidence-based delivery, and stop-the-line authority. It implements patterns from Anthropic's "Building Effective Agents" / "Effective Harnesses for Long-Running Agents".

## What you actually adopt (two levels)

### Level 1 — the contract (bake into the project's CLAUDE.md, cheap)
Even without vendoring the harness, encode SAW's **workflow contract** so the project's agents follow it.

**Trigger is per-unit-of-work and discretionary** — the agent decides each task whether to gate it. Gate when the change merges to main, has a side effect (send/publish/delete/pay/deploy), or is non-trivial (3+ steps / architectural); skip the ceremony for typos, local refactors, and reversible one-offs. What is NOT discretionary is the independence and merge gates below — those are structural, because an agent self-approving its own work under pressure is the exact failure SAW prevents.

- **Stop-the-Line gate (before any work):** verify acceptance criteria / definition-of-done exists. If missing, STOP and route to whoever owns requirements — never invent requirements.
- **Evidence-based delivery:** work is "done" only with verifiable proof (test output, logs, screenshots), not "trust me". This is the same idea as *Verification Before Done* in the operating system — SAW just makes the evidence an artifact attached to the ticket.
- **Independence is non-negotiable:** the agent that implements is NOT the one that validates. Solo/agent setups satisfy this with a **fresh reviewer subagent** (separate context) or a **human** — never self-review. With a full team, QA and Security are independent roles that may not sign off on their own work; PR-creation (RTE) *can* be collapsed into the implementer for simple PRs, QA and Security cannot.
- **Exit-state chain:** `Implementer → QA → PR/CI → Architecture review → HITL → MERGE`. Each role hands off with an explicit exit state ("Ready for QAS", "Approved", "Ready for HITL review"). Only a human merges.

### Level 2 — vendor the harness (only when the team wants the full thing)
The repo ships a `.claude/` harness: 24 slash commands, 11 SAFe agent profiles, 18 model-invoked skills, and hook-based guardrails.

```bash
git clone https://github.com/bybren-llc/safe-agentic-workflow /tmp/saw
cp -r /tmp/saw/.claude  <project>/.claude          # vendor the harness
# fill the {{PLACEHOLDER}} tokens (TICKET_PREFIX, PROJECT_NAME, AUTHOR_NAME, GITHUB_ORG, MCP server)
bash /tmp/saw/scripts/setup-template.sh            # or edit .claude/SETUP.md by hand
```
Then `/start-work TICKET-123` opens work behind the Stop-the-Line gate; `/pre-pr` validates before a PR; `/end-work` closes the session. Update later with `scripts/sync-claude-harness.sh sync --version <tag>` (manifest-protected, respects local edits).

## The three layers (how SAW enforces the contract)
| Layer | Mechanism | Role |
|-------|-----------|------|
| Hooks | automatic guardrails (format checks, blockers) | catch violations without asking |
| Commands | `/start-work`, `/pre-pr`, `/release`, `/end-work` | user-invoked workflow steps |
| Skills | pattern-discovery, validation, evidence assembly | model-invoked expertise |

## Agent roles (when the project needs a full team)
BSA (requirements) → BE/FE/Data developers (implement) → **QAS (gate owner, routing authority)** → RTE (PR + CI, no merge, no code) → System Architect (pattern/RLS review) → Security Engineer → HITL (human, final merge authority). Each role gets explicit CAN/CANNOT lists — same discipline as `references/guardrails.md` Layer 1.

## How this composes with the rest of the framework
- **`references/guardrails.md`** stays the *runtime* enforcement (approval tiers in orchestrator code). SAW is the *delivery-process* enforcement (who reviews what, in what order). Use both for agent systems.
- **Knowledge layer:** record each role's exit-state decisions and any stop-the-line events as notes in `~/SecondBrain/projects/<slug>/decisions/` so the audit trail is durable, not just in ticket comments.
- **Operating system:** SAW's stop-the-line + evidence gates ARE the "Verification Before Done" and "Plan First" rungs made into team process. Don't duplicate — reference.

## When NOT to use SAW
Solo project, no PR review process, no ticketing, prototype/research, or a library where the only gate is `cargo publish`. Adopting the 11-role team there is pure overhead — keep Level 1 contract ideas (evidence before done) and drop the rest.
