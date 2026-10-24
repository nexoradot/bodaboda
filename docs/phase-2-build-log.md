# Phase 2 build log

## Implementation boundary
The existing Django API is a scaffold. Payment endpoints intentionally do not process live M-Pesa transactions. Production readiness requires verified Daraja callbacks, PostgreSQL, authorization and tenant isolation, ledger services, migrations and tests.

## Next engineering sequence
1. Add daily obligations with a unique `(plan, due_date)` constraint and an idempotent generator.
2. Add append-only ledger entries with unique idempotency keys. Confirmed payment entries must only be written after provider verification.
3. Calculate arrears from due obligations and ledger allocations. Keep penalties separate and apply only client-approved contract rules.
4. Add Operations recovery cases and an auditable activity timeline.
5. Add organization/membership authorization and enforce organization scope on every API queryset before exposing operational records.
6. Add migrations and tests for duplicate generation, duplicate callbacks, partial payments, reversals and access isolation.
7. Validate spreadsheet imports against signed-off opening balances before a controlled pilot.

## Client settings still to approve
- Daily cutoff and approved rest days/pauses.
- Payment allocation order (candidate: oldest overdue obligation first).
- Grace period and penalty rules.
- Approval authority for waivers, corrections, settlements and reversals.
- Spreadsheet source of truth and opening-balance sign-off.
