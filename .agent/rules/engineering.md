# Engineering Best Practices

Standards for code quality, testing, dependencies, and change hygiene. These complement the workflow rules and apply to all code changes.

---

## API / Interface Discipline

- Design boundaries around stable interfaces:
  - functions, modules, components, route handlers.
- Prefer adding optional parameters over duplicating code paths.
- Keep error semantics consistent (throw vs return error vs empty result).

## Testing Strategy

- Add the smallest test that would have caught the bug.
- Prefer:
  - unit tests for pure logic,
  - integration tests for DB/network boundaries,
  - E2E only for critical user flows.
- Avoid brittle tests tied to incidental implementation details.

## Type Safety and Invariants

- Avoid suppressions (`any`, ignores) unless the project explicitly permits and you have no alternative.
- Encode invariants where they belong:
  - validation at boundaries, not scattered checks.

## Dependency Discipline

- Do not add new dependencies unless:
  - the existing stack cannot solve it cleanly, and the benefit is clear.
- Prefer standard library / existing utilities.

## Security and Privacy

- Never introduce secret material into code, logs, or chat output.
- Treat user input as untrusted:
  - validate, sanitize, and constrain.
- Prefer least privilege (especially for DB access and server-side actions).

## Performance (Pragmatic)

- Avoid premature optimization.
- Do fix:
  - obvious N+1 patterns, accidental unbounded loops, repeated heavy computation.
- Measure when in doubt; don't guess.

## Accessibility and UX (When UI Changes)

- Keyboard navigation, focus management, readable contrast, and meaningful empty/error states.
- Prefer clear copy and predictable interactions over fancy effects.

---

## Git and Change Hygiene

- Keep commits atomic and describable; avoid "misc fixes" bundles.
- Don't rewrite history unless explicitly requested.
- Don't mix formatting-only changes with behavioral changes unless the repo standard requires it.
- Treat generated files carefully:
  - only commit them if the project expects it.

---

## Definition of Done (DoD)

A task is done when:

- Behavior matches acceptance criteria.
- Tests/lint/typecheck/build (as relevant) pass or you have a documented reason they were not run.
- Risky changes have a rollback/flag strategy (when applicable).
- The code follows existing conventions and is readable.
- A short verification story exists: "what changed + how we know it works."

---

## Templates

### Plan Template (Paste into `TODO.md`)

- [ ] Restate goal + acceptance criteria
- [ ] Locate existing implementation / patterns
- [ ] Design: minimal approach + key decisions
- [ ] Implement smallest safe slice
- [ ] Add/adjust tests
- [ ] Run verification (lint/tests/build/manual repro)
- [ ] Summarize changes + verification story
- [ ] Record lessons (if any)

### Bugfix Template (Use for Reports)

- Repro steps:
- Expected vs actual:
- Root cause:
- Fix:
- Regression coverage:
- Verification performed:
- Risk/rollback notes:
