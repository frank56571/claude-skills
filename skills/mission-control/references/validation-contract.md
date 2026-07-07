# Validation Contract

Written in Phase 2, **before any code exists**. Defines correctness independently of implementation: assertions describe observable behavior, never internal structure. Tests written after implementation confirm decisions; the contract defines them.

## Rules

- Each assertion = observable behavior + how it will be verified. Can't state the verification method? The assertion is too vague — rewrite it.
- Every feature satisfies ≥1 assertion; every assertion is covered by ≥1 feature. If the sums don't close, the plan is wrong.
- After user approval, **only the user amends the contract**. Workers and validators never edit it. Log every amendment in MISSION.md.
- Scale honestly: a real project needs dozens–hundreds of assertions. Group by area.

## Format

```markdown
# Validation Contract — {mission}
Approved by user: {YYYY-MM-DD}

## {Area, e.g. Invoicing}
- **A-001** — POST /invoices with a past-due date returns 422 with error code INVOICE_DATE_PAST
  - Verify: pytest tests/test_invoices.py::test_past_due_rejected
  - Features: F-003
- **A-002** — Creating an invoice from the UI shows it in the list without a page reload
  - Verify: e2e — fill form, submit, assert row appears
  - Features: F-003, F-004
```

## Anti-patterns

- ❌ "Code is well-structured" — not observable behavior.
- ❌ "All tests pass" — circular; the contract exists precisely because post-hoc tests confirm rather than define.
- ❌ Assertion reverse-engineered from the implementation after the fact.
- ❌ Assertion without a concrete verification method.
