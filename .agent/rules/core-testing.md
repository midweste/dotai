# Testing Rules (Integration-First TDD)

## Approach

- Red → green → refactor for behavioral changes. Comment/doc-only fixes may skip test-first.
- Integration tests first (observable behavior across boundaries); unit tests later for speed/confidence.
- Deterministic: isolate from real networks, clocks, filesystems. Use injected clocks for time-sensitive logic.
- Code hard to test? Reshape production code (interfaces, seams, decomposition).

## Test Design

- Names express behaviors and outcomes; include bug/regression refs.
- Cover happy paths, edge cases, failure handling. Security-sensitive flows require negative tests.
- Small, purpose-built fixtures; reset shared state between tests.

## Tooling

- PHP: PHPUnit integration style; shared setup/teardown; no global state leakage.
- JS: repo-standard runner (`npm test`); lightweight mocks; sandboxed DOM/globals.
- WordPress: `WP_UnitTestCase`; reset hooks/options/globals per test.

## Safeguards

- No merging with failing tests. Mark deferred tests with `@todo`/`skip` + ticket link.
- Fast feedback: parallelize/split slow suites; quarantine flaky tests.
- Refactoring without new behavior: keep green, improve existing coverage.
- Fix bugs surfaced by tests; don't lock in poor behavior.
- Coverage: ~80% overall, ~100% on new/changed code, 100% on security-critical paths. Meaningful assertions over coverage numbers.
