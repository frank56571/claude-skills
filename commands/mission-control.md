---
name: mission-control
description: Run a mission — long, multi-feature work executed by an orchestrated agent team (contract-first validation, serial workers, adversarial validators). User-invoked only.
argument-hint: [goal — omit to resume the mission in the current project]
---

Read `~/.claude/skills/mission-control/SKILL.md` and follow it exactly, including its `references/` when each phase calls for them.

- `$ARGUMENTS` given → new mission with that goal, starting at Phase 1 (Scope).
- No arguments and `mission/MISSION.md` exists in the current project → RESUME that mission.
- No arguments and no existing mission → ask the user for the goal.
