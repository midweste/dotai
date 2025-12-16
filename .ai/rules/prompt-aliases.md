# Prompt Aliases

- **code sweep**

  1. Run the project’s automated test suite using the repo’s scripts; fix any failures.
  2. Run the project’s static analysis/lint tools; fix reported issues.
  3. Re-run the tests to confirm everything is green.
  4. Report remaining blockers or confirm success.

- **qa sweep**
  Follow `.ai/rules/quality-assurance.md` end-to-end, applying all relevant checks for the requested scope.

- **tdd sweep**
  Write a failing test for the desired behavior, make it pass, then refactor while keeping the suite green; prefer integration-first per `.ai/rules/testing.md`.

- **security sweep**
  Apply platform security checks: capability/nonce/authz validation, input sanitization, output escaping, prepared statements, secrets from env only; scan recent changes for security regressions and add tests where missing.

- **performance sweep**
  Review critical paths for N+1s, caching/transients/object cache usage, asset size/versioning, and blocking external calls; suggest concrete optimizations and note required measurements.

- **doc sweep**
  Update relevant docs (README/PROJECT/inline) for behavioral or command changes; summarize risk, rollout, and env vars touched.
