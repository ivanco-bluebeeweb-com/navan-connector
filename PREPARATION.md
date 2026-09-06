# Navan Connector — Preparation

## Product Scope
Build a comprehensive Imperal connector for **Navan** (formerly TripActions) under category **C29. Expense Management & Corporate Cards**. The integration interacts directly with Navan's Expense and Corporate Card REST APIs (`https://api.navan.com`), providing visibility and controls across corporate cards, out-of-pocket expenses, expense reports, spend policies, merchant categorization, employee reimbursements, and automated compliance auditing.

## Official API Specifications
- **API Architecture:** RESTful JSON API
- **Base URL:** `https://api.navan.com`
- **Core Endpoints:**
  - `GET /v1/me` — verify token privileges and company context
  - `GET /v1/expenses` — list expenses with cursor pagination
  - `GET /v1/expenses/{id}` — detailed expense breakdown
  - `GET /v1/cards` — virtual and physical corporate cards
  - `GET /v1/reports` — aggregated expense reports
  - `GET /v1/policies` — travel and spend limit policies
  - `GET /v1/merchants` — merchant classifications
  - `GET /v1/reimbursements` — employee reimbursement disbursements
- **Authentication Model:** Bearer Token via `Authorization: Bearer <api_key>`
- **Mandatory Requirements:**
  - Strict error classification: HTTP 429 rate limits with Retry-After extraction, HTTP 401/403 differentiation (Standard B8/B10).
  - Sanitization of Bearer tokens and API keys in error traces and diagnostic payloads (Standard B8).
  - Multi-tenant connection tracking and isolation via `connection_id` (Standard B9).

## Delivery Gates
1. [x] Official API discovery completed with Navan REST API specifications.
2. [x] Core resource endpoints and Bearer auth verified.
3. [x] Five mandatory specification documents authored.
4. [x] Client implemented with B8-B10 compliance, secret redaction, and 429/401 classification.
5. [x] Panel sidebar implemented conforming to UI_INTERFACE_STANDARD.md.
6. [x] Verification of functions, imports, and type hints passed.
7. [x] Deployment to Imperal platform completed.
8. [x] Tool pricing configured according to PRICING_POLICY.md.
