# Quality Assurance

## Scope

- ONLY act on folders containing a `merge.json` at their root (primary) or paths in PROJECT.md "Owned Code Paths" (fallback); skip vendor, core, and contributed plugins.
- This is to prevent changes and updates to core files and plugins that the user does not control.
- If there are bugs in core files and plugins, report them to the user with suggested fixes so they can be filed as tickets with authors.

## Initiation

- Apply this checklist only when explicitly asked to "prepare for production" or "review for production."
- State clearly when a rule cannot be verified (e.g., missing tooling) and suggest how to verify.

## Baseline Readiness

- All tests green; new behavior covered by integration-first tests plus targeted unit tests where they add confidence.
- Lint/format clean with project-standard tools (PHPStan/Psalm, ESLint, stylelint, etc.).

## Language-Specific Checks

- PHP: run the project’s configured PHPUnit and static analysis (PHPStan/Psalm) commands—use repo scripts/config, not hard-coded defaults.
- PHP: never commit PHPStan stub content into production source files; keep stubs in dedicated stub files/paths defined by the project config.
- JS/CSS: run the project’s configured test and lint commands; use the repo’s package scripts and configs.

## Code & Design

- Single-responsibility classes/functions; no feature logic parked in UI layers.
- Inputs validated at boundaries; typed interfaces and strict comparisons enforced.
- Remove dead/unused code, feature-flag stubs, and debug scaffolding.

## Security & Privacy Governance

### Data Handling

- Treat every artifact as production-bound: never include secrets, credentials, or customer data in prompts, logs, or generated files.
- Redact or mock sensitive values when sharing snippets; prefer environment variables over hard-coded strings.
- When adding an environment variable in code, always add it to `.env` and `.env.example` (if present) with a sensible default or placeholder.

### Access Controls

- Enforce role or capability checks before any privileged action, matching the platform's authorization model.
- Protect every state-changing request with anti-forgery tokens (nonces/CSRF tokens) and reject missing or invalid tokens.
- Use prepared statements or safe query builders for all database access, and sanitize external input with the platform's canonical helpers.

### Output Escaping

- Escape HTML, attributes, URLs, and JSON at the point of output using the platform's escaping primitives.
- For dynamic rich content, whitelist tags/attributes explicitly and document the allowed set.
- Default to safest encoding: HTML-escape text, attribute-escape attrs, URL-escape href/src, and JSON-encode structured data before output.

### Logging & Escalation

- Log security-relevant failures (nonce, capability, validation) using the project's logging facilities or `error_log` during development.
- Surface suspected vulnerabilities immediately via the security communication channel defined by the team; pause automation until issues are triaged.

### AI-Specific Guardrails

- Decline to execute destructive commands unless explicitly instructed by a human operator.
- When uncertain about compliance, fall back to read-only suggestions and request clarification rather than guessing.
- Never display or echo secrets from files, env vars, or configs; redact with clear placeholders.
- If a potential secret is detected, stop and notify the user to rotate it; do not copy it into responses.

## Performance & Stability

- Guard expensive operations with caching/transients where appropriate; avoid N+1 queries.
- Keep external calls wrapped with timeouts/retries; avoid blocking the main request when not required.
- Ensure deterministic tests and predictable time/clock usage (injected clocks).

## Refactoring

- When refactoring, always update the tests to match the new code.
- When refactoring, always update the documentation to match the new code.
- When refactoring, always ask if existing functions need a wrapper or can be replaced.

## Performance Review

- Capture baselines: measure key flows (page render, REST/AJAX endpoints, cron/queue jobs) for time, queries, and memory before/after changes.
- Check database efficiency: no N+1s; indexes used for new queries; paginate large result sets.
- Review assets: keep bundle sizes and critical CSS lean; compress/optimize images; ensure caching headers/versioning are in place.
- Validate caching strategy: object cache/transients for repeat lookups; avoid per-request rewrite flushes; ensure cache keys are scoped and invalidated correctly.
- Assess async/offline work: move heavy tasks to queues/cron where safe; ensure jobs are idempotent and bounded with timeouts/retries.
- Confirm configuration: production settings disable verbose logging/debug; timeouts appropriate for upstream calls.

## Compatibility & Accessibility

- Confirm browser/runtime targets and polyfills (if any) align with project standards.
- CSS uses custom properties/tokens; respects `prefers-reduced-motion`; meets WCAG AA contrast.

## Documentation & Ops

- Update README/PROJECT docs where behavior or commands change.
- Note migrations, cron/queue impacts, and new environment variables (names only).
- Provide release notes or a change summary highlighting risks, rollbacks, and manual steps.

## Observability

- Use structured logging; redact sensitive fields.
- Add/align metrics or trace identifiers for new flows where meaningful.
- Ensure error handling paths surface actionable messages without leaking stacks to users.

## Verification Steps (suggest to run)

- Run full test suite and linters.
- Exercise critical user paths manually (happy + edge cases).
- Verify install/activate/uninstall flows for plugins; ensure rewrites not flushed per request.

## Security Sweep

Apply platform security checks across the codebase or a targeted scope:

- Validate capability/nonce/authz on every state-changing action.
- Audit input sanitization at every boundary (forms, REST, CLI, queue payloads).
- Confirm output escaping at every render point (HTML, JSON, headers).
- Verify all database access uses prepared statements or parameterized ORM queries.
- Ensure secrets come from environment only — no hard-coded keys, DSNs, or tokens.
- Scan recent changes (since last release/tag) for security regressions.
- Add or update tests for any gaps found.

## Performance Sweep

Review critical paths for efficiency and suggest concrete optimizations:

- Identify N+1 query patterns; suggest eager-loading or batch queries.
- Audit caching/transients/object cache usage; verify keys are scoped and invalidated correctly.
- Check asset size and versioning (bundle sizes, critical CSS, image optimization).
- Flag blocking external calls in the request lifecycle; suggest async/queue alternatives.
- Capture before/after measurements where possible (query count, response time, memory).
- Note any findings that require profiling tools the agent cannot run.

## TDD Sweep

Apply test-driven development to the requested behavior:

1. Write a failing test that describes the desired behavior.
2. Implement the minimum code to make it pass.
3. Refactor while keeping the suite green.
4. Prefer integration-first tests per `.agent/rules/testing.md`.
5. Add targeted unit tests only where they add confidence beyond integration coverage.

## Cleanup

- Remove temporary files/fixtures created during testing.
- Ensure git status is clean except for intentional changes; do not leave generated artifacts unless required.
