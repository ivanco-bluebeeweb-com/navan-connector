# Navan Connector — Ideal Onboarding Experience

1. **Prerequisites**: Administrator or Integration Manager access in Navan.
2. **Key Generation**: Navigate to Company Settings > Integrations > API Access and generate an API key.
3. **Connecting in Imperal**:
   - Open Navan in Imperal OS.
   - Enter a connection label (e.g. Acme Navan Production).
   - Enter the API Key in the sidebar form.
   - Click "Connect Navan".
4. **Verification**: The connector runs `verify_auth()` to validate credentials against `/v1/me` and creates the active connection record.
