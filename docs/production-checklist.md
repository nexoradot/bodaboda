# BodaPay release checklist

## Security and access
- [ ] Implement account registration, login, phone OTP, password reset and session controls.
- [ ] Add owner/rider/admin role authorization and query-level data isolation; test cross-account access.
- [ ] Use production secrets; set DEBUG=0, strict ALLOWED_HOSTS, HTTPS, secure cookies and CSRF settings.
- [ ] Add rate limits, audit trails for sensitive changes and security checks.

## Money movement
- [ ] Confirm merchant/paybill/till arrangements with Safaricom and relevant providers.
- [ ] Configure Daraja sandbox before production credentials.
- [ ] Implement backend-only token acquisition and STK Push.
- [ ] Verify callbacks and reconcile transaction details server-side.
- [ ] Make callbacks idempotent; enforce unique transaction codes; handle duplicate/out-of-order callbacks.
- [ ] Never treat an STK initiation response as final payment confirmation.
- [ ] Test partial/overpayments, reversals, timeouts, rider reassignment and corrections.

## Accounting
- [ ] Document obligation dates, grace periods, mid-cycle plan changes, partial-payment allocation and overpayment rules.
- [ ] Calculate obligations from plans and qualifying confirmed ledger entries.
- [ ] Snapshot agreed penalty rules when agreements are accepted.
- [ ] Test computations and reconcile owner, rider and report views.

## Operations and privacy
- [ ] Configure PostgreSQL, backups and restore drills.
- [ ] Configure SMS/push providers with retries and delivery tracking.
- [ ] Publish privacy policy, retention schedule and user data access/correction procedures.
- [ ] Review Kenyan data-protection requirements with qualified counsel.
- [ ] Complete permission, payment, concurrency and recovery testing before pilot.

## Known demo boundary
Frontend browser storage is only for UI exploration. The API scaffold defaults to administrator-only access. M-Pesa STK Push and callback handlers deliberately return not-configured until verification is implemented. This repository is not production-ready.
