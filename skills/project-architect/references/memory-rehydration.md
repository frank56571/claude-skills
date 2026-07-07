# Memory & Rehydration

Claude has no memory between invocations. You build it.

## Short-Term Memory (Session Context)
Inject at the start of each execution:
```json
{
  "last_action": "What was the last thing completed",
  "pending_tasks": ["List of tasks still in queue"],
  "errors_recent": ["Recent errors and how they were resolved"],
  "current_context": "What the agent is currently working on"
}
```
Keep under 2000 tokens. Only what's relevant to the current task.

## Long-Term Memory (Persistent)
Database tables:
- `action_log` — every action with input, output, reasoning, status
- `workflow_runs` — multi-step workflow state with current_step and checkpoint_data
- `client_state` — per-client config, last sync, known exceptions
- `parking_lot` — uncertain items queued for human review

## Rehydration Startup Sequence
```
1. Load client config from DB/file
2. Query pending tasks from task queue
3. Query last 10 actions from action_log
4. Check workflow_runs for interrupted workflows
5. Build context summary (< 2000 tokens)
6. Inject into system prompt
7. Resume from correct step
```

## Multi-Step Workflow Recovery
```sql
CREATE TABLE workflow_runs (
    id TEXT PRIMARY KEY,
    workflow_type TEXT NOT NULL,
    client_id TEXT NOT NULL,
    current_step INTEGER NOT NULL DEFAULT 1,
    total_steps INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',  -- pending, in_progress, completed, failed
    checkpoint_data JSONB,                    -- state needed to resume
    started_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```
On restart: find `status = 'in_progress'`, read `current_step` and `checkpoint_data`, resume.

## Rules
- Never inject full memory — filter to what's relevant
- Context window is too valuable to waste on history
- Log reasoning, not just results — "categorized as X BECAUSE Y"
