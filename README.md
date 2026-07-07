# claude-skills

Two Claude Code skills for scaffolding and running larger projects.

| Skill | Command | What it does |
|-------|---------|--------------|
| **new-project** | `/new-project` | Interviews you, picks a battle-tested framework for the project type, and scaffolds a full repo: real code, passing smoke test, git + branch/PR flow, typed config, and a persistent knowledge layer (Obsidian memory vault + Graphify code graph). Backed by the `project-architect` skill. |
| **mission-control** | `/mission-control` | Runs long, multi-feature work as an orchestrated agent team: contract-first validation, serial workers, adversarial validators, evidence-before-merge. User-invoked only. |

## Layout

This repo mirrors `~/.claude/`, so installing is a copy:

```
commands/   → command entry points (the /slash-commands)
skills/     → the skill bodies the commands read
```

`/new-project` = `commands/new-project.md` + `skills/project-architect/`
`/mission-control` = `commands/mission-control.md` + `skills/mission-control/`

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
- No secrets or machine-specific absolute paths are baked in.
