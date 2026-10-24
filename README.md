# BodaPay — BodaBoda Rider & Owner Payment Management

A mobile-first demo for managing motorcycle owners, riders, daily payment agreements, payment history, arrears estimates, notifications and reports in Kenya.

## Demo status

This repository contains a **local interactive prototype** and a Django REST Framework backend scaffold. Browser data is demo-only and saved in local storage. No real M-Pesa payment is processed by the demo.

## Run the frontend demo

1. Open the `frontend/` directory.
2. Open `index.html` in a modern browser (Chrome, Edge or Firefox).
3. Use the role selector to preview Owner, Rider and Administrator views.
4. Add/edit demo motorcycles and riders, create agreements, record simulated payments, review arrears, use notifications, print sample receipts, and export CSV reports.

You can also serve the repository locally from its root:

```bash
python -m http.server 8080
```

Then open `http://localhost:8080/frontend/`.

## Run the API scaffold

Python 3.11+ recommended.

```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

API root: `http://127.0.0.1:8000/api/`.

## Core workflow

- Owner registers motorcycles and riders.
- Owner configures a daily payment plan, cycle dates and agreed penalty rule.
- Rider sees the obligation and payment history.
- In the eventual server-backed implementation, payments should be recorded only after a verified confirmation event.
- Arrears and penalties should be calculated from an auditable ledger, not a manually edited balance.
- Owners and riders receive notices; administrators can review reports and audit records.

## Before real-world launch

- Implement and test complete server-side authentication, phone verification, role-based authorization and tenant isolation.
- Connect PostgreSQL and deploy secure environment configuration, backups and monitoring.
- Finish Daraja STK Push, callback verification, idempotency and transaction reconciliation using official Safaricom documentation. An STK initiation response must not be treated as final payment confirmation.
- Test partial payments, overpayments, rider reassignment, plan changes, duplicate callbacks, concurrency and payment corrections.
- Implement production SMS/push notifications and document the privacy/retention policy.
- Obtain relevant Kenyan legal and data-protection advice before commercial use.

Never collect or store the rider's M-Pesa PIN. Do not use the browser-local demo records as a financial source of truth.

## Product specification

The system is based on the BodaBoda Rider & Owner Payment Management System Project Guide supplied for this project.