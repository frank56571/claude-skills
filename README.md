# claude-skills

Three Claude Code skills for scaffolding, running, and cross-checking larger projects.

| Skill | Command | What it does |
|-------|---------|--------------|
| **new-project** | `/new-project` | Interviews you, picks a battle-tested framework for the project type, and scaffolds a full repo: real code, passing smoke test, git + branch/PR flow, typed config, and a persistent knowledge layer (Obsidian memory vault + Graphify code graph + optional NotebookLM notebook). Every project also ships a companion (`/next`), a three-lens review barrier (`/verify`), a drift check against `specs/` (`/direction`), Must-Not-Trade-Off rules with a check each, adversarial `breaker` / `first-user` agents, and an opt-in, cost-capped [DeepSec](https://github.com/vercel-labs/deepsec) security layer. Backed by the `project-architect` skill. |
| **mission-control** | `/mission-control` | Runs long, multi-feature work as an orchestrated agent team: contract-first validation, serial workers, adversarial validators, evidence-before-merge. User-invoked only. |
| **codex-loop** | `/codex-loop` | Tandem loop with the OpenAI Codex CLI: Claude plans, Codex implements, Claude reviews the git diff, Codex fixes, then both run a blind adversarial review on the same diff. Git is the contract; max two fix rounds before escalating to you. |

## Layout

This repo mirrors `~/.claude/`, so installing is a copy:

```
commands/   → command entry points (the /slash-commands)
skills/     → the skill bodies the commands read
```

`/new-project` = `commands/new-project.md` + `skills/project-architect/`
`/mission-control` = `commands/mission-control.md` + `skills/mission-control/`
`/codex-loop` = `skills/codex-loop/` (skill only, no command file)

## Install

```sh
git clone https://github.com/frank56571/claude-skills.git
cd claude-skills
cp -R commands/* ~/.claude/commands/
cp -R skills/*   ~/.claude/skills/
```

Restart Claude Code, then type `/new-project` or `/mission-control`.

## Notes

- The knowledge layer assumes a central Obsidian vault at `~/SecondBrain/` and the [Graphify](https://pypi.org/project/graphifyy/) code-graph tool. Both are optional conventions — adapt the paths to your own setup.
- `codex-loop` needs the Codex CLI (`npm i -g @openai/codex`) signed in with a ChatGPT/OpenAI account. Its flags and model names were verified against Codex CLI 0.150.1; the SKILL.md is written in Spanish.
- No secrets or machine-specific absolute paths are baked in.
