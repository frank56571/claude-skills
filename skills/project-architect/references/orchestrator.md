# Orchestrator Patterns

The orchestrator is YOUR code that controls the LLM. It is NOT the LLM itself.

## Core Loop
```python
async def run():
    while tasks := await get_pending_tasks():
        for task in tasks:
            context = build_context(task)
            response = await call_claude(context)
            actions = parse_actions(response)

            for action in actions:
                if requires_approval(action):
                    await queue_for_approval(action)
                elif validate_action(action):
                    result = await execute_action(action)
                    await log_action(action, result)
                else:
                    await log_error(action, "validation_failed")
                    await escalate_to_human(action)
```

## Responsibilities
1. **Task routing** — decides which agent handles each task
2. **Context assembly** — builds prompt with memory + instructions + relevant data only
3. **Execution** — invokes Claude Code or API
4. **Response parsing** — extracts structured actions from LLM response
5. **Action execution** — executes actions (API calls, DB writes)
6. **Error handling** — retry with exponential backoff, fallback, human escalation
7. **Logging** — records everything with business context

## Idempotency Pattern
```python
async def process_idempotent(task_id: str, payload: dict):
    existing = await db.query("SELECT * FROM action_log WHERE task_id = ? AND status = 'completed'", task_id)
    if existing:
        return existing.result  # Already done, skip

    action_id = generate_uuid()
    try:
        result = await execute(payload)
        await db.insert("action_log", {"action_id": action_id, "task_id": task_id, "status": "completed", "result": result})
        return result
    except Exception as e:
        await db.insert("action_log", {"action_id": action_id, "task_id": task_id, "status": "failed", "error": str(e)})
        raise
```

## Circuit Breaker for External APIs
```python
class CircuitBreaker:
    def __init__(self, failure_threshold=3, recovery_timeout=300):
        self.failures = 0
        self.threshold = failure_threshold
        self.timeout = recovery_timeout
        self.last_failure = None
        self.state = "closed"

    async def call(self, func, *args):
        if self.state == "open":
            if time.time() - self.last_failure > self.timeout:
                self.state = "half_open"
            else:
                raise CircuitBreakerOpen(f"API blocked for {self.timeout}s")
        try:
            result = await func(*args)
            self.failures = 0
            self.state = "closed"
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure = time.time()
            if self.failures >= self.threshold:
                self.state = "open"
                await notify_admin(f"Circuit breaker OPEN: {func.__name__}")
            raise
```

## Timeouts
- External APIs (QB, Supabase): 10-15 seconds
- Claude API calls: 60 seconds max
- Total agent process: configurable hard timeout per client
