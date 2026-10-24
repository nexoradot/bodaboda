# BodaPay — High-End System Delivery Plan

## Objective
Upgrade the existing repository into a secure, server-backed fleet, rider, payment, arrears and recovery platform. The current browser-only interface is a prototype; it is not a production payment system.

## Core product modules
1. **Organization and access:** owner workspace, operations manager, finance/cashier, rider, and platform administrator roles; invitation and account recovery; server-side permissions; audit trail.
2. **Rider records:** identity and contact details, onboarding documents, next-of-kin where appropriate, status history, motorcycle assignment history, agreement acknowledgement and controlled access to sensitive data.
3. **Fleet register:** unique registration, make/model, ownership, insurance/licensing/service reminders, active/maintenance/inactive status, rider assignment timeline.
4. **Agreements and obligations:** effective-dated agreements, daily/weekly/monthly obligations, due dates, grace periods, holidays/approved pauses, payment allocation policy, signed/accepted version and immutable terms snapshot.
5. **Payment collection:** rider payment instructions and reminders; initiate STK Push only from the backend after credentials are configured; display pending until verified callback/reconciliation; unique provider transaction IDs; retries, duplicate callback protection, reversals and manual-payment evidence.
6. **Ledger and reconciliation:** append-only transaction events, receipt numbers, payment allocation to obligations, partial and excess payments, adjustments with reasons and approver, daily reconciliation and export.
7. **Arrears and recovery:** compute balances from obligations less verified allocations; ageing buckets; recovery notes and promises-to-pay; contact attempt history; disputes, waivers and settlement approvals; never silently overwrite balances.
8. **Notifications:** configurable due-date reminders and overdue escalations via approved SMS/WhatsApp/email providers; delivery states, retry queue, opt-out/preferences where required.
9. **Operations dashboard:** active riders and bikes, collections due/received, overdue balances, payment failures, recovery pipeline, fleet utilization and exceptions.
10. **Reports:** rider statement, motorcycle statement, daily collection sheet, arrears ageing, recovery log, payment reconciliation, audit/export reports.
11. **Support and governance:** incident/dispute register, data access controls, retention and privacy processes, backup/restore, monitoring and operational runbooks.

## Money and data integrity rules
- A payment is not successful because an STK Push request was sent. It becomes confirmed only after server-side verification of the provider response/callback and reconciliation rules.
- Store amounts as decimal values and use a server-generated unique internal reference plus unique provider transaction reference.
- Use database transactions and idempotency keys for payment allocation and callback handling.
- Derive outstanding balances from dated obligations and verified ledger allocations; retain every adjustment and its reason/actor/time.
- Keep agreement terms effective-dated and snapshot the agreed payment and penalty terms.
- Enforce ownership/workspace scope in every API query, not only in the interface.
- Do not store M-Pesa secrets in frontend code or GitHub.
- Clearly label demo/simulated transactions; do not issue demo receipts as proof of actual payment.

## Delivery phases
### Phase 1 — Discovery and workflow sign-off
Confirm operating model, payment frequency, rider onboarding, due-date rules, grace periods, recovery steps, roles, reports, provider/merchant arrangements and approval limits. Map current spreadsheets/books and agree on a migration and reconciliation plan.

### Phase 2 — Secure platform foundation
Configure production settings, PostgreSQL, migrations, authentication, role/organization isolation, audit events, error handling, backups and automated tests.

### Phase 3 — Operational records and ledger
Implement rider/fleet/assignment/agreement workflows, obligation generation, immutable ledger, allocation, rider statements, arrears ageing and recovery case tracking. Reconcile all views against the same source of truth.

### Phase 4 — Payment provider and reminders
Implement Daraja sandbox integration, server-side STK Push, callback validation, idempotency, transaction reconciliation, receipt issuance after confirmation, notification delivery and retry monitoring. Complete provider approval and production credential setup before live payments.

### Phase 5 — Pilot and launch
Import reconciled records, train owner/operations/finance/riders, run a limited pilot, test failures/reversals/disputes and daily reconciliation, sign off privacy/security and recovery processes, then launch with monitoring and support.

## Acceptance criteria
- Owner and operations manager see the same balances and transaction history.
- Every payment is traceable from initiation through confirmation, allocation, receipt and reconciliation.
- Duplicate callbacks do not create duplicate credits.
- No user can read or alter another workspace's data without explicit authorization.
- Every balance adjustment has a reason, actor, timestamp and approval where required.
- Rider statements reconcile to the ledger and obligation schedule.
- Failed or pending payments are not shown as confirmed collections.
- Reports export consistently and can be reconciled to source transactions.
- Backup restore, access-control, payment edge-case and audit tests pass.

## Decisions required from client
- Is the arrangement hire-purchase, daily remittance, lease, loan repayment, or another contract type?
- How often is payment due, and what are the grace period and non-working-day rules?
- Which payment channels are used (M-Pesa Paybill/Till, STK Push, bank, cash)?
- Who can record cash/bank payments and who approves corrections, waivers and settlements?
- What is the agreed recovery workflow and escalation authority?
- Which notifications, languages and channels should be used?
- What reports and opening balances need to be migrated?
- How many owners, motorcycles, riders and concurrent users are expected?
- Which Safaricom/provider merchant arrangement is already approved?

## Current repository boundary
The current frontend is a localStorage demo, and the Django backend is a scaffold. The Daraja endpoints are deliberately not configured. Production readiness must not be claimed until server-side authentication, tenant isolation, durable database, verified payment integration, reconciliation, monitoring, privacy review and end-to-end testing are complete.
