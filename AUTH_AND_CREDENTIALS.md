# Navan Connector — Authentication & Credentials

## Supported Authentication Model
- **Primary Method:** Bearer Access Token / API Key issued from Navan Admin Console.
- **Header:** `Authorization: Bearer <api_key>`
- **Validation:** Executed on connection via `GET /v1/me`.
- **Security Standards:**
  - Tokens are stored encrypted in Imperal secrets storage under key `navan_connections`.
  - Sensitive token values are masked in connection listings (`_mask`).
  - All outgoing HTTP requests and error logs redact API keys via `_sanitize_msg`.
