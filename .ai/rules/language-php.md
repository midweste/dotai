# Php Coding Rules

## PHP Development Rules

## General PHP Standards

- Follow PSR-12 coding style
- Follow SOLID principles
- Always use strict types: `declare(strict_types=1);`
- Use type hints for all method parameters and return types
- Use `?` for nullable types
- Use constructor property promotion where applicable
- Group use statements by type (classes, functions, constants)
- Instead of deep nesting conditionals, return early
- Prefer pure functions and immutable value objects; avoid shared mutable state.
- Default to `readonly` properties (PHP 8.2+) and `enum`/`BackedEnum` for closed sets instead of string constants.
- Use `match` over long `switch`/`if` ladders; keep guard clauses for early exits.
- Throw domain-specific exceptions instead of returning `null`/`false`; never silence exceptions.
- Favor dependency injection over service locators/singletons; keep constructors lean and explicit.
- Require strict scalar comparisons (`===`, `!==`) and avoid loose truthiness checks.
- Normalize time handling with `DateTimeImmutable` and injected clocks; avoid `time()`/`date()` in domain logic.
- Keep collections type-safe via array shape docs or static analysis annotations; avoid mixed arrays of dissimilar types.
- Enforce static analysis (PHPStan/Psalm) at high level; allow ignores only with documented rationale.
- Prefer native attributes over docblock annotations when available (e.g., ORM/serializer metadata).
- Document public APIs with concise PHPDoc only when types aren’t obvious; avoid redundant comments.
- Ban implicit output in libraries (no `echo`/`var_dump`); use structured logging instead.
- Prefer small, pure helpers over traits; if traits are used, keep them stateless.

## Code Organization

- Use namespaces following PSR-4
- One class per file
- Class names in `StudlyCaps`
- Method names in `camelCase`
- Property names in `camelCase`
- Constants in `UPPER_CASE`
- Add PHPDoc only when the intent, types, or edge cases are not obvious from signatures and names; avoid redundant docblocks on self-explanatory code.
- Keep methods small and focused (single responsibility)
- Use return type declarations
- Keep classes cohesive: group behaviors by bounded context; avoid “god” classes that mix admin UI, domain logic, and persistence.
- Place code where it belongs: controllers/admin screens handle I/O and orchestration; domain/services handle business rules; repositories/persistence adapters handle storage; utilities stay framework-agnostic.
- Prefer interfaces for cross-layer contracts; keep implementations in feature-specific namespaces (e.g., `Queue\Admin`, `Queue\Domain`, `Queue\Infrastructure`).
- Do not park feature logic in UI classes (e.g., queue operations stay in queue services, not `AdminInterface`); move misplaced methods before adding new ones.
- Co-locate tests and fixtures with their feature/module when possible for clarity.

## PHP Namespacing Rule

Never use fully-qualified namespaces (FQCN) in the middle of PHP code. Always use `use` statements at the top of the file and reference the short class name or an alias.

### Bad

```php
$logger = rr()->make(\Illuminate\Log\Logger::class);
```

### Good

```php
use Illuminate\Log\Logger;
...
$logger = rr()->make(Logger::class);
```

### Exceptions

- Inside `use` statements themselves.
- When there is a name collision that cannot be resolved with an alias (rare).
- Inside strings and comments (though preferred to use the short name even there if possible).
