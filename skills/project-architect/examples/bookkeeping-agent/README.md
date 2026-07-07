# Example: Bookkeeping Agent (PARSER/SCRIBE)

Real architecture from Aldyne's accounting automation system.

## Agents

### PARSER
- Reads bank feeds and receipts (OCR via Tesseract)
- Outputs `ParsedTransaction` schema
- CAN: read QB bank feeds, process images, extract text
- CANNOT: write to QB, modify accounts, send anything

### SCRIBE
- Receives `ParsedTransaction` from PARSER
- Categorizes using client rules from `config/client-rules/`
- Outputs `JournalEntryDraft` schema
- CAN: read client rules, create drafts, query category history
- CANNOT: publish to QB without explicit owner approval

## Data Flow
```
QB Bank Feed → PARSER → ParsedTransaction (validated) → SCRIBE → JournalEntryDraft (validated) → Approval Queue → Human Approves → Publish to QB
```

## Schemas
```python
class ParsedTransaction(BaseModel):
    transaction_id: str
    date: date
    description: str
    amount: float
    currency: Literal["USD", "DOP"]
    vendor_name: str | None = None
    suggested_category: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    source: Literal["bank_feed", "receipt_ocr", "manual"]

class JournalEntryDraft(BaseModel):
    transaction_id: str
    account_debit: str
    account_credit: str
    amount: float
    memo: str
    category: str
    requires_approval: bool
    reasoning: str
    confidence: float = Field(ge=0.0, le=1.0)
```

## Parking Lot Triggers
- confidence < 0.7
- description is empty or "MISC DEBIT"
- vendor not found in client's category_rules
- amount is negative (refund/adjustment — needs human classification)
- duplicate transaction detected (same amount + date + vendor within 24h)

## Client Config Key Fields
- `category_rules`: vendor name → category + account mapping
- `approval_thresholds.auto_approve_below`: 500 USD
- `special_rules`: "All transactions over $5000 require partner review"
