# Security & Privacy Governance

## Data Handling

- Treat every artifact as production-bound: never include secrets, credentials, or customer data in prompts, logs, or generated files.
- Redact or mock sensitive values when sharing snippets; prefer environment variables over hard-coded strings.
- When adding an environment variable in code, always add it to `.env` and `.env.example` (if present) with a sensible default or placeholder.

## Access Controls

- Enforce role or capability checks before any privileged action, matching the platform’s authorization model.
- Protect every state-changing request with anti-forgery tokens (nonces/CSRF tokens) and reject missing or invalid tokens.
- Use prepared statements or safe query builders for all database access, and sanitize external input with the platform’s canonical helpers.

## Output Escaping

- Escape HTML, attributes, URLs, and JSON at the point of output using the platform’s escaping primitives.
- For dynamic rich content, whitelist tags/attributes explicitly and document the allowed set.
- Default to safest encoding: HTML-escape text, attribute-escape attrs, URL-escape href/src, and JSON-encode structured data before output.

## Logging & Escalation

- Log security-relevant failures (nonce, capability, validation) using the project’s logging facilities or `error_log` during development.
- Surface suspected vulnerabilities immediately via the security communication channel defined by the team; pause automation until issues are triaged.

## AI-Specific Guardrails

- Decline to execute destructive commands unless explicitly instructed by a human operator.
- When uncertain about compliance, fall back to read-only suggestions and request clarification rather than guessing.
- Never display or echo secrets from files, env vars, or configs; redact with clear placeholders.
- If a potential secret is detected, stop and notify the user to rotate it; do not copy it into responses.
