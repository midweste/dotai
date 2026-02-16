# Engineering Best Practices

Complement workflow rules. Apply to all code changes.

## API / Interface Discipline

- Stable interfaces at boundaries (functions, modules, components). Optional params over duplicated paths. Consistent error semantics.

## Testing Strategy

- Smallest test that catches the bug. Unit for pure logic, integration for boundaries, E2E for critical flows only. Avoid brittle implementation-detail tests.

## Type Safety

- No suppressions (`any`, ignores) without project permission. Validate at boundaries, not scattered checks.

## Dependencies

- No new deps unless existing stack can't solve it cleanly. Prefer stdlib/existing utilities.

## Security & Privacy

- No secrets in code, logs, or output. User input is untrusted — validate, sanitize, constrain. Least privilege.

## Performance

- No premature optimization. Fix N+1s, unbounded loops, repeated heavy computation. Measure when in doubt.

## Accessibility (UI Changes)

- Keyboard nav, focus management, readable contrast, meaningful empty/error states.

## Git Hygiene

- Atomic commits; no "misc fixes" bundles. Don't mix formatting with behavioral changes. Generated files committed only if project expects it.

## Definition of Done

Behavior matches criteria · tests/lint/build pass · rollback strategy for risky changes · code follows conventions · verification story exists.

## Templates

**Plan** (`TODO.md`): Goal → locate patterns → design → implement → test → verify → summarize → lessons.

**Bugfix**: Repro steps → expected vs actual → root cause → fix → regression coverage → verification → risk/rollback.
