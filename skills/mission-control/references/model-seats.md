# Model Seats

Right model per role — and a different **provider** for at least one reviewer, so validation doesn't share the implementer's training data.

| Seat | Model | Mechanism |
|------|-------|-----------|
| Orchestrator | Session model (Opus/Fable) — slow careful reasoning | Main session |
| Worker | `sonnet` — code fluency, cheap, clean context per feature | Agent tool `model: sonnet` |
| Scrutiny (internal) | `haiku`/`sonnet`, fresh context | `code-reviewer` + `security-reviewer` agents |
| Scrutiny (cross-provider) | GPT/Gemini via external CLI | Bash — see below |
| User-testing | any | `verify` skill / `e2e-runner` agent |

## Cross-provider reviewer — fallback chain

Try in order, use the first CLI that exists (`which <cli>`):

1. **`cursor-agent`** (installed on this machine):
   ```bash
   cd "$(mktemp -d)" && cursor-agent -p "<review prompt with diff inline>" --model gpt-5 --output-format text
   ```
   Run from an empty temp dir with the diff INLINE in the prompt — `-p` mode has write+bash access, so never point it at the repo. Model availability depends on the Cursor subscription (`cursor-agent --help` lists examples).
2. **`codex exec -m gpt-5.6-sol -s workspace-write review --base <branch> "<adversarial instructions>"`** — OpenAI Codex CLI (installed 2026-08-27, v0.150.1). `review` reads the repo diff itself, no need to inline the patch. Always pass `-m`: the configured `gpt-5-codex` is dead for ChatGPT accounts. Options go BEFORE the subcommand. `--full-auto` does not exist.
3. **`gemini -p "<prompt>"`** — Gemini CLI.
4. **Fallback**: Claude `haiku` subagent with fresh context — and record in the MISSION.md log that provider diversity was NOT achieved for this milestone. Never silently fake independence.

A CLI that exists but fails at invocation (auth expired, model unavailable) → fall through to the next link in the chain, same as if absent. A degraded run on a non-frontier model from another provider still counts as provider diversity; the Claude fallback does not.

## Reviewer prompt contents

Give the cross-provider reviewer ONLY:
- the diff (`git diff main...<branch>`)
- the milestone's assertions
- an adversarial instruction: *"Find reasons this diff fails these assertions. Report concrete defects with file:line. Do not summarize, do not praise."*

NEVER include the worker's reasoning, the handoff, or prior validator output — blind review is the point.
