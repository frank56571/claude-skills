# Guardrails — 4-Layer System

## Layer 1: System Prompt (Declarative Restrictions)
Every agent MUST have explicit CAN/CANNOT lists:
```markdown
# What this agent CAN do:
- [list specific allowed actions]

# What this agent CANNOT do:
- [list specific prohibited actions]
- Publish/send/delete anything without explicit owner approval
- Modify account configurations
- Access systems outside its scope

# Golden rule: When in doubt, STOP and REPORT.
```

## Layer 2: Approval Gates (Orchestrator Code)
Classify every action into tiers. This goes in `src/orchestrator/approvals.py`:
```python
ACTION_TIERS = {
    "auto_execute": ["read_data", "categorize", "log_action", "draft_entry"],
    "notify_then_execute": ["update_mapping", "create_draft"],
    "require_approval": ["publish", "delete", "send_email", "modify_account", "payment"]
}
```
CRITICAL: This is code logic, not just prompt instructions. The orchestrator enforces it.

## Layer 3: Rate Limiting & Scope
- Max actions per cycle (configurable per client)
- Max token spend per session (budget cap)
- Hard timeout: kill process after X minutes
- File system scope: agent only touches authorized directories
- Use `/permissions` with wildcards, never `--dangerously-skip-permissions`

## Layer 4: Output Validation
Before executing ANY external action, validate with schema:
```python
from pydantic import BaseModel, ValidationError

def safe_execute(action_payload: dict, schema_class: type[BaseModel]):
    try:
        validated = schema_class(**action_payload)
    except ValidationError as e:
        log_error(action_payload, f"Schema validation failed: {e}")
        queue_for_review(action_payload)
        return None
    return execute(validated)
```

## Gotchas
- Prompt-only guardrails are NOT sufficient — Claude can hallucinate past them
- Always validate at the orchestrator level, never trust LLM output blindly
- Log every blocked action with reason — helps debug false positives
