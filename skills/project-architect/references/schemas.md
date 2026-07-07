# Inter-Agent Data Contracts

Every handoff between agents MUST have a defined Pydantic schema. No loose dicts.

## Pattern
```python
from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime

class AgentOutput(BaseModel):
    """Define what Agent A produces and Agent B expects."""
    task_id: str = Field(..., description="Unique task identifier")
    timestamp: datetime = Field(default_factory=datetime.now)
    status: Literal["success", "failed", "needs_review"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str = Field(..., description="WHY this decision was made")
    data: dict  # The actual payload

class ValidationResult(BaseModel):
    valid: bool
    errors: list[str] = []
    warnings: list[str] = []
```

## Validation at Every Boundary
```python
def agent_a_to_agent_b(raw_output: dict) -> AgentOutput:
    """Validate that Agent A produced what Agent B expects."""
    return AgentOutput(**raw_output)  # Raises ValidationError if contract broken
```

## Rules
- Every schema includes `reasoning` field — agents MUST explain their decisions
- Every schema includes `confidence` field — enables parking lot routing
- Use `Literal` types for enums, never free-form strings for categories
- Schema files live in `src/schemas/` and are imported by both agents
- When schema changes, BOTH agents must be updated — treat it like an API migration

## Gotchas
- LLMs sometimes return JSON with extra/missing fields — Pydantic catches this
- Always use `model_validate()` not manual dict parsing
- If an agent adds a new field, make it `Optional` with a default to avoid breaking the other agent
