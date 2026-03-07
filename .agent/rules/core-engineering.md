# Engineering Best Practices

Complement workflow rules. Apply to all code changes.

## Core Principles

- **Simple, elegant solutions**: prefer the simplest, most elegant code that solves the problem. Readable beats clever; straightforward beats compact. For non-trivial changes, pause and ask "is there a simpler structure?" If a fix feels hacky, reassess — there's almost always a cleaner path.
- **Root-cause discipline**: never patch symptoms. Trace every fix to its root cause. If a fix feels like a workaround, it probably is — dig deeper before committing.

## API / Interface Discipline

- Stable interfaces at boundaries (functions, modules, components). Optional params over duplicated paths. Consistent error semantics.
- When a method returns a collection that can be full or subset (filtered, paginated), use explicit naming (`getAllX()` vs `getFilteredX()`). Never leave the default ambiguous. When adding a filter to a data source, audit all consumers to verify they use the correct variant.
- **Match file conventions**: before naming a new method, function, or variable, scan the file for the dominant convention (snake_case, camelCase, PascalCase). Match it exactly.
- **Preserve comparison semantics**: when refactoring conditional logic, never change the type of comparison (partial → exact, case-sensitive → insensitive, allowlist → denylist) without calling out the behavioral difference and asking whether the change is intentional.

## Testing Strategy

→ See `core-testing.md` for full testing rules.

## Type Safety

- No suppressions (`any`, ignores) without project permission. Validate at boundaries, not scattered checks.

## Dependencies

- No new deps unless existing stack can't solve it cleanly. Prefer stdlib/existing utilities.

## Configuration

- When adding env vars, scan the config file for an existing section header that matches. Place the new var under that section, grouped with related vars. Never create a duplicate section header.
- When a value is already defined in config (database connections, queue names, cache stores), derive it dynamically. Never duplicate infrastructure definitions as hardcoded constants.
- Before overriding framework config defaults, read the upstream vendor/source default first. Only override values that genuinely differ from upstream.
- When customizing shared config, merge only the keys you own — don't replace the entire namespace. Keep a minimal config with just your additions.

## CLI Commands

- When creating a new CLI command, register it in the appropriate framework registry (service provider, plugin bootstrap, etc.) in the same edit batch. Don't leave commands unregistered.

## Security & Privacy

→ See `core-quality-assurance.md` § Security & Privacy for full rules.

## Performance

- No premature optimization. Fix N+1s, unbounded loops, repeated heavy computation. Measure when in doubt.

## Accessibility (UI Changes)

- Keyboard nav, focus management, readable contrast, meaningful empty/error states.

## Git Hygiene

- Atomic commits; no "misc fixes" bundles. Don't mix formatting with behavioral changes. Generated files committed only if project expects it.

## Definition of Done

Behavior matches criteria · tests/lint/build pass · rollback strategy for risky changes · code follows conventions · verification story exists.

## Templates

**Plan**: Goal → locate patterns → design → implement → test → verify → summarize → lessons.

**Bugfix**: Repro steps → expected vs actual → root cause → fix → regression coverage → verification → risk/rollback.
