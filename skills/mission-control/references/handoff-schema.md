# Handoff Schema

The worker's LAST act, always. No handoff = feature not done = next feature blocked. This is how context survives agent boundaries and how the mission self-heals: errors get written down at feature boundaries instead of being remembered (badly).

## Template — `mission/handoffs/F-XXX.md`

```markdown
# Handoff — F-XXX {feature name}
Worker finished: {YYYY-MM-DD HH:MM} · Branch: {branch} · Status: completed | partial | blocked

## Completed
- {what actually got done}

## Left undone
- {anything not done — empty ONLY if truly nothing}

## Commands run (with exit codes)
- `pytest -q` → 0
- `npm run typecheck` → 0

## Issues discovered
- {anything smelly, even outside this feature's scope}

## Deviations from spec
- {where implementation differs from the feature spec, and why}

## Files touched
- {paths}

## Assertions
- A-012: test written (tests/test_x.py::test_y), passing locally
```

## Orchestrator duties on receipt

- "Issues discovered" or "Deviations" non-empty → resolve or convert to a corrective feature BEFORE dispatching the next worker. Progress stays blocked until then. (Ownership rule: anything surfaced in a handoff is handled here, at the feature boundary; failed assertions found by validators are handled by the milestone loop. A deviation that touches an assertion's behavior becomes a corrective feature NOW — don't wait for validation to catch it.)
- "Left undone" non-empty with Status=completed → it is `partial`; re-classify and act.
- Commands section missing exit codes → reject the handoff, ask the worker to complete it. Claims without exit codes are not evidence. An "Assertions" claim without a matching command+exit code in the handoff is prose, not proof — reject those too.
