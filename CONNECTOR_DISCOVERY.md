# Navan Connector — Discovery & API Architecture

## Vendor Overview
Navan (formerly TripActions) is an all-in-one corporate travel, card, and expense management platform used by modern enterprises to automate expense reconciliation, manage card spend limits, and disburse employee reimbursements.

## Verified Endpoints & Schemas
- `GET /v1/me`: Validates API key authenticity and returns connected company profile.
- `GET/POST /v1/expenses`: Query and record card and out-of-pocket transactions.
- `GET/POST /v1/cards`: Provision, inspect, and freeze corporate virtual/physical cards.
- `GET/POST /v1/reports`: Review and approve consolidated expense reports.
- `GET/POST /v1/policies`: Spend limit and policy rule inspection.
- `GET/POST /v1/merchants`: Merchant categorization registry.
- `GET/POST /v1/reimbursements`: ACH/bank reimbursement tracking.

## Value-Add Functions
- `audit_spend_compliance`: Scans recent expense submissions and flags non-compliant or flagged transactions.
- `get_spend_overview`: Aggregates spend volume by merchant category and department.
