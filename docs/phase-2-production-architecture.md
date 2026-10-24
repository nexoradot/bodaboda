# BodaPay — Phase 2 Production Architecture (Client-Aligned)

## Confirmed operating assumptions
- Daily payment obligation.
- M-Pesa is the intended primary collection channel.
- Initial operating fleet is approximately 50–200 motorcycles.
- The Operations Manager owns arrears follow-up and recovery case handling.
- Current operational records are spreadsheets and must be imported only after reconciliation.
- The existing repository and current frontend remain the project baseline. Demo/localStorage records are not the production financial source of truth.

## Target architecture
- **Web client:** existing responsive BodaPay UI, progressively switched from localStorage demo operations to authenticated API calls. Demo mode must be visibly separated from live mode.
- **Application API:** Django REST Framework. All financial calculations and payment status transitions occur server-side.
- **Database:** PostgreSQL in hosted environments; SQLite may be used for local development only. Use migrations and managed backups.
- **Identity and permissions:** authenticated accounts, role-based access (Owner, Operations Manager, Finance/Collections, Rider, Platform Administrator), least privilege and workspace scoping on every query.
- **Payment integration:** backend-only Safaricom Daraja adapter. Secrets in deployment environment/secret manager, never frontend source or repository. STK initiation is a pending request only; verified callback/reconciliation is required before crediting a rider.
- **Notifications:** provider adapter and durable delivery records with retry/error status. Do not pretend that an SMS or WhatsApp message was sent unless a provider confirms it.
- **Operations:** structured logs without PINs/secrets, audit events for sensitive actions, health/readiness checks, backups, restore testing and monitored deployment.

## Core domain model
1. Organization/workspace — legal/business name, timezone (Africa/Nairobi), status and settings.
2. Membership — user, organization, role, status; one user may have explicitly granted memberships.
3. Rider — profile, contact details, optional identity references, onboarding status and consent/notice tracking.
4. Motorcycle — unique registration scoped to an organization, make/model, status and fleet metadata.
5. Assignment — dated rider-to-motorcycle history; prevent conflicting active assignments.
6. Agreement/plan — motorcycle, rider/assignment, daily amount, start/end dates, due-time and grace policy, agreed terms version, approval/acceptance timestamps and status.
7. Daily obligation — one dated amount due per active agreement day, with approved pause/holiday exceptions recorded rather than deleting history.
8. Payment attempt — internal UUID, amount, phone, idempotency key, provider checkout reference, state and timestamps. Never store a rider M-Pesa PIN.
9. Verified payment — unique provider transaction code, amount, payer/reference, callback evidence, verification time and reversal linkage.
10. Allocation/ledger entry — immutable credit/debit entries linking confirmed money to daily obligations; corrections use reversal/adjustment entries, not edits or deletion.
11. Recovery case/activity — case status, owner (Operations Manager), ageing, contact attempts, promise-to-pay, dispute/hold, next action, notes and closure reason.
12. Notification — channel, recipient, template, delivery state, retry count and provider reference.
13. Audit event — actor, organization, action, entity, timestamp, reason and minimal before/after metadata. Exclude secrets and unnecessary sensitive data.

## Authoritative balance formula
For a rider/agreement and date:
- Obligations due = sum of generated daily obligations that are due and not legitimately paused/voided through an audited process.
- Net confirmed payments = sum of verified allocations minus linked reversals.
- Outstanding principal = obligations due minus net allocations, floored at zero only for display; retain any credit balance separately.
- Penalties are calculated only under approved and disclosed contract rules after grace days, and remain a separate ledger category from principal.
- Never treat a pending, failed, unverified or simulated payment as received money.

## Daily operating workflow
1. At a configured Africa/Nairobi cutoff, generate obligations idempotently for active agreements.
2. Send due reminders using the configured channel; record each delivery attempt.
3. Rider initiates M-Pesa payment from an authenticated session or approved payment prompt.
4. API records a pending payment attempt and initiates Daraja STK Push only when configured.
5. Verified callback handler validates expected fields and amount/reference, deduplicates transaction codes, and records the payment inside a database transaction.
6. Ledger allocation applies the agreed policy (oldest due first is a candidate, but must be approved by the client); issue a receipt only after confirmation.
7. Reconciliation compares provider transactions with internal payment attempts and surfaces unmatched, duplicate, reversed and late callbacks.
8. Overdue obligations create/update recovery cases for the Operations Manager. Every contact, promise, dispute, adjustment and closure is logged.
9. Owner and Operations Manager dashboards use the same server-side queries and show a shared as-of timestamp.

## Spreadsheet migration plan
1. Obtain the actual spreadsheets and identify every tab, formula, hidden row and duplicate.
2. Agree a source-to-target mapping for riders, motorcycle registrations, assignments, daily agreements, opening principal, receipts, arrears, and historical payments.
3. Create a staging import with row number, source filename, import batch ID, validation errors and duplicate detection.
4. Normalize dates to Africa/Nairobi, money to decimal KES, phone numbers to normalized Kenyan format and motorcycle registrations to a consistent uppercase format.
5. Reconcile opening balances per rider/motorcycle against signed-off source totals. Do not silently infer missing transactions.
6. Preview errors and duplicates to the Operations Manager; correct the source or explicitly approve documented exceptions.
7. Import in a transaction with an audit trail and import-batch reference; retain original source files according to the agreed retention policy.
8. Run a parallel reconciliation period before retiring spreadsheets.

## Security and reliability controls
- Server-side authorization and organization filtering for every list/detail/write endpoint.
- Separate live payment credentials by environment; no secrets in GitHub, logs, or browser.
- Idempotency for payment initiation and callbacks; unique constraints for provider transaction IDs.
- Database transactions around confirmation, ledger posting and allocation.
- Use UTC timestamps internally and Africa/Nairobi for business dates and display.
- Rate limit authentication and payment initiation; validate phone, amount and ownership server-side.
- Production DEBUG off, strict hosts, HTTPS, secure cookies, CSRF and restrictive CORS.
- Minimize ID data, restrict access, document retention and support access/correction requests.
- Automated tests for access isolation, daily obligation generation, partial payments, overpayments, duplicates, reversals, delayed callbacks, rider reassignment, pauses, import reconciliation and recovery audit.
- Restore drills and a documented incident/support process.

## Implementation sequence
### Phase 2A — Secure foundation
Production-safe settings, PostgreSQL environment support, migrations, workspace/membership and role permissions, audit helpers, API tests, CI validation.

### Phase 2B — Ledger first
Daily obligation generation, confirmed payment ledger, allocation rules, balances and statements. Build reconciliation tests before any real provider integration.

### Phase 2C — Recovery operations
Operations Manager queue, ageing buckets, next actions, promises-to-pay, disputes/holds, approved waivers/settlements and complete activity history.

### Phase 2D — Daraja sandbox
Backend-only credentials, STK initiation, callback validation, idempotency, reversal handling and sandbox test evidence. Production credentials only after merchant setup and acceptance testing.

### Phase 2E — Spreadsheet migration and pilot
Import preview, row-level validation, approved opening balances, parallel reconciliation, user training, access review, backup/restore verification and signed pilot acceptance.

## Decisions to confirm with client before financial rules are frozen
- Daily cutoff and what counts as a non-working day or approved pause.
- Whether allocation is oldest overdue first, current-day first, or another agreed rule.
- Grace period and whether penalties are permitted; rate, cap, calculation base and approval.
- What happens with cash/bank payments or an M-Pesa outage (even if M-Pesa is primary).
- Who may create/approve adjustments, waivers, settlements and reversals.
- Required rider reminder timing and approved SMS/WhatsApp provider.
- Source spreadsheet layouts, data owner and signed-off opening balance totals.
- Merchant Paybill/Till and Daraja sandbox/production onboarding status.

## Release gates
Do not describe this as production-ready until database migrations and automated tests pass, access isolation is proven, ledger reconciliation is signed off, payment callbacks are verified and idempotent, spreadsheet opening balances reconcile, operational backups are restored in a drill, and the client signs the pilot acceptance checklist.
